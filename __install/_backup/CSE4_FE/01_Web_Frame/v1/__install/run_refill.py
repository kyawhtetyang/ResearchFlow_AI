import os
import shutil
import sys
from pathlib import Path

from restore_config import (
    file_sha256,
    load_manifest,
    safe_join_project_root,
    should_skip_restore_path,
)


SCRIPT_PATH = os.path.abspath(__file__)
INSTALL_FOLDER = os.path.dirname(SCRIPT_PATH)
PROJECT_ROOT = os.path.dirname(INSTALL_FOLDER)

EXTRA_REFILL_SKIP_SUFFIXES = (".DS_Store",)


def should_skip(rel_path):
    return should_skip_restore_path(rel_path, extra_suffixes=EXTRA_REFILL_SKIP_SUFFIXES)


def under_any_refill_root(rel_path, refill_roots):
    normalized = rel_path.replace("\\", "/").strip("/")
    for root in refill_roots:
        clean_root = root.replace("\\", "/").strip("/")
        if normalized == clean_root or normalized.startswith(clean_root + "/"):
            return True
    return False


def resolve_source_root(manifest):
    source = manifest.get("refill_source")
    if not source:
        print("❌ refill_source missing in manifest.json")
        sys.exit(1)

    source_root = Path(os.path.expanduser(source)).resolve()
    if not source_root.is_dir():
        print(f"❌ Refill source folder not found: {source_root}")
        sys.exit(1)
    return source_root


def refill_from_manifest_files(source_root: Path, refill_files):
    copied_files = []
    overwritten_files = []
    already_correct = []
    skipped_rules = []
    missing_sources = []
    source_mismatch = []
    verify_failed = []

    for entry in refill_files:
        rel_file = (entry.get("path") or "").replace("\\", "/").strip("/")
        expected_hash = entry.get("sha256")
        if not rel_file:
            continue
        if should_skip(rel_file):
            skipped_rules.append(rel_file)
            continue

        src_file = source_root / rel_file
        if not src_file.is_file():
            missing_sources.append(rel_file)
            continue

        if expected_hash and file_sha256(src_file) != expected_hash:
            source_mismatch.append(rel_file)
            continue

        try:
            _, dst_file = safe_join_project_root(PROJECT_ROOT, rel_file)
        except ValueError:
            skipped_rules.append(rel_file)
            continue

        existed_before = os.path.exists(dst_file)
        if existed_before and expected_hash and file_sha256(dst_file) == expected_hash:
            already_correct.append(rel_file)
            continue

        os.makedirs(os.path.dirname(dst_file), exist_ok=True)
        shutil.copy2(src_file, dst_file)

        if expected_hash and file_sha256(dst_file) != expected_hash:
            verify_failed.append(rel_file)
            continue

        if existed_before:
            overwritten_files.append(rel_file)
        else:
            copied_files.append(rel_file)

    return {
        "copied": copied_files,
        "overwritten": overwritten_files,
        "already_correct": already_correct,
        "skipped": sorted(set(skipped_rules)),
        "missing_sources": sorted(set(missing_sources)),
        "source_mismatch": sorted(set(source_mismatch)),
        "verify_failed": sorted(set(verify_failed)),
    }


