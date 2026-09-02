"""A minimal MCP stdio client for the cockpit.

The cockpit exposes exactly three verbs and only over MCP, so the scripts here speak MCP rather than
reaching for the binaries underneath: they drive the same surface a Claude session gets. Nothing in
this file does any of the work — cockpit_publish runs the step, commits, signs and republishes the
union; this only carries the request there and the answer back.
"""
import json, os, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# COCKPIT_TRACE=1 prints the JSON-RPC actually exchanged. Useful when the question is "what did the
# cockpit get told", which is not always what a script meant to tell it.
TRACE = os.environ.get("COCKPIT_TRACE") == "1"


def _trace(direction, msg):
    if TRACE:
        print(f"{direction} {json.dumps(msg, indent=2, sort_keys=True)}", file=sys.stderr)


class Cockpit:
    def __init__(self, repo=REPO):
        self.repo = repo
        env = dict(os.environ, COCKPIT_REPO_DIR=repo)
        self.p = subprocess.Popen([os.path.join(repo, "bin", "cockpit"), "mcp"],
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=None, text=True, env=env, bufsize=1)
        self.n = 0
        self.request("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                                    "clientInfo": {"name": "cockpit-example", "version": "1"}})
        self._send({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}})

    def _send(self, msg):
        _trace("-->", msg)
        self.p.stdin.write(json.dumps(msg) + "\n")
        self.p.stdin.flush()

    def request(self, method, params):
        self.n += 1
        self._send({"jsonrpc": "2.0", "id": self.n, "method": method, "params": params})
        while True:
            line = self.p.stdout.readline()
            if not line:
                raise SystemExit("the cockpit closed its output before answering")
            msg = json.loads(line)
            _trace("<--", msg)
            if msg.get("id") == self.n:
                if "error" in msg:
                    raise SystemExit(f"{method} failed: {msg['error']}")
                return msg["result"]

    def call(self, tool, arguments):
        """One tool call. A refusal is raised rather than returned: every guard in the cockpit —
        the wrong repo, a template outside the ceiling, a failed reproduction — arrives this way,
        and a script that carried on past one would publish something the cockpit declined."""
        res = self.request("tools/call", {"name": tool, "arguments": arguments})
        if res.get("isError"):
            raise SystemExit(f"{tool} refused:\n" +
                             "".join(c.get("text", "") for c in res.get("content", [])))
        return res["structuredContent"]

    def hash(self, path):
        """The content hash of a file, as the substrate computes it."""
        out = subprocess.run([os.path.join(self.repo, "bin", "plankton"), "hash", path],
                             capture_output=True, text=True, cwd=self.repo,
                             env=dict(os.environ, PLANKTON_DIR=os.path.join(self.repo, "registry/plankton")))
        if out.returncode != 0:
            raise SystemExit(out.stderr)
        return out.stdout.strip()

    def close(self):
        self.p.stdin.close()
        self.p.wait(timeout=10)
