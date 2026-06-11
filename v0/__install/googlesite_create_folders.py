import os

base_path = os.path.dirname(os.path.abspath(__file__))

# ==========================================================
# Google Site – Knowledge Structure
# ==========================================================

folders_text = """
World History
Myanmar History
Anthropology
Political Science
Earth Science
Geography
Religion History
Business Overview
Physics
Chemistry
Art
Literature
Biology
Microbiology
Business Biography
Local Business Biography
Mathematics
Economics
"""

folders = [line.strip() for line in folders_text.splitlines() if line.strip()]

for folder in folders:
    os.makedirs(os.path.join(base_path, folder), exist_ok=True)
    print(f"Created: {folder}")
