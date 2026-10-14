import json
import os
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

from agentstore.registry import AgentSpec, Registry, ValidationError
from agentstore.runtime import Runtime
from agentstore.server import make_handler

ROOT = Path(__file__).resolve().parent.parent / "agents"


class RegistryTests(unittest.TestCase):
    def test_bundled_agents_valid(self):
        self.assertIn("grok-bot", [s.id for s in Registry(ROOT).list()])

    def test_roundtrip_and_validation(self):
        with tempfile.TemporaryDirectory() as d:
            r = Registry(d)
            r.save(AgentSpec.from_dict({"id": "a-1", "name": "A", "system_prompt": "hi"}))
            self.assertEqual(r.get("a-1").name, "A")
            r.delete("a-1")
            self.assertEqual(r.list(), [])
            for bad in ({"id": "../x", "name": "x", "system_prompt": "p"},
                        {"id": "ok", "name": "x", "system_prompt": "p", "bogus": 1},
                        {"id": "ok", "name": "x", "system_prompt": ""}):
                with self.assertRaises(ValidationError):
                    AgentSpec.from_dict(bad)
            with self.assertRaises(ValidationError):
                r.get("../etc")


class ServerTests(unittest.TestCase):
    def setUp(self):
        os.environ.update(AGENTSTORE_API_KEY="k", WH_SECRET="s")
        self.tmp = tempfile.TemporaryDirectory()
        reg = Registry(self.tmp.name)
        reg.save(AgentSpec.from_dict({"id": "bot", "name": "Bot", "system_prompt": "p",
                                      "connectors": {"webhook": {"secret_env": "WH_SECRET"}}}))
        self.srv = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(reg, Runtime(lambda spec, msgs: "echo:" + msgs[-1]["content"])))
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()
        self.base = f"http://127.0.0.1:{self.srv.server_port}"

    def tearDown(self):
        self.srv.shutdown(); self.srv.server_close(); self.tmp.cleanup()

    def call(self, method, path, body=None, headers=None):
        req = urllib.request.Request(self.base + path, method=method, headers=headers or {},
                                     data=json.dumps(body).encode() if body is not None else None)
        try:
            with urllib.request.urlopen(req) as r:
                return r.status, json.load(r)
        except urllib.error.HTTPError as e:
            return e.code, json.load(e)

    def test_auth_required(self):
        self.assertEqual(self.call("GET", "/agents")[0], 401)
        self.assertEqual(self.call("GET", "/agents", headers={"authorization": "Bearer k"})[0], 200)

    def test_chat_and_webhook(self):
        auth = {"authorization": "Bearer k"}
        self.assertEqual(self.call("POST", "/agents/bot/chat", {"text": "yo"}, auth)[1], {"reply": "echo:yo"})
        self.assertEqual(self.call("POST", "/hooks/webhook/bot", {"text": "x"})[0], 401)
        code, out = self.call("POST", "/hooks/webhook/bot", {"text": "x"}, {"x-webhook-secret": "s"})
        self.assertEqual((code, out), (200, {"reply": "echo:x"}))
        self.assertEqual(self.call("POST", "/hooks/slack/bot", {}, {})[0], 404)

    def test_put_agent(self):
        auth = {"authorization": "Bearer k"}
        spec = {"id": "new-one", "name": "N", "system_prompt": "p"}
        self.assertEqual(self.call("PUT", "/agents/new-one", spec, auth)[0], 200)
        self.assertEqual(self.call("PUT", "/agents/other", spec, auth)[0], 400)


if __name__ == "__main__":
    unittest.main()
