import re

target_file = r'c:\Python\MathProject_AST_Research\core\code_generator.py'
source_file = r'c:\Python\MathProject_AST_Research\temp\new_auto_gen.py'

with open(target_file, 'r', encoding='utf-8') as f:
    target_content = f.read()

with open(source_file, 'r', encoding='utf-8') as f:
    new_func_content = f.read()

# Locate the start of auto_generate_skill_code
# Using a simpler string search if possible, or regex
pattern = r'def auto_generate_skill_code\(skill_id, queue=None\):'
match = re.search(pattern, target_content)

if match:
    start_idx = match.start()
    # Assume it matches until the end of the file since it's the last function
    # We will keep content up to start_idx and append new content
    final_content = target_content[:start_idx] + new_func_content + "\n"
    
    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(final_content)
    print("Successfully updated code_generator.py")
else:
    print("Could not find auto_generate_skill_code function")
