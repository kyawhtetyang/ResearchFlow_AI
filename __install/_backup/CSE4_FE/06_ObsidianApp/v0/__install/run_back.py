# load/new_versions/run_back.py
import fnmatch
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path

from restore_config import (
    is_valid_version,
    MANIFEST_SCHEMA_VERSION,
    default_refill_source,
    detect_project_name,
    file_metadata,
    normalize_snapshot_rel_path,
    project_snapshot_root,
    should_skip_restore_path,
    write_manifest,
)

# =========================
# CONFIGURATION
# =========================
FOLDER_MODE = "top"

INCLUDE_COMMAND_LINE = False
INCLUDE_FILE_TREE = True
INCLUDE_BODY = True

INCLUDE_INVISIBLE_FILES = True
INCLUDE_INVISIBLE_FOLDERS = False
KEEP_BINARY_PLACEHOLDER = False

EXCLUDED_PATH_PATTERNS = [
    "backend/data",
    "backend_fastapi/data",
    "data",
]

BLACKLIST_FOLDERS = {
    "__install",
    ".git",
    ".venv",
    ".idea",
    ".vscode",
    "__pycache__",
    ".next",
    "dist",
    "node_modules",
    "_backup",
    "build",
    "target",
    "release",
    ".release",
    "out",
}

BLACKLIST_FILES = {
    ".DS_Store",
    "package-lock.json",
}

EXTERNALIZE_EXTENSIONS = {
    ".db",
    ".sqlite",
    ".sqlite3",
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
    ".ico",
    ".icns",
    ".webp",
    ".heic",
    ".gif",
    ".bmp",
    ".tiff",
    ".avif",
    ".zip",
}

INVISIBLE_FILE_WHITELIST = {".env", ".gitignore"}
SNAPSHOT_DIR_NAME = "__snapshot"

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INSTALL_FOLDER = os.path.join(PROJECT_ROOT, "__install")
OUTPUT_FILE = os.path.join(INSTALL_FOLDER, "all_back.txt")

LANG_MAP = {
    ".py": "python",
    ".html": "html",
    ".js": "javascript",
    ".css": "css",
    ".txt": "text",
    ".md": "markdown",
    ".json": "json",
    ".yml": "yaml",
    ".yaml": "yaml",
    ".sh": "shell",
    ".bat": "bat",
    ".tsx": "tsx",
    ".ts": "ts",
    ".sql": "sql",
    "": "shell",
}


def normalize_rel_path(path: str) -> str:
    value = (path or "").strip().replace("\\", "/")
    if not value:
        return ""

    if os.path.isabs(value):
        abs_root = os.path.realpath(PROJECT_ROOT)
        abs_path = os.path.realpath(value)
        try:
            if os.path.commonpath([abs_root, abs_path]) != abs_root:
                return ""
        except ValueError:
            return ""
        value = os.path.relpath(abs_path, abs_root).replace("\\", "/")

    while value.startswith("./"):
        value = value[2:]

    try:
        normalized = normalize_snapshot_rel_path(value)
    except ValueError:
        return ""
    return normalized.strip("/")


def parse_exclusion_rule(raw_pattern: str):
    raw = (raw_pattern or "").strip().replace("\\", "/")
    if not raw:
        return None

    is_children_marker = False
    if raw.endswith("/*"):
        is_children_marker = True
        raw = raw[:-2]
    elif raw.endswith("/"):
        is_children_marker = True
        raw = raw[:-1]

    normalized = normalize_rel_path(raw)
    if not normalized:
        return None

    if is_children_marker:
        return ("children_only", normalized)

    if not any(ch in normalized for ch in "*?["):
        candidate_abs = os.path.join(PROJECT_ROOT, normalized)
        if os.path.isfile(candidate_abs):
            return ("full", normalized)
        return ("children_only", normalized)

    return ("glob", normalized)


def get_path_exclusion_state(rel_path: str, is_dir: bool) -> str:
    rel = normalize_rel_path(rel_path)
    for raw_pattern in EXCLUDED_PATH_PATTERNS:
        rule = parse_exclusion_rule(raw_pattern)
        if not rule:
            continue
        kind, value = rule

        if kind == "children_only":
            if is_dir and rel == value:
                return "children_only"
            if rel.startswith(value + "/"):
                return "full"
            continue

        if kind == "full" and rel == value:
            return "full"

        if kind == "glob" and fnmatch.fnmatch(rel, value):
            return "full"

    return "none"


