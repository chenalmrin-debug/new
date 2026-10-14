import argparse
import json
import sys

from .registry import AgentSpec, Registry
from .runtime import Runtime
from .server import serve


def main(argv=None):
    p = argparse.ArgumentParser(prog="agentstore")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    sh = sub.add_parser("show"); sh.add_argument("id")
    new = sub.add_parser("new"); new.add_argument("id"); new.add_argument("--name"); new.add_argument("--prompt", required=True)
    ch = sub.add_parser("chat"); ch.add_argument("id"); ch.add_argument("text")
    sv = sub.add_parser("serve"); sv.add_argument("--host", default="127.0.0.1"); sv.add_argument("--port", type=int, default=8080)
    a = p.parse_args(argv)
    reg = Registry()
    if a.cmd == "list":
        for s in reg.list():
            print(f"{s.id}\t{s.name}\t{','.join(s.connectors) or '-'}")
    elif a.cmd == "show":
        print(json.dumps(reg.get(a.id).to_dict(), ensure_ascii=False, indent=2))
    elif a.cmd == "new":
        print(reg.save(AgentSpec.from_dict({"id": a.id, "name": a.name or a.id, "system_prompt": a.prompt})))
    elif a.cmd == "chat":
        print(Runtime().chat(reg.get(a.id), a.text))
    elif a.cmd == "serve":
        serve(a.host, a.port)


if __name__ == "__main__":
    sys.exit(main())
