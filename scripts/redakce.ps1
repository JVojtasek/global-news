# =====================================================================
#  RANNI SMENA REDAKCE
#  Spousti se sama kazdy den v 7:00 pres Planovac uloh Windows.
#  Rucne se da spustit taky: pravym tlacitkem -> Run with PowerShell
# =====================================================================
$ErrorActionPreference = 'Continue'
$repo = Join-Path $env:USERPROFILE 'global-news'
$logDir = Join-Path $repo 'logs'
New-Item -ItemType Directory -Path $logDir -Force | Out-Null
$stamp = Get-Date -Format 'yyyy-MM-dd_HH-mm'
$log = Join-Path $logDir "redakce_$stamp.log"

function Zapis($t) {
  $line = "[{0}] {1}" -f (Get-Date -Format 'HH:mm:ss'), $t
  Write-Host $line
  Add-Content -Path $log -Value $line -Encoding UTF8
}

Zapis "=== RANNI SMENA REDAKCE ==="
Set-Location $repo

# 1) stahnout aktualni zadani
Zapis "Stahuji dnesni zadani z GitHubu..."
git fetch -q origin 2>&1 | Out-Null
git reset --hard -q origin/main 2>&1 | Out-Null
$brief = Join-Path $repo 'data\brief.md'
if (-not (Test-Path $brief)) { Zapis "CHYBA: zadani neexistuje. Koncim."; exit 1 }
Zapis ("Zadani ze dne: " + (Get-Item $brief).LastWriteTime.ToString('dd.MM. HH:mm'))

# 2) nechat Claude Code napsat clanky
Zapis "Predavam praci Claude Code (muze trvat 10-20 minut)..."
$instrukce = Get-Content (Join-Path $repo 'scripts\REDAKCE.md') -Raw -Encoding UTF8
$vystup = $instrukce | claude -p --permission-mode acceptEdits --output-format text 2>&1
$vystup | Out-File -FilePath (Join-Path $logDir "claude_$stamp.log") -Encoding UTF8
Zapis "Claude Code dokoncil praci."

# 3) kolik toho napsal
$nove = @(Get-ChildItem (Join-Path $repo 'content\inbox') -Filter *.md -ErrorAction SilentlyContinue)
Zapis ("Clanku v inboxu: " + $nove.Count)
if ($nove.Count -eq 0) {
  Zapis "Nic se nenapsalo. Koncim bez odeslani."
  Zapis "Podrobnosti v: $logDir\claude_$stamp.log"
  exit 0
}
foreach ($f in $nove) { Zapis ("  - " + $f.Name) }

# 4) odeslat na GitHub
Zapis "Odesilam na GitHub..."
git add content/inbox content/cs 2>&1 | Out-Null
git -c user.email="redakce@users.noreply.github.com" -c user.name="redakce" commit -qm "[bot] redakce dodala $($nove.Count) clanku" 2>&1 | Out-Null
git pull --rebase --autostash -q origin main 2>&1 | Out-Null
$push = git push origin main 2>&1
if ($LASTEXITCODE -eq 0) {
  Zapis "HOTOVO. Clanky jsou na GitHubu, web se prestavi behem par minut."
} else {
  Zapis "CHYBA pri odesilani:"
  $push | ForEach-Object { Zapis ("   " + $_) }
}
Zapis "=== KONEC SMENY ==="
