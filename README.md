# jsony-reader

Append-only wiki log manager for the `llm-wiki` structure. Manages
`{Project}/wiki/.system/audit.log.json`.

Pure Python 3, **no dependencies** (stdlib only).

## Install

### Unix (Linux / macOS)

```bash
bash install.sh                       # installs to ~/.claude/scripts/jsony-reader
# or specify a destination:
bash install.sh /custom/path
```

After install, the binary lives at `~/.claude/scripts/jsony-reader/jsony-reader`.

### Windows

```powershell
# PowerShell (recommended):
.\install.ps1                         # installs to %USERPROFILE%\.claude\scripts\jsony-reader
# or specify a destination:
.\install.ps1 C:\tools\jsony-reader
```

You can also **run directly from the repo folder** without installing — the
`jsony-reader.cmd` batch wrapper is checked in and works immediately:

```cmd
jsony-reader --path MyProject init
jsony-reader --path MyProject add '{"title":"hello"}'
```

> **Tip:** After installing, add the destination directory to your `PATH` so
> `jsony-reader` works from any terminal. The installer will print the
> one-liner command to do this.

## Commands

| Command | Description |
|---|---|
| `jsony-reader --path {Project} init [--force]` | create an empty `audit.log.json` |
| `jsony-reader --path {Project} add '<json>'` | append an entry (arg or stdin) |
| `jsony-reader --path {Project} last [N]` | show N most recent (default 5) |
| `jsony-reader --path {Project} list [--limit N] [--json]` | list entries (oldest→newest) |
| `jsony-reader --path {Project} validate` | check every entry against the schema |
| `jsony-reader --path {Project} summary` | aggregate statistics |

`--path` defaults to the current directory; the log always resolves to
`<path>/wiki/.system/audit.log.json`.

## Entry schema

Required: `date` (YYYY-MM-DD), `title`. `date` auto-fills to today if omitted on `add`.
Recognized: `type`/`operation` (init|add|fix|update|feature|implement|ingest|manual),
`status`, `summary`/`notes`, `details`, `files`, `metrics`.

```bash
jsony-reader --path {Project} add '{"date":"2026-06-20","operation":"manual","title":"Update config","status":"success","notes":"..."}'

# stdin also works:
cat entry.json | jsony-reader --path {Project} add
```

## About the JSONY core

`jsony_core.py` is the recursive-descent JSONY parser adapted from
`Kyle-Helmick/Python-JSONY` (GPL-3.0). The original was a teaching exercise:
it parsed one whitespace-free line into a tree and called `exit(1)` on any
error. This adaptation makes it usable as a library — errors raise
`JsonyError`, a `.to_python()` converter recovers real dict/list/str/float/
bool/None values, and a pre-tokenizer adds tolerance for **whitespace,
trailing commas, and `//` + `/* */` comments**.

JSONY is used as the *parse path* for inbound `add` payloads. The log file
itself is written as strict JSON (via the stdlib) so any other tool can read
it; `validate`/`last`/etc. read strict JSON first and fall back to the JSONY
parser if the file was hand-edited into a loose form.

**Known quirk:** JSONY (like JSON) has a single number type and parses every
number as a float, so `1` round-trips through `add` parsing as `1.0`. This is
harmless for the log (its fields are strings) but worth knowing if you store
numeric `metrics`.
