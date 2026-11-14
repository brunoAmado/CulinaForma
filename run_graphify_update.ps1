# High-Core Windows Graphify Guard (<= 61 Workers) for InsightBake
$ErrorActionPreference = "Stop"
$env:GRAPHIFY_MAX_WORKERS = [math]::Min(61, [math]::Max(2, [int]($env:NUMBER_OF_PROCESSORS * 0.75)))
Write-Host "[Graphify Guard] GRAPHIFY_MAX_WORKERS capped at $($env:GRAPHIFY_MAX_WORKERS)"

$graphifyPy = $null
if (Test-Path "graphify-out\.graphify_python") {
    $cand = (Get-Content "graphify-out\.graphify_python" -Raw).Trim()
    if ($cand -and (Test-Path $cand)) { $graphifyPy = $cand }
}
if (-not $graphifyPy -and (Get-Command uv -ErrorAction SilentlyContinue)) {
    $uvDir = (uv tool dir 2>$null).Trim()
    if ($uvDir) {
        $cand = Join-Path $uvDir "graphifyy\Scripts\python.exe"
        if (Test-Path $cand) { $graphifyPy = $cand }
    }
}
if (-not $graphifyPy) {
    $cand = "C:\Users\bruno\PycharmProjects\chronicle-rag\.venv\Scripts\python.exe"
    if (Test-Path $cand) { $graphifyPy = $cand }
}

New-Item -ItemType Directory -Force -Path "graphify-out" | Out-Null
& $graphifyPy -c @"
import json
from pathlib import Path
from graphify.detect import detect
from graphify.extract import extract, collect_files
from graphify.build import build_from_json
from graphify.cluster import cluster, score_all
from graphify.analyze import god_nodes, surprising_connections, suggest_questions
from graphify.report import generate
from graphify.export import to_json

root = Path('.').resolve()
det = detect(root)
Path('graphify-out/.graphify_detect.json').write_text(json.dumps(det, ensure_ascii=False), encoding='utf-8')
code_files = []
for f in det.get('files', {}).get('code', []):
    p = Path(f)
    code_files.extend(collect_files(p) if p.is_dir() else [p])
if code_files:
    ast_res = extract(code_files)
    Path('graphify-out/.graphify_extract.json').write_text(json.dumps(ast_res, indent=2, ensure_ascii=False), encoding='utf-8')
    G = build_from_json(ast_res)
    comms = cluster(G)
    cohesion = score_all(G, comms)
    gods = god_nodes(G)
    surprises = surprising_connections(G, comms)
    labels = {cid: 'Community ' + str(cid) for cid in comms}
    qs = suggest_questions(G, comms, labels)
    rep = generate(G, comms, cohesion, labels, gods, surprises, det, {'input': 0, 'output': 0}, '.', suggested_questions=qs)
    Path('graphify-out/GRAPH_REPORT.md').write_text(rep, encoding='utf-8')
    to_json(G, comms, 'graphify-out/graph.json')
    print(f'[Graphify] Built graphify-out/graph.json: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges')
"@
