# V-Agent Extensions

The open extension registry for [V-Agent](https://github.com/otzpt/V-Agent). Extensions are small Python modules that give V-Agent's AI agent new tools — the agent can call them mid-conversation just like its built-in `read_file` / `run_command` tools.

The **Extensions** panel inside V-Agent reads [`registry.json`](registry.json) from this repo and installs entries with one click.

## Available extensions

| Extension | What the AI gains |
|-----------|-------------------|
| **HTTP Fetch** | `fetch_url` — GET any public URL (docs, REST APIs, raw files) |
| **TODO Scanner** | `list_todos` — structured list of every TODO/FIXME/HACK/XXX in the workspace |
| **Serial Tools** | `list_serial_ports`, `serial_send` — talk to Arduino/Pico/ESP32 boards over serial |

## Writing an extension

An extension is a single `main.py` exposing `register(ctx)`:

```python
def my_tool(cwd, args):
    """cwd: workspace root the user has open; args: dict from the AI's tool call.
    Return a string — it goes straight back to the AI."""
    return f"you said {args.get('message', '')!r}"

def register(ctx):
    ctx.add_tool(
        "my_tool",
        my_tool,
        'args: {"message": "…"} — describe here exactly when and how the AI should use this.',
    )
```

Rules of thumb:
- **Return strings, never raise** — errors should come back as `"ERROR: …"` so the AI can react.
- **Stdlib only** if possible; if you need a package, detect the `ImportError` and return the `pip install …` command as the error message.
- The description is your tool's prompt — document the `args` shape in it.

## Submitting

1. Add `extensions/<your-id>/main.py`.
2. Add an entry to `registry.json` (`id`, `name`, `version`, `author`, `description`, `tags`, `repo`, `entry`).
3. Open a pull request.

## Security note

Extensions run as plain Python with your user permissions inside V-Agent's sidecar. Only install extensions whose source you've read — the **View source** button on every card takes you straight to it.

## License

MIT
