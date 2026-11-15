$ErrorActionPreference = "Stop"
# RULE-19: Third-party graphify is retired at runtime. This canonical script updates SetMiddle's
# Sovereign AST, 4-Axis Topology & Semantic Gravity Graph (InsightCode + InsightGravity + InsightChanged).
$env:GRAPHIFY_MAX_WORKERS = [math]::Min(61, [math]::Max(2, [int]($env:NUMBER_OF_PROCESSORS * 0.75)))
$chronicleDir = Join-Path $HOME "PycharmProjects\chronicle-rag"
$pyBin = Join-Path $chronicleDir ".venv\Scripts\python.exe"
$syncScript = Join-Path $chronicleDir "sovereign_ast_graph_sync.py"
$targetWorkspace = if ($PSScriptRoot) { $PSScriptRoot } else { (Get-Location).Path }
& $pyBin $syncScript --workspace $targetWorkspace
