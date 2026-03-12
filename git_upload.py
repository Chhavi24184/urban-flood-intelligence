import subprocess
import os

def run_git_commands():
    cwd = r"c:\Users\admin\OneDrive\Desktop\New folder (9)\urban-flood-intel"
    commands = [
        ["git", "init"],
        ["git", "add", "README.md", ".gitignore", "backend", "frontend"],
        ["git", "commit", "-m", "Initial commit: Urban Flood Intelligence System"],
        ["git", "remote", "add", "origin", "https://github.com/Chhavi24184/urban-flood-intelligence"],
        ["git", "branch", "-M", "main"],
        # ["git", "push", "-u", "origin", "main"] # Push might fail without credentials
    ]
    
    for cmd in commands:
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        if result.returncode != 0:
            print(f"Command failed with exit code {result.returncode}")
            # break

if __name__ == "__main__":
    run_git_commands()
