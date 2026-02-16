#!/usr/bin/env python3
"""
==================================+
| Hugging Face Space Entry Point  |
==================================+

This script clones a the main leaderboard space from github and then runs the application from it.
This architecture ensures git operations target the GitHub repo, not the HF Space.

Architecture:
- HF Space contains only this entry point
- Actual application code lives in GitHub (https://github.com/MALIBA-AI/bambara-asr-leaderboard)
- Git operations are patched to target the cloned GitHub repo
- File operations (like leaderboard.csv) happen in the GitHub repo directory
"""

import os
import subprocess
import sys
import re
from pathlib import Path


def mask_sensitive_info(text):
    if text is None:
        return text
    
    patterns = [
        (r'ghp_[a-zA-Z0-9]{36,}', 'ghp_***'),           
        (r'github_pat_[a-zA-Z0-9_]{82,}', 'github_pat_***'),  
        (r'hf_[a-zA-Z0-9]{20,}', 'hf_***'),             
        (r'://[^:@]+:[^:@]+@', '://***:***@'),          
    ]
    
    masked = text
    for pattern, replacement in patterns:
        masked = re.sub(pattern, replacement, masked)
    
    return masked


def run_command(cmd, check=True, cwd=None, capture_output=True):
    cmd_display = ' '.join(cmd) if isinstance(cmd, list) else cmd
    print(f"Running: {mask_sensitive_info(cmd_display)}")
    
    try:
        result = subprocess.run(
            cmd if isinstance(cmd, list) else cmd.split(),
            check=check,
            capture_output=capture_output,
            text=True,
            cwd=cwd
        )
        
        if result.stdout and capture_output:
            print(mask_sensitive_info(result.stdout))
        if result.stderr and capture_output:
            print(mask_sensitive_info(result.stderr), file=sys.stderr)
            
        return result
        
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        if e.stdout:
            print(f"stdout: {mask_sensitive_info(e.stdout)}")
        if e.stderr:
            print(f"stderr: {mask_sensitive_info(e.stderr)}")
        raise


def setup_github_repo(repo_dir, github_user, github_repo, github_token, github_email):
    if not repo_dir.exists():
        print(f" Cloning repository: {github_repo}")
        
        if github_token and github_token.strip():
            repo_url = f"https://{github_user}:{github_token}@github.com/{github_repo}.git"
        else:
            repo_url = f"https://github.com/{github_repo}.git"
        
        run_command(["git", "clone", repo_url, str(repo_dir)])
        
        run_command(["git", "config", "user.email", github_email], cwd=repo_dir)
        run_command(["git", "config", "user.name", github_user], cwd=repo_dir)
        
        if github_token and github_token.strip():
            remote_url = f"https://{github_user}:{github_token}@github.com/{github_repo}.git"
            run_command(["git", "remote", "set-url", "origin", remote_url], cwd=repo_dir)
            
        print("Repository cloned successfully")
        
    else:
        print("\n Repository exists, pulling latest changes...")
        result = run_command(["git", "pull"], cwd=repo_dir, check=False)
        
        if result.returncode == 0:
            print("Repository updated successfully")
        else:
            print("Git pull failed, continuing with existing version")
    
    return True


def setup_environment(app_dir, repo_dir):
    requirements_file = app_dir / "requirements.txt"
    if requirements_file.exists():
        print("\n Installing requirements...")
        run_command([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)])
        print("Requirements installed successfully")
    else:
        print("No requirements.txt found, skipping dependency installation")
    
    os.environ['LEADERBOARD_FILE'] = str(repo_dir / "leaderboard.csv")
    
    sys.path.insert(0, str(app_dir))


def patch_git_operations(repo_dir):
    import subprocess as orig_subprocess
    
    original_run = orig_subprocess.run
    
    def patched_run(cmd, *args, **kwargs):
        is_git_command = False
        if isinstance(cmd, list) and len(cmd) > 0 and cmd[0] == 'git':
            is_git_command = True
        elif isinstance(cmd, str) and cmd.strip().startswith('git'):
            is_git_command = True
        
        if is_git_command and 'cwd' not in kwargs:
            kwargs['cwd'] = str(repo_dir)
            print(f"[Git Patch] Redirecting git command to: {mask_sensitive_info(str(repo_dir))}")
        
        return original_run(cmd, *args, **kwargs)
    
    orig_subprocess.run = patched_run
    print("Git operations patched successfully")


def setup_and_run():
    GITHUB_USER  = os.getenv('GITHUB_USER', 'sudoping01')
    GITHUB_REPO  = os.getenv('GITHUB_REPO', 'MALIBA-AI/bambara-asr-leaderboard')
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
    GITHUB_EMAIL = os.getenv('GITHUB_EMAIL', 'sudoping01@gmail.com')
    
    repo_dir = Path("/tmp/github_repo")
    app_dir = repo_dir / "space"
    
    print("=" * 60)
    print(" HuggingFace Space - GitHub Integration Setup")
    print("=" * 60)
    print(f"Repository: {GITHUB_REPO}")
    print(f"Target directory: {repo_dir}")
    print("=" * 60)
    
    try:
        setup_github_repo(repo_dir, GITHUB_USER, GITHUB_REPO, GITHUB_TOKEN, GITHUB_EMAIL)
    except Exception as e:
        print(f"\n Failed to setup GitHub repository: {e}")
        sys.exit(1)
    
    if not app_dir.exists():
        print(f"\n Error: 'space' directory not found in {repo_dir}")
        print("Available directories:")
        for item in repo_dir.iterdir():
            print(f"  - {item.name}")
        print("\nPlease ensure your repository has a 'space' directory with the application code.")
        sys.exit(1)
    
    print(f" Application directory found: {app_dir}")
    
    os.chdir(app_dir)
    print(f" Working directory: {os.getcwd()}")
    
    try:
        setup_environment(app_dir, repo_dir)
    except Exception as e:
        print(f"\n Failed to setup environment: {e}")
        sys.exit(1)
    
    try:
        patch_git_operations(repo_dir)
    except Exception as e:
        print(f"\n Failed to patch git operations: {e}")
        print("Continuing anyway...")
    
    app_file = app_dir / "app.py"
    if not app_file.exists():
        print(f"\n Error: app.py not found in {app_dir}")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("   Starting Application")
    print("=" * 60 + "\n")
    
    try:
        with open(app_file) as f:
            exec(f.read(), {'__name__': '__main__'})
    except Exception as e:
        print(f"\n Application error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def main():
    try:
        setup_and_run()
    except KeyboardInterrupt:
        print("\n\n Application stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()