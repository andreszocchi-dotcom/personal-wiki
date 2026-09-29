"""The three interaction modes. Each one differs in instructions, context and tools:

  search  retrieval tool only. No model call, no generated text.
  ask     RAG: retrieve -> research rules + passages + question -> Gemma ->
          citation check. No chat history, no persona. Standalone every time.
  chat    persona + recent conversation. A router decides per turn whether the
          message needs the notes; retrieval is a tool chat can use, not a rule.
"""

import re

from . import config, evidence, llm, retrieval

CITE = re.compile(r"\[S(\d+)\]")
INSUFFICIENT = "INSUFFICIENT EVIDENCE"


# ---------------------------------------------------------------- search

def search(query, k=None):
    passages = retrieval.search(query, k=k)
    evidence.log_run("search", query=query, passages=passages)
    return passages


# ---------------------------------------------------------------- citations

def check_citations(answer, passages):
    """Mechanical checks the harness can do; support must still be read by a human.

    - every [S#] must refer to a passage that was actually retrieved
    - a non-refusal answer must cite at least one passage
    """
    cited = sorted({int(n) for n in CITE.findall(answer)})
    invalid = [n for n in cited if not 1 <= n <= len(passages)]
    refused = INSUFFICIENT in answer.upper()
    problems = []
    if invalid:
        problems.append(f"cites passages that were not retrieved: {', '.join(f'S{n}' for n in invalid)}")
    if not refused and not cited:
        problems.append("answer makes claims without citing any passage")
    return {
        "cited": [f"S{n}" for n in cited if n not in invalid],
        "cited_sources": [f"{passages[n - 1]['path']} | {passages[n - 1]['location']}"
                          for n in cited if n not in invalid],
        "invalid": [f"S{n}" for n in invalid],
        "insufficient_evidence": refused,
        "problems": problems,
        "ok": not problems,
    }


# ---------------------------------------------------------------- ask

def ask(question, stream_to=None, k=None):
    """Standalone grounded answer. Deliberately takes no history argument."""
    passages = retrieval.search(question, k=k)
    rules = config.RESEARCH_RULES.read_text(encoding="utf-8")

    if not passages:
        # Nothing in the index shares a keyword with the question: no evidence
        # to give the model, so answer the refusal without a model call.
        answer = f"{INSUFFICIENT}: no passage in the indexed sources matches this question."
        if stream_to:
            stream_to(answer)
        metrics = {"model_called": False}
    else:
        messages = [
            {"role": "system", "content": rules},
            {"role": "user", "content":
                f"Passages retrieved from the wiki's original sources:\n\n"
                f"{retrieval.format_passages(passages)}\n\n"
                f"Question: {question}"},
        ]
        answer, metrics = llm.chat(messages, temperature=0.1, stream_to=stream_to)
        metrics["model_called"] = True

    check = check_citations(answer, passages)
    record = evidence.log_run("ask", question=question, passages=passages,
                              answer=answer, citations=check, metrics=metrics)
    return {"answer": answer, "passages": passages, "citations": check,
            "metrics": metrics, "run_id": record["run_id"]}


# ---------------------------------------------------------------- chat

ROUTE_SCHEMA = {
    "type": "object",
    "properties": {
        "retrieve": {"type": "boolean"},
        "query": {"type": "string"},
        "reason": {"type": "string"},
    },
    "required": ["retrieve", "query", "reason"],
}


class ChatSession:
    """Holds conversation context for one `wiki chat` session (memory only)."""

    def __init__(self):
        self.history = []          # [{"role": "user"|"assistant", "content": str}]
        self.last_passages = []

    def recent(self):
        return self.history[-config.CHAT_HISTORY_MESSAGES:]

    def route(self, message, force=None):
        """Decide whether this turn needs the notes. Returns (retrieve, query, reason)."""
        if force is not None:
            return force, message, "forced by user command"
        convo = "\n".join(f"{m['role']}: {m['content'][:300]}" for m in self.recent()[-4:])
        decision, _ = llm.chat_json([
            {"role": "system", "content": config.ROUTER_RULES.read_text(encoding="utf-8")},
            {"role": "user", "content":
                f"Recent conversation:\n{convo or '(none)'}\n\nNew message: {message}"},
        ], ROUTE_SCHEMA)
        return bool(decision["retrieve"]), decision.get("query") or message, decision.get("reason", "")

    def turn(self, message, stream_to=None, force_retrieve=None):
        retrieve, query, reason = self.route(message, force_retrieve)
        carried = False
        if retrieve:
            passages = retrieval.search(query)
        elif self.last_passages:
            # A follow-up like "make that shorter" rewrites a reply that cited
            # notes. Re-attach those passages for this one turn so its
            # citations still point at text the harness can show and check.
            passages, carried = self.last_passages, True
        else:
            passages = []
        self.last_passages = [] if carried else passages

        system = config.PERSONA.read_text(encoding="utf-8")
        context = self.recent()
        messages = [{"role": "system", "content": system}] + context
        if passages:
            # Notes are attached per turn and never stored in history, so
            # later turns can't mistake them for conversation.
            intro = ("Notes retrieved for the previous message, re-attached for this follow-up "
                     if carried else "Notes retrieved for this message ")
            messages.append({"role": "system", "content":
                intro + "(cite as [S#] when you use them):\n\n" + retrieval.format_passages(passages)})
        elif retrieve:
            messages.append({"role": "system", "content":
                "A notes search was run for this message and found nothing relevant. "
                "Say so if the user asked about their notes; do not invent personal facts."})
        messages.append({"role": "user", "content": message})

        reply, metrics = llm.chat(messages, temperature=0.7, stream_to=stream_to)
        self.history += [{"role": "user", "content": message},
                         {"role": "assistant", "content": reply}]
        check = check_citations(reply, passages) if passages else None
        evidence.log_run("chat", message=message, retrieval={"used": retrieve, "query": query,
                         "reason": reason, "carried_from_previous_turn": carried},
                         passages=passages, answer=reply,
                         citations=check, metrics=metrics, history_messages_sent=len(context))
        return {"reply": reply, "retrieved": retrieve, "carried": carried, "reason": reason, "query": query,
                "passages": passages, "citations": check, "metrics": metrics}
