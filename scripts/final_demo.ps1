param(
  [switch]$Online
)

$ErrorActionPreference = "Stop"
$env:OFFLINE_MODE = if ($Online) { "0" } else { "1" }

Write-Host "OFFLINE_MODE=$env:OFFLINE_MODE"

Write-Host "Running demo pipeline..."
.\.venv\Scripts\python.exe run_demo.py --scenario ferrari

Write-Host "Starting API server..."
$proc = Start-Process -FilePath .\.venv\Scripts\python.exe -ArgumentList @("-m","uvicorn","main:app","--port","8000") -PassThru
try {
  Start-Sleep -Seconds 2
  $health = Invoke-RestMethod -Uri "http://localhost:8000/api/health" -Method Get
  $graph = Invoke-RestMethod -Uri "http://localhost:8000/api/graph" -Method Get
  $nodes = ($graph.nodes | Measure-Object).Count
  $links = ($graph.links | Measure-Object).Count
  Write-Host "Health: $($health.status)"
  Write-Host "Graph nodes: $nodes, links: $links"

  $feedPath = "logs/agent_feed.jsonl"
  if (Test-Path $feedPath) {
    $lines = (Get-Content $feedPath | Measure-Object).Count
    Write-Host "Agent feed lines: $lines"
  } else {
    Write-Host "Agent feed missing: $feedPath"
  }

  Write-Host "Open http://localhost:8000/static/index.html"
} finally {
  if ($proc -and -not $proc.HasExited) { $proc | Stop-Process }
}