def should_ignore_hidden(name: str) -> bool:
    if not name.startswith("."):
        return False
    return name not in INVISIBLE_FILE_WHITELIST


def should_ignore_file(name: str) -> bool:
    if name in BLACKLIST_FILES:
        return True
    if should_ignore_hidden(name) and not INCLUDE_INVISIBLE_FILES:
        return True
    return False


def should_externalize_by_extension(filename: str) -> bool:
    _, ext = os.path.splitext(filename)
    return ext.lower() in EXTERNALIZE_EXTENSIONS


def is_probably_binary_file(file_path: str) -> bool:
    if should_externalize_by_extension(os.path.basename(file_path)):
        return True

    try:
        with open(file_path, "rb") as handle:
            chunk = handle.read(4096)
    except OSError:
        return False

    if not chunk:
        return False
    if b"\x00" in chunk:
        return True
    try:
        chunk.decode("utf-8")
    except UnicodeDecodeError:
        return True
    return False


def detect_version():
    return os.path.basename(PROJECT_ROOT)


def prompt_snapshot_label():
    env_label = os.environ.get("SNAPSHOT_LABEL", "").strip()
    if env_label:
        if not is_valid_version(env_label):
            raise ValueError(f"invalid SNAPSHOT_LABEL: {env_label}")
        return env_label

    while True:
        label = input("🏷️ Snapshot label (e.g. v1, v2.1; blank to skip): ").strip()
        if not label:
            return ""
        if is_valid_version(label):
            return label
        print("❌ Invalid label. Use forms like v1, v2, or v2.1")


def get_language(filename):
    if filename == ".env":
        return "shell"
    if filename == ".gitignore":
        return "text"
    _, ext = os.path.splitext(filename)
    return LANG_MAP.get(ext.lower(), "shell")


