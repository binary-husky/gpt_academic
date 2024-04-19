import os
import json
import re

# Define regular expression patterns
pattern = r'i18n\((\"{3}.*?\"{3}|\".*?\")\)'

# Load the .py file
with open('ChuanhuChatbot.py', 'r', encoding='utf-8') as f:
    contents = f.read()

# Load the .py files in the modules folder
for filename in os.listdir("modules"):
    if filename.endswith(".py"):
        with open(os.path.join("modules", filename), "r", encoding="utf-8") as f:
            contents += f.read()

# Matching with regular expressions
matches = re.findall(pattern, contents, re.DOTALL)

# Convert to key/value pairs
data = {match.strip('()"'): '' for match in matches}

# Save as a JSON file
with open('labels.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)