# Offline demonstration. Disconnect Wi-Fi/Ethernet FIRST, then run from the repo root:
#
#   powershell -ExecutionPolicy Bypass -File scripts\offline_demo.ps1
#
# Everything printed is also saved to evidence\offline\transcript.txt.
# Afterwards, run `python wiki.py chat` by hand for the interactive part
# (see README "Offline demonstration").

$ErrorActionPreference = "Continue"
$env:PYTHONIOENCODING = "utf-8"
Set-Location (Split-Path $PSScriptRoot -Parent)
New-Item -ItemType Directory -Force evidence\offline | Out-Null
Start-Transcript -Path evidence\offline\transcript.txt -Force | Out-Null

function Step($text) { Write-Host "`n==================== $text ====================" -ForegroundColor Cyan }

Step "Connectivity check (must fail while offline)"
try { Test-NetConnection 1.1.1.1 -Port 443 -InformationLevel Quiet -WarningAction SilentlyContinue } catch { $false }
Get-NetAdapter | Where-Object Status -eq "Up" | Select-Object Name, Status | Format-Table -AutoSize
Get-Date

Step "Restart Ollama (local runtime) so the CLI starts from a clean state"
Get-Process "ollama app","ollama","llama-server" -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep 2
Start-Process "$env:LOCALAPPDATA\Programs\Ollama\ollama app.exe"
Start-Sleep 8
ollama list | Out-Host

Step "wiki status"
python wiki.py status | Out-Host

Step "wiki --help"
python wiki.py --help | Out-Host

Step "wiki ingest (re-ingest one local source; must not create duplicate notes)"
$before = (Get-ChildItem vault\wiki -Recurse -Filter *.md).Count
Measure-Command { python wiki.py ingest "vault\raw\Source\LinkedIn Profile.md" --force | Out-Host } | Select-Object TotalSeconds
$after = (Get-ChildItem vault\wiki -Recurse -Filter *.md).Count
"notes before: $before  after: $after"
python scripts\check_links.py | Out-Host

Step "wiki search (no model)"
python wiki.py search "Workday data migration" -k 3 | Out-Host

Step "wiki ask: four test questions (writes evidence\cards\test-1..4.md)"
python wiki.py eval tests\questions.json --out evidence\cards | Out-Host

Step "Memory while loaded"
ollama ps | Out-Host
Get-Process llama-server | Select-Object Id, @{n='WorkingSetGB';e={[math]::Round($_.WorkingSet64/1GB,2)}}
"Free RAM: {0:N1} GB" -f ((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB)

Step "Chat / search / ask mode checks (writes evidence\checks\mode-checks.md)"
python scripts\mode_checks.py | Out-Host

Step "Done"
Get-Date
Stop-Transcript | Out-Null
