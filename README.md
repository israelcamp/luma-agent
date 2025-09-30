# Luma Agent

## Install

UV: `curl -LsSf https://astral.sh/uv/install.sh | sh`

Ollama: `curl -fsSL https://ollama.com/install.sh | sh`

1. `uv sync`
1. `source .venv/bin/activate`
1. `ollama pull llama3.2:3b-instruct-q5_K_M`
1. `fastapi dev api.py`
1. `streamlit run streamlit.py`
