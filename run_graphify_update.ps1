$ErrorActionPreference = "Stop"
# RULE-19 Backward-Compatible Wrapper: Preserves <=61 worker env invariant (Gate 05) while delegating
# 100% of AST & 4-Axis Topology indexing to SetMiddle Sovereign InsightCode + InsightGravity + InsightChanged.
$env:GRAPHIFY_MAX_WORKERS = [math]::Min(61, [math]::Max(2, [int]($env:NUMBER_OF_PROCESSORS * 0.75)))
$chronicleDir = Join-Path $HOME "PycharmProjects\chronicle-rag"
$pyBin = Join-Path $chronicleDir ".venv\Scripts\python.exe"
$syncScript = Join-Path $chronicleDir "sovereign_ast_graph_sync.py"
$targetWorkspace = if ($PSScriptRoot) { $PSScriptRoot } else { (Get-Location).Path }
& $pyBin $syncScript --workspace $targetWorkspace
