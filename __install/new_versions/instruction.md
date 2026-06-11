# Terminal Command Documentation Rule

Use this rule for future terminal-based work in this repo.

## Goal
- Keep a clear step-by-step terminal history.
- Keep install, snapshot, refill, and restore behavior reproducible.
- Separate project-local execution history from global computer/infra history.

## Scope Modes

### 1. Project mode (default)
Use when the task is specific to this repo/app.

Write step files under:
- `<project_root>/__install/terminal`

### 2. Global Ops mode
Use when the task changes shared computer/system/VPS policy beyond this repo.

Write raw evidence directly under:
- `/Users/kyawhtet/Library/CloudStorage/GoogleDrive-kyaw.htet.yang@gmail.com/My Drive/25.07 Obsidian/2. Computer/00_Inbox/Terminal/YYYY/YYYY-MM/`

Promote the shared install/ops rule into the clean vault under:
- `/Users/kyawhtet/Library/CloudStorage/GoogleDrive-kyaw.htet.yang@gmail.com/My Drive/(1) Timeline/25.08_Obsidian_Clean/00_System/06_Ops/01_Install/README.md`

## Direct Raw Write Rule
For Global Ops mode, do not write to project terminal folders and copy later.

Required behavior:
1. Generate the raw step file directly in the final `2. Computer/00_Inbox/Terminal/YYYY/YYYY-MM/` folder.
2. Use `--output-dir` or `TERMINAL_DIR` to point to that final destination at write time.
3. Treat manual transfer/copy as fallback only for recovery, not normal workflow.

## Install Workflow Context
- `v0` is the active/live workflow.
- `v1+` are snapshot/history references.
- Use `run-install` as the preferred user-facing entrypoint.
- `run_back.py` generates `all_back.txt`, `file_tree.txt`, and `manifest.json`.
- `run.py` restores text/code from `all.txt`.
- `run_refill.py` restores externalized files from pCloud using `manifest.json`.

## Output Path Resolution

### Project mode
Priority order:
1. `--output-dir`
2. `TERMINAL_DIR`
3. `<project_root>/__install/terminal`

Safety rule:
- final output path must stay inside `<project_root>/__install`

### Global Ops mode
Priority order:
1. `--output-dir`
2. `TERMINAL_DIR`
3. `/Users/kyawhtet/Library/CloudStorage/GoogleDrive-kyaw.htet.yang@gmail.com/My Drive/25.07 Obsidian/2. Computer/00_Inbox/Terminal/YYYY/YYYY-MM/`

Safety rule:
- final output path must stay inside `2. Computer/00_Inbox/Terminal`

## Naming Convention
- `Step1_<short-topic>.md`
- `Step2_<short-topic>.md`
- `Step3_<short-topic>.md`
- use ASCII only, `_`, and no spaces

## Required Content
1. Scope
2. Exact terminal commands used
3. Verification checks
4. Result status (`done` / `failed` / `needs follow-up`)
5. Next step reference if any
6. If global-ops related, list promoted files/rules

## Style Rules
- No chat transcript.
- Keep it execution-focused.
- Use absolute paths when helpful.
