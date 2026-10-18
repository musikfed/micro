param([string]$Root="F:\asmicro_PC")
$ErrorActionPreference="Continue"
$backend="http://127.0.0.1:8000"
$llm="http://192.168.0.100:8780"
$monitor="http://192.168.0.100:8765/stats"

function Check($name,[scriptblock]$fn) {
  try {
    $v=& $fn
    Write-Host "[PASS] $name" -ForegroundColor Green
    if($null -ne $v){$v | Format-List *}
    return $true
  } catch {
    Write-Host "[FAIL] $name :: $($_.Exception.Message)" -ForegroundColor Red
    return $false
  }
}

Write-Host "asmicro test_load diagnostics"
Write-Host "Root=$Root"

Check "backend /api/status" { Invoke-RestMethod "$backend/api/status" -TimeoutSec 8 } | Out-Null
Check "LLM proxy /health" { Invoke-RestMethod "$llm/health" -TimeoutSec 8 } | Out-Null
Check "Python httpx direct VPN (proxy bypass)" {
  Push-Location $Root
  try { uv run --python 3.12 python -c "import httpx; r=httpx.get('http://192.168.0.100:8780/api/tags',timeout=8,trust_env=False); print(r.status_code); print(r.text[:300])" }
  finally { Pop-Location }
} | Out-Null
Check "X79 monitor" { Invoke-RestMethod $monitor -TimeoutSec 5 } | Out-Null
Check "ESP32 beep command" { Invoke-RestMethod -Method Post "$backend/api/wake-sound/test" -TimeoutSec 8 } | Out-Null

$body = @{text="Диагностика Микро. Динамик и синтез речи работают."} | ConvertTo-Json
Check "Silero -> ESP32" {
  Invoke-RestMethod -Method Post -Uri "$backend/api/speak" -ContentType "application/json; charset=utf-8" -Body ([Text.Encoding]::UTF8.GetBytes($body)) -TimeoutSec 45
} | Out-Null

Write-Host ""
Write-Host "Voice checks:"
Write-Host "  1) say: Микро, скажи привет"
Write-Host "  2) Voice Log must show a non-empty ASR transcript"
Write-Host "  3) if transcript contains 'микро' but TRIGGER MISS -> wake matcher/aliases"
Write-Host "  4) if chat works but voice has no answer -> inspect wake gate, not Ollama"
