import re

# 1. Read first_app_code.py (the pure original)
with open("first_app_code.py", "r", encoding="utf-8") as f:
    orig = f.read()

# 2. Read update_data.py to extract GLOSSARY_DB (which has 349 terms)
with open("update_data.py", "r", encoding="utf-8") as f:
    upd = f.read()

# Extract GLOSSARY_DB from update_data.py
gloss_match = re.search(r"(GLOSSARY_DB = \{.*?\n\})", upd, re.DOTALL)
glossary_code = gloss_match.group(1) if gloss_match else ""

# 3. Read apply_30_events.py to extract HISTORY_DB (which has 30 items)
with open("apply_30_events.py", "r", encoding="utf-8") as f:
    apply_code = f.read()

hist_match = re.search(r"(HISTORY_DB = \[.*?\]\n)", apply_code, re.DOTALL)
history_code = hist_match.group(1) if hist_match else ""

# Now we replace the original DBs in first_app_code.py
# First find where they are in orig
# orig has GLOSSARY_DB = { ... }
orig = re.sub(r"GLOSSARY_DB = \{.*?\}\n", glossary_code + "\n", orig, flags=re.DOTALL)

# orig has HISTORY_DB = [ ... ]
orig = re.sub(r"HISTORY_DB = \[.*?\]\n", history_code + "\n", orig, flags=re.DOTALL)

# Write back to app.py
with open("app.py", "w", encoding="utf-8") as f:
    f.write(orig)

print("Combined successfully.")
