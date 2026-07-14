"""HTTP Fetch — lets the V-Agent AI fetch a public URL and read the response.

V-Agent extension contract:
  register(ctx) is called once at sidecar startup;
  each tool is fn(cwd: str, args: dict) -> str.
"""

import urllib.request

MAX_CHARS = 12_000


def fetch_url(cwd, args):
    url = str((args or {}).get("url", "")).strip()
    if not url.startswith(("http://", "https://")):
        return "ERROR: 'url' must start with http:// or https://"
    req = urllib.request.Request(url, headers={"User-Agent": "V-Agent-Extension/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            status = resp.status
            body = resp.read(MAX_CHARS * 4).decode("utf-8", "replace")
    except Exception as e:
        return f"ERROR fetching {url}: {e}"
    if len(body) > MAX_CHARS:
        body = body[:MAX_CHARS] + f"\n…(truncated at {MAX_CHARS} chars)"
    return f"HTTP {status} {url}\n\n{body}"


def register(ctx):
    ctx.add_tool(
        "fetch_url",
        fetch_url,
        'args: {"url": "https://…"} — HTTP GET a public URL and return the '
        "response body (truncated to 12k chars). Use it to read documentation, "
        "REST APIs, or raw files from the internet.",
    )
