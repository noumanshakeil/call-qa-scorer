# Dev server for call-qa-scorer
$env:LLM_MODE = "mock"
uvicorn backend.main:app --reload --port 8000