def refill_from_roots(source_root: Path, refill_roots):
    copied_files = []
    skipped_existing = []
    skipped_rules = []
    missing_roots = []

    for refill_root in refill_roots:
        source_dir = source_root / refill_root.rstrip("/")
        if not source_dir.exists():
            missing_roots.append(refill_root)

    for root, dirs, files in os.walk(source_root):
        rel_dir = os.path.relpath(root, source_root).replace("\\", "/")
        if rel_dir == ".":
            rel_dir = ""

        pruned = []
        for folder in dirs:
            rel_d = f"{rel_dir}/{folder}".strip("/")
            if should_skip(rel_d + "/"):
                skipped_rules.append(rel_d + "/")
            else:
                pruned.append(folder)
        dirs[:] = pruned

        for filename in files:
            rel_file = f"{rel_dir}/{filename}".strip("/")
            if not under_any_refill_root(rel_file, refill_roots):
                continue
            if should_skip(rel_file):
                skipped_rules.append(rel_file)
                continue

            try:
                _, dst_file = safe_join_project_root(PROJECT_ROOT, rel_file)
            except ValueError:
                skipped_rules.append(rel_file)
                continue

            src_file = source_root / rel_file
            if os.path.exists(dst_file):
                skipped_existing.append(rel_file)
                continue

            os.makedirs(os.path.dirname(dst_file), exist_ok=True)
            shutil.copy2(src_file, dst_file)
            copied_files.append(rel_file)

    return {
        "copied": copied_files,
        "overwritten": [],
        "already_correct": skipped_existing,
        "skipped": sorted(set(skipped_rules)),
        "missing_sources": sorted(set(missing_roots)),
        "source_mismatch": [],
        "verify_failed": [],
    }


def main():
    try:
        manifest = load_manifest(INSTALL_FOLDER)
    except FileNotFoundError as exc:
        print(f"❌ {exc}")
        sys.exit(1)

    source_root = resolve_source_root(manifest)
    refill_files = manifest.get("refill_files", [])
    refill_roots = manifest.get("refill_paths", [])

    if not refill_files and not refill_roots:
        print("ℹ️ No refill entries recorded in manifest.json.")
        print("   Nothing to refill.")
        return

    print(f"🔄 Refill source: {source_root}")
    print(f"🎯 Refill target: {PROJECT_ROOT}\n")

    if refill_files:
        print("📌 Refill scope (exact manifest files):")
        for entry in refill_files[:20]:
            print(f"   - {entry.get('path')}")
        if len(refill_files) > 20:
            print(f"   ... and {len(refill_files) - 20} more")
        print("")
        summary = refill_from_manifest_files(source_root, refill_files)
    else:
        print("📌 Refill scope (legacy manifest roots):")
        for root in refill_roots:
            print(f"   - {root}")
        print("")
        summary = refill_from_roots(source_root, refill_roots)

    for rel in summary["copied"]:
        print(f"✅ Copied missing file: {os.path.join(PROJECT_ROOT, rel)}")
    for rel in summary["overwritten"]:
        print(f"♻️ Replaced mismatched file: {os.path.join(PROJECT_ROOT, rel)}")

    print("\n📊 Refill summary")
    print(f"   Copied missing files: {len(summary['copied'])}")
    print(f"   Overwritten mismatched files: {len(summary['overwritten'])}")
    print(f"   Already correct: {len(summary['already_correct'])}")
    print(f"   Skipped by rules: {len(summary['skipped'])}")
    print(f"   Missing source files/roots: {len(summary['missing_sources'])}")
    print(f"   Source hash mismatches: {len(summary['source_mismatch'])}")
    print(f"   Verify failures after copy: {len(summary['verify_failed'])}")

    if summary["missing_sources"]:
        print("   Missing sources:")
        for rel in summary["missing_sources"][:30]:
            print(f"   - {rel}")
        if len(summary["missing_sources"]) > 30:
            print(f"   ... and {len(summary['missing_sources']) - 30} more")

    if summary["source_mismatch"]:
        print("   Source hash mismatches:")
        for rel in summary["source_mismatch"][:30]:
            print(f"   - {rel}")
        if len(summary["source_mismatch"]) > 30:
            print(f"   ... and {len(summary['source_mismatch']) - 30} more")

    if summary["verify_failed"]:
        print("   Verify failures:")
        for rel in summary["verify_failed"][:30]:
            print(f"   - {rel}")
        if len(summary["verify_failed"]) > 30:
            print(f"   ... and {len(summary['verify_failed']) - 30} more")

    if summary["skipped"]:
        print("   Skipped paths:")
        for rel in summary["skipped"][:30]:
            print(f"   - {rel}")
        if len(summary["skipped"]) > 30:
            print(f"   ... and {len(summary['skipped']) - 30} more")


if __name__ == "__main__":
    main()
