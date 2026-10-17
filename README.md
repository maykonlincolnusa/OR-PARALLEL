# OR PARALLEL

**A local artificial-society simulator powered by Llama and LM Studio.**

OR PARALLEL is an experimental interactive world where autonomous inhabitants form memories, build relationships, react to unexpected events, and evolve across branching timelines. The simulation runs locally on Apple Silicon through the OpenAI-compatible API exposed by Bionic/LM Studio.

## Why this project exists

Most LLM demos stop at a chat interface. OR PARALLEL treats the language model as a shared cognitive engine for an evolving world. Every turn produces structured decisions that change the city, its inhabitants, and its social indicators.

## Current prototype

- Eight inhabitants with distinct roles, traits, colors, and memories
- A visual 2D city with six interactive locations
- User-created events such as blackouts, rumors, and economic crises
- Social indicators for trust, economy, and tension
- A chronological event feed
- Local Llama inference with structured JSON responses
- Browser-only fallback mode for public demonstrations
- Responsive interface with no frontend framework required

## Architecture

```text
Browser UI
   │
   ▼
Python local server
   │
   ▼
Bionic / LM Studio API
   │
   ▼
Llama 3.2 3B Instruct
   │
   ▼
Structured event → memory → metrics → timeline
```

The application uses one shared local model. Each inhabitant receives a different identity and context instead of loading a separate model into memory.

## Run locally

Requirements:

- Python 3.9 or newer
- Bionic or LM Studio
- A locally downloaded instruction model such as Llama 3.2 3B Instruct

1. Start the local model API in Bionic/LM Studio.
2. Confirm its OpenAI-compatible URL. This project defaults to `http://127.0.0.1:1235/v1`.
3. Start the application:

```bash
python3 server.py
```

4. Open `http://127.0.0.1:8765`.

If the model API is unavailable, the interface automatically switches to demonstration mode.

## Configuration

```bash
LMSTUDIO_BASE_URL=http://127.0.0.1:1235/v1 python3 server.py
```

Optional environment variables:

- `LMSTUDIO_BASE_URL`: local OpenAI-compatible API URL
- `LMSTUDIO_MODEL`: exact model identifier
- `PORT`: OR PARALLEL web-server port

## Roadmap

- Persistent episodic memories with local embeddings
- Relationship graphs and reputation changes
- True timeline snapshots and side-by-side universe comparison
- Agent goals, needs, routines, and resource constraints
- Replayable simulations and evaluation reports
- Improved prompting and automated behavioral tests

## Important note

OR PARALLEL is a creative simulation and engineering experiment. It does not claim to predict real human or social behavior.

## Repository

[github.com/maykonlincolnusa/OR-PARALLEL](https://github.com/maykonlincolnusa/OR-PARALLEL)
