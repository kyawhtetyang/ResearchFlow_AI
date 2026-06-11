import os
import shutil
import hashlib
import re

# ==========================================================
# CONFIG / CONSTANTS (class-based)
# ==========================================================
class Config:
    # Operation modes
    DRY_RUN = False       # if True, no files are changed
    UNDO = False          # restore latest backup only
    REPLACE_ALL = False   # if True, clears __install folder before copying

    # Paths
    MASTER_CS_FOLDER = os.path.expanduser("~/execution")
    SCRIPT_FOLDER = os.path.dirname(os.path.abspath(__file__))
    NEW_VERSIONS_FOLDER = os.path.join(SCRIPT_FOLDER, "new_versions")
    BACKUP_FOLDER = os.path.join(SCRIPT_FOLDER, "_backup")
    BACKUP_ONLY_FILE = "all.txt"

    # Rules
    EXCLUDE_PATHS = [
        os.path.join(SCRIPT_FOLDER, "_backup")
    ]
    WALK_SKIP_DIRS = {
        '__install',
        '_backup',
        '.git',
        '.venv',
        'venv',
        'env',
        'node_modules',
        'site-packages',
        '__pycache__',
        'dist',
        'build',
        'target',
        'release',
        'out',
        '.next',
    }
    COPY_IF_MISSING = []
    PRESERVE_LOCAL_ITEMS = {
        'all.txt',
        'all_back.txt',
        'file_tree.txt',
        'manifest.json',
        '.build_hash',
        '__pycache__',
    }
    PRESERVE_LOCAL_PATTERNS = (
        re.compile(r'^start_[a-z0-9_]+\.sh$', re.I),
        re.compile(r'^stop_[a-z0-9_]+\.sh$', re.I),
    )

# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def compute_hash(file_path):
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def backup_file(file_path):
    """Backup only all.txt preserving folder structure"""
    if os.path.basename(file_path) != Config.BACKUP_ONLY_FILE:
        return

    rel_path = os.path.relpath(file_path, Config.MASTER_CS_FOLDER)
    backup_path = os.path.join(Config.BACKUP_FOLDER, rel_path)

    os.makedirs(os.path.dirname(backup_path), exist_ok=True)
    shutil.copy(file_path, backup_path)
    os.utime(backup_path, None)

    print(f"💾 Backup saved: {backup_path}")


def restore_latest_backup_only():
    backups = []

    for root, _, files in os.walk(Config.BACKUP_FOLDER):
        for f in files:
            if f == Config.BACKUP_ONLY_FILE:
                src = os.path.join(root, f)
                dst = os.path.join(
                    Config.MASTER_CS_FOLDER,
                    os.path.relpath(src, Config.BACKUP_FOLDER)
                )
                backups.append((src, dst, os.path.getmtime(src)))

    if not backups:
        print("⚠️ No backups found.")
        return

    latest_time = max(b[2] for b in backups)

    for src, dst, mtime in backups:
        if mtime == latest_time:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy(src, dst)
            os.utime(dst, None)
            print(f"♻️ Restored: {dst}")


def file_differs(src, dst):
    return not os.path.exists(dst) or compute_hash(src) != compute_hash(dst)


def is_preserved_local_item(name):
    if name in Config.PRESERVE_LOCAL_ITEMS:
        return True

    return any(pattern.match(name) for pattern in Config.PRESERVE_LOCAL_PATTERNS)


def update_run_version(file_path, version):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    new_content = re.sub(
        r'version\s*=\s*[\'"].*?[\'"]',
        f"version = '{version}'",
        content
    )

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)


def should_copy(src, dst):
    if Config.REPLACE_ALL:
        return True

    name = os.path.basename(src)

    # Never overwrite locally-generated snapshot files (e.g. all_back.txt).
    if is_preserved_local_item(name):
        return False

    if name in Config.COPY_IF_MISSING:
        return not os.path.exists(dst)

    return file_differs(src, dst)


def copy_new_versions(src_folder, dst_folder, folder_name):
    actions = []

    for item in os.listdir(src_folder):
        if item in Config.PRESERVE_LOCAL_ITEMS:
            continue

        src = os.path.join(src_folder, item)
        dst = os.path.join(dst_folder, item)

        if os.path.isfile(src):
            if not should_copy(src, dst):
                continue

            if os.path.exists(dst) and not Config.DRY_RUN:
                backup_file(dst)

            if not Config.DRY_RUN:
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy(src, dst)
                os.utime(dst, None)

                if item == "run.py":
                    update_run_version(dst, folder_name)

            actions.append(item)

        elif os.path.isdir(src):
            if not os.path.exists(dst) and not Config.DRY_RUN:
                os.makedirs(dst, exist_ok=True)

            sub = copy_new_versions(src, dst, folder_name)
            actions += [f"{item}/{s}" for s in sub]

    return actions


def delete_path(path):
    if os.path.isdir(path) and not os.path.islink(path):
        shutil.rmtree(path)
    else:
        os.remove(path)


def remove_stale_install_items(install_path):
    if not os.path.isdir(install_path):
        return []

    expected_items = set(os.listdir(Config.NEW_VERSIONS_FOLDER))
    keep_items = expected_items | Config.PRESERVE_LOCAL_ITEMS
    removed = []

    for item in sorted(os.listdir(install_path)):
        if item in keep_items or is_preserved_local_item(item):
            continue

        target = os.path.join(install_path, item)
        print(f"🗑 Deleting stale item: {target}")

        if not Config.DRY_RUN:
            backup_file(target)
            delete_path(target)

        removed.append(item)

    return removed


def clear_install_folder(path):
    if os.path.exists(path):
        print(f"🗑 Clearing: {path}")
        if not Config.DRY_RUN:
            shutil.rmtree(path)


# ==========================================================
# MAIN
# ==========================================================

def main():
    if Config.UNDO:
        print("⏸ UNDO MODE")
        restore_latest_backup_only()
        return

    total_folders = 0
    total_items = 0

    for root, dirs, _ in os.walk(Config.MASTER_CS_FOLDER):
        dirs[:] = [d for d in dirs if d not in Config.WALK_SKIP_DIRS]
        folder_name = os.path.basename(root)

        if not re.match(r"v([0-9]|[1-9][0-9])(\.([1-9]|[1-9][0-9]))?$", folder_name, re.I):
            continue

        parent = os.path.dirname(root)
        if not re.match(r"\d{2}_.*", os.path.basename(parent)):
            continue

        if any(os.path.abspath(root).startswith(os.path.abspath(p)) for p in Config.EXCLUDE_PATHS):
            continue

        install_path = os.path.join(root, "__install")

        if Config.REPLACE_ALL:
            clear_install_folder(install_path)

        if not os.path.exists(install_path) and not Config.DRY_RUN:
            os.makedirs(install_path, exist_ok=True)

        removed = remove_stale_install_items(install_path)
        actions = copy_new_versions(Config.NEW_VERSIONS_FOLDER, install_path, folder_name)

        changed_items = removed + actions
        if changed_items:
            print(f"✅ {'Would update' if Config.DRY_RUN else 'Updated'}: {install_path}")
            total_items += len(changed_items)

        total_folders += 1

    print("\n🎯 Complete")
    print(f"Folders processed: {total_folders}")
    print(f"Items updated: {total_items}")
    print("🧪 Dry run only." if Config.DRY_RUN else "✅ Applied.")


# ==========================================================
# ENTRY
# ==========================================================

if __name__ == "__main__":
    main()
