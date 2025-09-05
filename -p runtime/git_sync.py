import subprocess

def git_pull(repo_path="."):
    """
    Pull latest changes from the given repo.
    Safe wrapper: won't crash if git is missing or repo is clean.
    """
    try:
        result = subprocess.run(
            ["git", "-C", repo_path, "pull"],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0:
            print("[git_sync] Repo updated:", result.stdout.strip())
        else:
            print("[git_sync] Git error:", result.stderr.strip())
    except FileNotFoundError:
        print("[git_sync] Git not installed. Skipping sync.")
    except Exception as e:
        print("[git_sync] Unexpected error:", e)
import subprocess
import os

REPO_URL = "https://github.com/eriirfos-eng/genesis.git"
LOCAL_PATH = os.path.dirname(os.path.abspath(__file__))

def git_pull():
    try:
        # Check if already a git repo
        if not os.path.exists(os.path.join(LOCAL_PATH, ".git")):
            print("[git_sync] Cloning genesis repo...")
            subprocess.run(["git", "clone", REPO_URL, LOCAL_PATH], check=True)
        else:
            print("[git_sync] Pulling latest changes from genesis...")
            subprocess.run(["git", "-C", LOCAL_PATH, "pull"], check=True)
    except Exception as e:
        print(f"[git_sync] Git error: {e}")

