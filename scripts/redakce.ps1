# =====================================================================
#  RANNI SMENA REDAKCE  (My Paper)
#
#  Spousti se sama nekolikrat denne pres Planovac uloh Windows
#  (uloha "The Deeper Story - ranni smena"). Rucne taky:
#  pravym tlacitkem -> Run with PowerShell
#
#  Co se zmenilo 14. 8. 2026:
#   * pise se do SLOTU podle data/edition-plan.json (viz scripts/REDAKCE.md)
#   * odesila se VSECHNO, na co smena sahla (drive jen content/inbox a
#     content/cs — zmeny v content/en, treba doplnene bloky impact:,
#     se kazde rano tise zahazovaly)
#   * push se opakuje, dokud neprojde; nedokoncena prace z minuleho behu
#     se odesle na zacatku toho dalsiho
#   * kdyz uz zadny slot nechybi, smena skonci rychle a nic nepise
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

# Odesle vse, co je v repozitari rozdelane. Vraci $true, kdyz je
# main shodny s originem. Opakuje, protoze mezi commitem a pushem
# tam bezne zapise nekdo jiny (boti z GitHub Actions).
function Odesli($zprava) {
  Set-Location $repo
  git add -A content data/daily-agenda 2>&1 | Out-Null
  $staged = git diff --staged --name-only 2>$null
  if ($staged) {
    $pocet = ($staged | Measure-Object).Count
    Zapis ("Commituji zmen: " + $pocet)
    git -c user.email="redakce@users.noreply.github.com" -c user.name="redakce" commit -qm $zprava 2>&1 | Out-Null
  }
  $ahead = git rev-list --count origin/main..HEAD 2>$null
  if (-not $ahead -or $ahead -eq '0') { Zapis "Neni co odesilat."; return $true }

  for ($i = 1; $i -le 3; $i++) {
    git pull --rebase --autostash -q origin main 2>&1 | Out-Null
    git push origin main 2>&1 | Out-Null
    git fetch -q origin 2>&1 | Out-Null
    $zbyva = git rev-list --count origin/main..HEAD 2>$null
    if ($zbyva -eq '0') { Zapis ("Odeslano na GitHub (pokus " + $i + ")."); return $true }
    Zapis ("Push neprosel, zkousim znovu (pokus " + $i + " ze 3)...")
    Start-Sleep -Seconds 8
  }
  Zapis "CHYBA: push se nepodaril ani na treti pokus. Prace zustava v repozitari a odesle ji dalsi beh."
  return $false
}

# ZAMEK — dve smeny nikdy nesmi psat do stejneho inboxu naraz.
# 14. 8. 2026 se to stalo (rucni spusteni + naplanovana uloha ve 12:00)
# a kazdy slot mel dve verze. IgnoreNew v Planovaci uloh hlida jen
# instance spustene planovacem, rucni spusteni ne. Tenhle zamek hlida obe.
$lockFile = Join-Path $logDir ".smena.lock"
if (Test-Path $lockFile) {
  $stary = Get-Content $lockFile -Raw -ErrorAction SilentlyContinue
  $starePid = ($stary -split "\|")[0]
  $zije = Get-Process -Id $starePid -ErrorAction SilentlyContinue
  $vek = (Get-Date) - (Get-Item $lockFile).LastWriteTime
  if ($zije -and $vek.TotalMinutes -lt 90) {
    Zapis ("Jina smena uz bezi (PID " + $starePid + ", " + [int]$vek.TotalMinutes + " min). Koncim.")
    exit 0
  }
  Zapis "Naslo se osirele zamknuti, prebiram praci."
}
"{0}|{1}" -f $PID, (Get-Date -Format o) | Set-Content $lockFile -Encoding UTF8

Zapis "=== SMENA REDAKCE ==="
Set-Location $repo

# 0) nejdriv dorovnat, co zbylo z minule (treba kdyz predtim spadl push
#    nebo byl pocitac vypnuty uprostred behu)
git fetch -q origin 2>&1 | Out-Null
Odesli "[bot] redakce: dorovnani z minuleho behu" | Out-Null

# 1) stahnout aktualni stav a zadani
Zapis "Stahuji aktualni stav z GitHubu..."
git pull --rebase --autostash -q origin main 2>&1 | Out-Null

$brief = Join-Path $repo 'data\brief.md'
if (-not (Test-Path $brief)) { Zapis "CHYBA: zadani data\brief.md neexistuje. Koncim."; exit 1 }
Zapis ("Zadani ze dne: " + (Get-Item $brief).LastWriteTime.ToString('dd.MM. HH:mm'))

$plan = Join-Path $repo 'data\edition-plan.json'
if (Test-Path $plan) {
  try {
    $p = Get-Content $plan -Raw -Encoding UTF8 | ConvertFrom-Json
    Zapis ("Plan vydani na " + $p.date + ": " + $p.public_count + " verejnych slotu")
  } catch { Zapis "Plan vydani se nepodarilo precist, jedu dal." }
}

# 2) nechat Claude Code napsat chybejici sloty
if (-not (Get-Command claude -ErrorAction SilentlyContinue)) {
  Zapis "CHYBA: prikaz 'claude' neni v PATH. Bez nej smena psat nemuze. Koncim."
  exit 1
}
Zapis "Predavam praci Claude Code (muze trvat 10-20 minut)..."
$pred = @(Get-ChildItem (Join-Path $repo 'content\inbox') -Filter *.md -ErrorAction SilentlyContinue).Count
$instrukce = Get-Content (Join-Path $repo 'scripts\REDAKCE.md') -Raw -Encoding UTF8
$vystup = $instrukce | claude -p --permission-mode acceptEdits --output-format text 2>&1
$vystup | Out-File -FilePath (Join-Path $logDir "claude_$stamp.log") -Encoding UTF8
Zapis "Claude Code dokoncil praci."

# 3) co pribylo
$nove = @(Get-ChildItem (Join-Path $repo 'content\inbox') -Filter *.md -ErrorAction SilentlyContinue)
Zapis ("Clanku v inboxu: " + $nove.Count + " (pred smenou " + $pred + ")")
foreach ($f in $nove) { Zapis ("  - " + $f.Name) }

# 4) odeslat VSECHNO, na co smena sahla — i kdyz v inboxu nic nepribylo.
#    Smena bezne upravuje i content/en (bloky impact:) a content/cs (preklady)
#    a driv se tyhle zmeny nikdy neodeslaly.
$pribylo = $nove.Count - $pred
$zprava = if ($pribylo -gt 0) { "[bot] redakce dodala $pribylo clanku" } else { "[bot] redakce: uprava clanku" }
if (Odesli $zprava) {
  Zapis "HOTOVO. Web se prestavi behem par minut."
} else {
  Zapis "Smena skoncila, ale prace ceka na odeslani."
}
Zapis ("Podrobnosti v: " + $logDir + "\claude_$stamp.log")
Remove-Item $lockFile -Force -ErrorAction SilentlyContinue
Zapis "=== KONEC SMENY ==="
