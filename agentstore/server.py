"""HTTP API (stdlib only).

Management/chat (Authorization: Bearer $AGENTSTORE_API_KEY):
  GET    /agents                  list agents
  GET    /agents/{id}             get one
  PUT    /agents/{id}             create/replace (JSON spec)
  DELETE /agents/{id}
  POST   /agents/{id}/chat        {"text": "...", "session": "..."} -> {"reply": "..."}
Service webhooks (authenticated by the connector itself):
  POST   /hooks/{connector}/{id}  e.g. /hooks/telegram/grok-bot
"""
from __future__ import annotations

import hmac
import json
import os
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .connectors import REGISTRY
from .registry import AgentSpec, Registry, ValidationError
from .runtime import Runtime

MAX_BODY = 1_000_000


def make_handler(registry: Registry, runtime: Runtime):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def _send(self, code, obj):
            data = json.dumps(obj, ensure_ascii=False).encode()
            self.send_response(code)
            self.send_header("content-type", "application/json; charset=utf-8")
            self.send_header("content-length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _body(self) -> bytes:
            n = int(self.headers.get("content-length") or 0)
            if n > MAX_BODY:
                raise ValueError("body too large")
            return self.rfile.read(n)

        def _authed(self) -> bool:
            key = os.environ.get("AGENTSTORE_API_KEY")
            got = self.headers.get("authorization", "")
            return bool(key) and hmac.compare_digest(got, f"Bearer {key}")  # fail closed if unset

        def _route(self, method):
            path = self.path.split("?")[0].rstrip("/")
            try:
                m = re.fullmatch(r"/hooks/([a-z]+)/([a-z0-9-]+)", path)
                if method == "POST" and m:
                    return self._hook(*m.groups())
                if not self._authed():
                    return self._send(401, {"error": "unauthorized"})
                if path == "/agents" and method == "GET":
                    return self._send(200, [s.to_dict() for s in registry.list()])
                m = re.fullmatch(r"/agents/([a-z0-9-]+)(/chat)?", path)
                if not m:
                    return self._send(404, {"error": "not found"})
                agent_id, chat = m.groups()
                if chat and method == "POST":
                    body = json.loads(self._body() or b"{}")
                    text = body.get("text")
                    if not isinstance(text, str) or not text.strip():
                        return self._send(400, {"error": "text is required"})
                    reply = runtime.chat(registry.get(agent_id), text, str(body.get("session", "default")))
                    return self._send(200, {"reply": reply})
                if method == "GET":
                    return self._send(200, registry.get(agent_id).to_dict())
                if method == "PUT":
                    data = json.loads(self._body())
                    if data.get("id") != agent_id:
                        return self._send(400, {"error": "id in body must match URL"})
                    registry.save(AgentSpec.from_dict(data))
                    return self._send(200, {"ok": True})
                if method == "DELETE":
                    registry.delete(agent_id)
                    return self._send(200, {"ok": True})
                return self._send(405, {"error": "method not allowed"})
            except KeyError:
                self._send(404, {"error": "agent not found"})
            except (ValidationError, ValueError, json.JSONDecodeError) as e:
                self._send(400, {"error": str(e)})
            except Exception:
                self._send(500, {"error": "internal error"})

        def _hook(self, cname, agent_id):
            spec = registry.get(agent_id)
            cfg = spec.connectors.get(cname)
            if cfg is None or cname not in REGISTRY:
                return self._send(404, {"error": "connector not enabled for this agent"})
            conn = REGISTRY[cname](cfg)
            raw = self._body()
            headers = {k.lower(): v for k, v in self.headers.items()}
            if not conn.verify(headers, raw):
                return self._send(401, {"error": "bad signature"})
            payload = json.loads(raw or b"{}")
            if payload.get("type") == "url_verification":  # Slack handshake
                return self._send(200, {"challenge": payload.get("challenge")})
            parsed = conn.parse(payload)
            if parsed is None:
                return self._send(200, {"ok": True, "ignored": True})
            text, session, target = parsed
            reply = runtime.chat(spec, text, session)
            return self._send(200, conn.send(target, reply) or {"ok": True})

        def do_GET(self): self._route("GET")
        def do_POST(self): self._route("POST")
        def do_PUT(self): self._route("PUT")
        def do_DELETE(self): self._route("DELETE")

    return Handler


def serve(host="127.0.0.1", port=8080, registry: Registry | None = None, runtime: Runtime | None = None):
    srv = ThreadingHTTPServer((host, port), make_handler(registry or Registry(), runtime or Runtime()))
    print(f"agentstore listening on http://{host}:{port}")
    srv.serve_forever()
