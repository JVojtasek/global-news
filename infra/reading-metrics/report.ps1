param([string]$Wrangler = "$env:LOCALAPPDATA\npm-cache\_npx\32026684e21afda6\node_modules\.bin\wrangler.cmd")
$ErrorActionPreference = 'Stop'
if (!(Test-Path -LiteralPath $Wrangler)) { throw 'Wrangler nebyl nalezen. Nainstalujte jej nebo zadejte parametr Wrangler.' }
$env:NODE_OPTIONS = '--use-system-ca'
$env:CLOUDFLARE_ACCOUNT_ID = '527c0911d8eef3c3834ea7a8db705eef'
$sql = (Get-Content -LiteralPath (Join-Path $PSScriptRoot 'report.sql') -Raw) -replace '(?m)^--.*$', '' -replace '\s+', ' '
$json = & $Wrangler d1 execute mypaper-reading-metrics --remote --command $sql --json
if ($LASTEXITCODE -ne 0) { throw 'Nepodařilo se načíst souhrny z Cloudflare.' }
$response = $json | ConvertFrom-Json
if (-not $response[0].success) { throw 'Cloudflare nevrátil úspěšný výsledek.' }
$rows = @($response[0].results)
$encode = { param($v) [System.Net.WebUtility]::HtmlEncode([string]$v) }
$body = foreach ($row in $rows) {
  $path = & $encode $row.path
  $clicks = if ($null -eq $row.clicks) { 'méně než 5' } else { [string]$row.clicks }
  $time = if ($null -eq $row.avg_visible_seconds) { 'méně než 5 měření' } else { "cca $($row.avg_visible_seconds) s" }
  "<tr><td><a href=`"https://mypaper.news$path`">$path</a></td><td>$clicks</td><td>$time</td></tr>"
}
$generated = [System.Net.WebUtility]::HtmlEncode((Get-Date).ToString('dd.MM.yyyy HH:mm'))
$empty = if ($rows.Count -eq 0) { '<p>Zatím nejsou dostupné dostatečné souhrnné počty.</p>' } else { '' }
$html = @"
<!doctype html><html lang="cs"><meta charset="utf-8"><title>My Paper – čtenost</title>
<style>body{font:16px system-ui;max-width:1000px;margin:3em auto;padding:0 1em;color:#192330}table{border-collapse:collapse;width:100%}td,th{border-bottom:1px solid #ddd;padding:.8em;text-align:left}small{color:#536071}</style>
<h1>My Paper – čtenost</h1><p>Posledních 30 dní · vytvořeno $generated</p>
<p>Jen předem prověřené články. Kliknutí nejsou počtem různých lidí; čas viditelné stránky není důkaz čtení. Údaje pod 5 událostí nezobrazujeme.</p>
$empty<table><thead><tr><th>Článek</th><th>Kliknutí</th><th>Průměrná viditelná doba</th></tr></thead><tbody>$($body -join "`n")</tbody></table>
<small>Souhrnný interní přehled; data mají zpoždění. Zdravotní témata se do měření nezařazují.</small></html>
"@
$destination = Join-Path $env:TEMP 'mypaper-reading-report.html'
[System.IO.File]::WriteAllText($destination, $html, [System.Text.UTF8Encoding]::new($false))
Write-Output $destination
