#!/usr/bin/env python3
"""OR PARALLEL — servidor local e ponte para o LM Studio/Bionic."""

from __future__ import annotations

import json
import mimetypes
import os
import random
import urllib.error
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).parent
WEB = ROOT / "web"
LM_BASE = os.getenv("LMSTUDIO_BASE_URL", "http://127.0.0.1:1235/v1")
PORT = int(os.getenv("PORT", "8765"))


def lm_request(path: str, payload: dict | None = None, timeout: int = 90) -> dict:
    data = None if payload is None else json.dumps(payload).encode()
    request = urllib.request.Request(
        f"{LM_BASE}{path}", data=data, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read())


def available_model() -> str:
    configured = os.getenv("LMSTUDIO_MODEL")
    if configured:
        return configured
    models = [
        item for item in lm_request("/models", timeout=3).get("data", [])
        if "embed" not in item.get("id", "").lower()
    ]
    if not models:
        raise RuntimeError("Nenhum modelo carregado no Bionic/LM Studio")
    return models[0]["id"]


def simulate_with_llama(state: dict, event: str) -> dict:
    model = available_model()
    allowed_agents = [item.get("name", "") for item in state.get("agents", []) if item.get("name")]
    allowed_locations = ["Praça", "Mercado", "Hospital", "Prefeitura", "Café", "Residências"]
    compact = {
        "day": state.get("day", 1),
        "period": state.get("period", "Manhã"),
        "metrics": state.get("metrics", {}),
        "agents": state.get("agents", []),
        "new_event": event,
    }
    schema = {
        "name": "city_turn",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "headline": {"type": "string"},
                "summary": {"type": "string"},
                "actor": {"type": "string"},
                "location": {"type": "string"},
                "dialogue": {"type": "string"},
                "memory": {"type": "string"},
                "metric_delta": {
                    "type": "object",
                    "properties": {
                        "trust": {"type": "integer"},
                        "economy": {"type": "integer"},
                        "tension": {"type": "integer"},
                    },
                    "required": ["trust", "economy", "tension"],
                    "additionalProperties": False,
                },
            },
            "required": ["headline", "summary", "actor", "location", "dialogue", "memory", "metric_delta"],
            "additionalProperties": False,
        },
    }
    payload = {
        "model": model,
        "temperature": 0.25,
        "max_tokens": 500,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Você é o motor de uma pequena cidade artificial. Produza um acontecimento "
                    "plausível, coerente com o estado informado e sem afirmar que a simulação prevê "
                    "comportamento humano real. Responda em português brasileiro. Os deltas devem "
                    "estar entre -8 e 8. Escolha somente atores fornecidos e um destes locais: "
                    "Praça, Mercado, Hospital, Prefeitura, Café ou Residências. Trate falta de "
                    "energia como apagão, nunca como derramamento. Não use markdown."
                ),
            },
            {"role": "user", "content": json.dumps(compact, ensure_ascii=False)},
        ],
        "response_format": {"type": "json_schema", "json_schema": schema},
    }
    response = lm_request("/chat/completions", payload)
    result = json.loads(response["choices"][0]["message"]["content"])
    if result.get("actor") not in allowed_agents:
        result["actor"] = allowed_agents[0] if allowed_agents else "Ana"
    if result.get("location") not in allowed_locations:
        result["location"] = "Praça"
    for field in ("headline", "summary", "dialogue", "memory"):
        value = result.get(field)
        if not isinstance(value, str) or len(value.strip()) < 8:
            result[field] = {
                "headline": "A cidade reage ao novo acontecimento",
                "summary": f"Os habitantes começaram a reagir a: {event}.",
                "dialogue": "Precisamos entender a situação antes de decidir.",
                "memory": f"{result['actor']} participou da resposta ao acontecimento.",
            }[field]
    deltas = result.get("metric_delta", {})
    result["metric_delta"] = {
        key: max(-8, min(8, int(deltas.get(key, 0))))
        for key in ("trust", "economy", "tension")
    }
    result["source"] = f"Llama local · {model}"
    return result


def fallback_turn(state: dict, event: str) -> dict:
    agents = state.get("agents") or [{"name": "Ana", "role": "Enfermeira"}]
    actor = random.choice(agents)
    reactions = [
        ("Uma conversa muda o clima da praça", "propôs que os moradores compartilhassem recursos"),
        ("Uma decisão inesperada divide opiniões", "pediu uma reunião aberta antes de agir"),
        ("Uma pequena aliança começa a surgir", "ofereceu ajuda em troca de colaboração futura"),
    ]
    headline, action = random.choice(reactions)
    return {
        "headline": headline,
        "summary": f"Após ‘{event or 'um dia aparentemente comum'}’, {actor['name']} {action}.",
        "actor": actor["name"],
        "location": random.choice(["Praça", "Mercado", "Hospital", "Prefeitura"]),
        "dialogue": "Precisamos decidir juntos antes que a situação piore.",
        "memory": f"{actor['name']} tomou iniciativa durante {event or 'um período de incerteza'}.",
        "metric_delta": {"trust": random.randint(-2, 5), "economy": random.randint(-3, 3), "tension": random.randint(-2, 5)},
        "source": "Motor demonstrativo · conecte o Llama para decisões generativas",
    }


class Handler(SimpleHTTPRequestHandler):
    def translate_path(self, path: str) -> str:
        clean = path.split("?", 1)[0].split("#", 1)[0]
        if clean == "/":
            clean = "/index.html"
        return str(WEB / clean.lstrip("/"))

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def send_json(self, data: dict, status: int = 200) -> None:
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path == "/api/status":
            try:
                model = available_model()
                self.send_json({"connected": True, "model": model})
            except Exception as exc:
                self.send_json({"connected": False, "message": str(exc)})
            return
        super().do_GET()

    def do_POST(self) -> None:
        if self.path != "/api/step":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", 0))
        payload = json.loads(self.rfile.read(length) or b"{}")
        try:
            result = simulate_with_llama(payload.get("state", {}), payload.get("event", ""))
        except Exception:
            result = fallback_turn(payload.get("state", {}), payload.get("event", ""))
        self.send_json(result)


if __name__ == "__main__":
    mimetypes.add_type("text/javascript", ".js")
    print(f"OR PARALLEL disponível em http://127.0.0.1:{PORT}")
    print(f"Procurando o LM Studio/Bionic em {LM_BASE}")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()

