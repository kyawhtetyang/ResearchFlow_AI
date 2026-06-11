import os
import shutil

MASTER_FOLDER = r"/Users/kyawhtet/Documents/EDU/CS"
DUPLICATE_FOLDER = r"/Users/kyawhtet/Documents/EDU/CS_Duplicate"

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def process_v_folder(v_src, v_dst):
    """Copy only __install, keep all.txt, delete everything else."""
    install_src = os.path.join(v_src, "__install")
    keep_file = os.path.join(v_dst, "all.txt")

    ensure_dir(v_dst)

    if os.path.exists(install_src):
        temp_install = os.path.join(v_dst, "__install")
        shutil.copytree(install_src, temp_install)

        all_txt_path = os.path.join(temp_install, "all.txt")
        if os.path.exists(all_txt_path):
            shutil.move(all_txt_path, keep_file)

        shutil.rmtree(temp_install)

def find_and_process_v(src_root, dst_root):
    """Recursively find all v* folders and process them."""
    for entry in os.listdir(src_root):
        src_path = os.path.join(src_root, entry)
        dst_path = os.path.join(dst_root, entry)

        if os.path.isdir(src_path):
            if entry.startswith("v"):
                process_v_folder(src_path, dst_path)
            else:
                find_and_process_v(src_path, dst_path)

if __name__ == "__main__":
    ensure_dir(DUPLICATE_FOLDER)
    find_and_process_v(MASTER_FOLDER, DUPLICATE_FOLDER)
    print("All v* folders processed: only all.txt from __install preserved.")