def read_text_lines(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as handle:
            return [line.rstrip() for line in handle]
    except UnicodeDecodeError:
        return None


def write_folder(folder, version, f_out):
    f_out.write(f"### {folder}\n")
    f_out.write("```python\n")
    f_out.write(f"# {version}/{folder}/\n")
    f_out.write("```\n\n")


def write_file(file_path, rel_path, version, level, f_out):
    filename = os.path.basename(file_path)
    if should_ignore_file(filename):
        return
    if is_probably_binary_file(file_path):
        if KEEP_BINARY_PLACEHOLDER:
            lang = get_language(filename)
            f_out.write(f"{'#' * level} {filename}\n")
            f_out.write(f"```{lang}\n")
            f_out.write(f"# {version}/{rel_path}\n")
            f_out.write("[binary file externalized]\n")
            f_out.write("```\n\n")
        return

    content_lines = read_text_lines(file_path)
    if content_lines is None:
        return

    lang = get_language(filename)
    f_out.write(f"{'#' * level} {filename}\n")
    f_out.write(f"```{lang}\n")
    f_out.write(f"# {version}/{rel_path}\n")
    for line in content_lines:
        f_out.write(line + "\n")
    f_out.write("```\n\n")


def sort_entries(path):
    entries = os.listdir(path)

    def sort_key(name):
        full = os.path.join(path, name)
        is_dir = os.path.isdir(full)
        if FOLDER_MODE == "down":
            return (0 if not is_dir else 1, name.lower())
        if FOLDER_MODE == "alphabet":
            return (name.lower(),)
        return (0 if is_dir else 1, name.lower())

    return sorted(entries, key=sort_key)


def traverse(path, level, f_out, version):
    entries = sort_entries(path)

    for entry in entries:
        full = os.path.join(path, entry)
        rel_path = os.path.relpath(full, PROJECT_ROOT).replace("\\", "/")
        exclusion_state = get_path_exclusion_state(rel_path, os.path.isdir(full))

        if os.path.isdir(full) and entry in BLACKLIST_FOLDERS:
            continue
        if exclusion_state == "full":
            continue
        if os.path.isdir(full) and should_ignore_hidden(entry) and not INCLUDE_INVISIBLE_FOLDERS:
            continue
        if os.path.isfile(full) and should_ignore_file(entry):
            continue

        if os.path.isdir(full):
            write_folder(rel_path, version, f_out)
            if exclusion_state == "children_only":
                continue
            traverse(full, level + 1, f_out, version)
        else:
            write_file(full, rel_path, version, level, f_out)


def generate_file_tree(path, prefix=""):
    lines = []
    entries = sort_entries(path)

    filtered_entries = []
    for entry in entries:
        full = os.path.join(path, entry)
        rel_path = os.path.relpath(full, PROJECT_ROOT).replace("\\", "/")

        if os.path.isdir(full) and entry in BLACKLIST_FOLDERS:
            continue
        if os.path.isdir(full) and should_ignore_hidden(entry) and not INCLUDE_INVISIBLE_FOLDERS:
            continue
        if os.path.isfile(full) and should_ignore_file(entry):
            continue
        if get_path_exclusion_state(rel_path, os.path.isdir(full)) == "full":
            continue
        filtered_entries.append(entry)

    for i, entry in enumerate(filtered_entries):
        full = os.path.join(path, entry)
        rel_path = os.path.relpath(full, PROJECT_ROOT).replace("\\", "/")
        exclusion_state = get_path_exclusion_state(rel_path, os.path.isdir(full))

        connector = "└─ " if i == len(filtered_entries) - 1 else "├─ "
        if os.path.isdir(full):
            lines.append(f"{prefix}{connector}{entry}/")
            if exclusion_state == "children_only":
                continue
            new_prefix = prefix + ("    " if i == len(filtered_entries) - 1 else "│   ")
            lines.extend(generate_file_tree(full, new_prefix))
        else:
            lines.append(f"{prefix}{connector}{entry}")
    return lines


def iter_project_files():
    for root, dirs, files in os.walk(PROJECT_ROOT):
        rel_dir = os.path.relpath(root, PROJECT_ROOT).replace("\\", "/")
        if rel_dir == ".":
            rel_dir = ""

        pruned_dirs = []
        for folder in dirs:
            if folder in BLACKLIST_FOLDERS:
                continue
            if should_ignore_hidden(folder) and not INCLUDE_INVISIBLE_FOLDERS:
                continue
            rel_folder = f"{rel_dir}/{folder}".strip("/")
            if get_path_exclusion_state(rel_folder, True) == "full":
                continue
            pruned_dirs.append(folder)
        dirs[:] = pruned_dirs

        for filename in files:
            if should_ignore_file(filename):
                continue
            rel_file = f"{rel_dir}/{filename}".strip("/")
            if not rel_file:
                continue
            yield os.path.join(root, filename), rel_file


def build_refill_entries():
    entries = []
    seen = set()

    for source_file, rel_path in iter_project_files():
        if should_skip_restore_path(rel_path):
            continue
        if rel_path in seen:
            continue

        reason = None
        if get_path_exclusion_state(rel_path, False) == "full":
            reason = "excluded_path"
        elif is_probably_binary_file(source_file):
            reason = "binary_detected"
        else:
            continue

        payload = file_metadata(source_file)
        payload["path"] = rel_path
        payload["reason"] = reason
        entries.append(payload)
        seen.add(rel_path)

    return sorted(entries, key=lambda item: item["path"])


def build_manifest(version, refill_source: Path, refill_entries, snapshot_label):
    refill_paths = []
    for raw_pattern in EXCLUDED_PATH_PATTERNS:
        rule = parse_exclusion_rule(raw_pattern)
        if not rule:
            continue
        kind, value = rule
        if kind != "children_only":
            continue
        abs_candidate = os.path.join(PROJECT_ROOT, value)
        if os.path.exists(abs_candidate):
            refill_paths.append(value + "/")

    return {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project_name": detect_project_name(PROJECT_ROOT),
        "active_version": version,
        "snapshot_label": snapshot_label or None,
        "history_id": None,
        "snapshot_store": "live",
        "snapshot_file": "all_back.txt",
        "refill_source": str(refill_source),
        "refill_paths": sorted(set(refill_paths)),
        "refill_files": refill_entries,
        "excluded_path_patterns": EXCLUDED_PATH_PATTERNS,
    }


def comparable_manifest_payload(payload):
    clean = json.loads(json.dumps(payload))
    clean.pop("generated_at", None)
    return clean


def should_archive_existing_source(refill_source: Path, manifest_payload):
    snapshot_dir = refill_source / SNAPSHOT_DIR_NAME
    previous_all = snapshot_dir / "all_back.txt"
    previous_manifest = snapshot_dir / "manifest.json"
    if not previous_all.is_file() or not previous_manifest.is_file():
        return False

    current_all = Path(OUTPUT_FILE).read_bytes()
    previous_all_bytes = previous_all.read_bytes()
    if current_all != previous_all_bytes:
        return True

    previous_payload = json.loads(previous_manifest.read_text(encoding="utf-8"))
    return comparable_manifest_payload(previous_payload) != comparable_manifest_payload(manifest_payload)


def archive_existing_source(refill_source: Path):
    if not refill_source.exists():
        return None

    live_manifest_file = refill_source / SNAPSHOT_DIR_NAME / "manifest.json"
    archive_label = None
    if live_manifest_file.is_file():
        payload = json.loads(live_manifest_file.read_text(encoding="utf-8"))
        candidate = (payload.get("snapshot_label") or "").strip()
        if candidate and is_valid_version(candidate) and candidate != "v0":
            archive_label = candidate

    snapshot_root = project_snapshot_root(PROJECT_ROOT)
    if archive_label:
        archive_path = snapshot_root / archive_label
    else:
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")
        archive_path = snapshot_root / stamp

    archive_path.parent.mkdir(parents=True, exist_ok=True)
    if archive_path.exists():
        shutil.rmtree(archive_path)
    shutil.copytree(refill_source, archive_path)

    snapshot_manifest = archive_path / SNAPSHOT_DIR_NAME / "manifest.json"
    if snapshot_manifest.is_file():
        payload = json.loads(snapshot_manifest.read_text(encoding="utf-8"))
        payload["history_id"] = archive_path.name
        payload["snapshot_store"] = "history"
        payload["refill_source"] = str(archive_path)
        snapshot_manifest.write_text(
            json.dumps(payload, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
    return archive_path


def sync_refill_entries(refill_source: Path, refill_entries):
    for entry in refill_entries:
        rel_path = entry["path"]
        source_file = Path(PROJECT_ROOT) / rel_path
        if not source_file.is_file():
            continue
        target_path = refill_source / rel_path
        target_path.parent.mkdir(parents=True, exist_ok=True)
        if target_path.is_file() and file_metadata(target_path)["sha256"] == entry["sha256"]:
            continue
        shutil.copy2(source_file, target_path)


def sync_snapshot_bundle(refill_source: Path, manifest_file: str):
    snapshot_dir = refill_source / SNAPSHOT_DIR_NAME
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(OUTPUT_FILE, snapshot_dir / "all_back.txt")
    shutil.copy2(manifest_file, snapshot_dir / "manifest.json")


def main():
    version = detect_version()
    os.makedirs(INSTALL_FOLDER, exist_ok=True)
    snapshot_label = prompt_snapshot_label()

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f_out:
        if INCLUDE_COMMAND_LINE:
            f_out.write("```shell\n")
            f_out.write(f"cd {PROJECT_ROOT}\n")
            f_out.write("```\n\n")

        if INCLUDE_FILE_TREE:
            f_out.write("### __install/map.txt\n")
            f_out.write("```python\n")
            f_out.write(f"# {version}/__install/map.txt\n")
            f_out.write(f"{version}/\n")
            for line in generate_file_tree(PROJECT_ROOT):
                f_out.write(line + "\n")
            f_out.write("```\n\n")

        if INCLUDE_BODY:
            traverse(PROJECT_ROOT, 3, f_out, version)

    refill_source = default_refill_source(PROJECT_ROOT)
    refill_source.mkdir(parents=True, exist_ok=True)
    refill_entries = build_refill_entries()
    manifest_payload = build_manifest(version, refill_source, refill_entries, snapshot_label)

    archived_to = None
    if should_archive_existing_source(refill_source, manifest_payload):
        archived_to = archive_existing_source(refill_source)

    sync_refill_entries(refill_source, refill_entries)
    manifest_file = write_manifest(INSTALL_FOLDER, manifest_payload)
    sync_snapshot_bundle(refill_source, manifest_file)

    print(f"✅ Export complete: {OUTPUT_FILE}")
    print(f"🧾 Manifest written: {manifest_file}")
    if snapshot_label:
        print(f"🏷️ Snapshot label: {snapshot_label}")
    print(f"📦 Externalized refill files: {len(refill_entries)}")
    if archived_to is not None:
        print(f"🗂️ Archived previous refill source to: {archived_to}")
    else:
        print("🗂️ No history snapshot created (no diff).")


if __name__ == "__main__":
    main()
