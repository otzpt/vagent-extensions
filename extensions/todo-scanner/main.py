"""TODO Scanner — collects TODO / FIXME / HACK / XXX comments across the workspace.

V-Agent extension contract:
  register(ctx) is called once at sidecar startup;
  each tool is fn(cwd: str, args: dict) -> str.
"""

import os
import re

MARKERS   = re.compile(r"\b(TODO|FIXME|HACK|XXX)\b[:\s]?(.*)", re.IGNORECASE)
SKIP_DIRS = {".git", "node_modules", "__pycache__", "target", "dist", "build", ".venv", "venv"}
TEXT_EXTS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".c", ".h", ".cpp", ".hpp", ".cs", ".java",
    ".rs", ".go", ".rb", ".php", ".swift", ".kt", ".ino", ".css", ".html", ".md",
    ".yml", ".yaml", ".toml", ".sh", ".ps1", ".sql", ".lua", ".dart",
}
MAX_RESULTS = 200


def list_todos(cwd, args):
    root = str((args or {}).get("path") or cwd or ".")
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for fname in filenames:
            if os.path.splitext(fname)[1].lower() not in TEXT_EXTS:
                continue
            fpath = os.path.join(dirpath, fname)
            try:
                with open(fpath, encoding="utf-8", errors="ignore") as f:
                    for lineno, line in enumerate(f, 1):
                        m = MARKERS.search(line)
                        if m:
                            rel = os.path.relpath(fpath, root)
                            text = (m.group(1).upper() + " " + m.group(2).strip())[:160]
                            out.append(f"{rel}:{lineno}: {text}")
                            if len(out) >= MAX_RESULTS:
                                return "\n".join(out) + f"\n…(stopped at {MAX_RESULTS} results)"
            except OSError:
                continue
    return "\n".join(out) if out else "(no TODO/FIXME/HACK/XXX comments found)"


def register(ctx):
    ctx.add_tool(
        "list_todos",
        list_todos,
        'args: {"path": "optional subfolder"} — scan the workspace for '
        "TODO / FIXME / HACK / XXX comments and return them as file:line: text.",
    )
