import os
import sys

# Set encoding for stdout
sys.stdout.reconfigure(encoding='utf-8')

cwd = os.getcwd()
print(f"CWD: {cwd}")

resume_dir = os.path.join(cwd, 'study', 'resume')
print(f"Target: {resume_dir}")

if os.path.exists(resume_dir):
    print("Directory exists.")
    files = os.listdir(resume_dir)
    print(f"Files count: {len(files)}")
    for f in files:
        print(f"  {repr(f)}")
else:
    print("Directory does NOT exist.")
