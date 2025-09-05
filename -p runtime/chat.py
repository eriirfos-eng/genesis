#!/usr/bin/env python3
from albert_rag import load_knowledge, prepare_context
import os
import sys
import datetime
from pathlib import Path
from email.utils import format_datetime
from dotenv import load_dotenv
from transformers import pipeline
from openai import OpenAI
import git_sync

# === LOGGING ===
def log(msg: str):
    print(f"[skybase] {msg}")

# === LOAD ENV ===
env_path = Path(__file__).parent / "config.env"
if not env_path.exists():
    sys.exit(f"[skybase] ERROR: config.env not found at {env_path}")

load_dotenv(dotenv_path=env_path)

hf_token = os.environ.get("ALBERT")
MODE = os.environ.get("SKYBASE_MODE", "remote")

print(f"[debug] Loaded config from: {env_path}")
print(f"[debug] ALBERT token loaded? {'yes' if hf_token else 'NO!'}")
print(f"[debug] SKYBASE_MODE = {MODE}")

# === GENESIS TIMESTAMP ===
def genesis_stamp():
    now = datetime.datetime.now(datetime.timezone.utc)
    return {
        "utc_z": now.strftime("%Y-%m-%dT%H:%M:%SZ"),  # 2025-09-05T15:55:22Z
        "iso": now.isoformat(),                       # 2025-09-05T15:55:22+00:00
        "rfc": format_datetime(now, usegmt=True),     # Fri, 05 Sep 2025 15:55:22 GMT
    }

_ts = genesis_stamp()
identity = {
    "user": "Simeon",
    "ai": "Albert",
    "genesis_stamp": _ts["utc_z"],
}

log(
    f"Genesis inception stamped @ {_ts['utc_z']} "
    f"| ISO {_ts['iso']} | RFC {_ts['rfc']}"
)
log(f"Identity loaded: {identity['user']} ↔ {identity['ai']}")

# === CONFIG ===
EXIT_COMMANDS = ["::exit", "::quit", "::bye"]
SYNC_COMMAND = "::sync"

# === COLORS ===
GREEN = "\033[92m"
CYAN = "\033[96m"
RESET = "\033[0m"
knowledge = load_knowledge()

if MODE == "local":
    history = prepare_context(knowledge, "local")
    ...
elif MODE == "remote":
    history = prepare_context(knowledge, "remote")
    ...

# === INIT GIT SYNC ===
git_sync.git_pull()
# === KNOWLEDGE / RAG LOAD ===
def load_knowledge(base_dir="knowledge"):
    """
    Loads psalms + system_instructions.txt into a dict.
    """
    kb = {}
    base = Path(__file__).parent / base_dir

    # load system instructions
    sys_file = Path(__file__).parent / "system_instructions.txt"
    if sys_file.exists():
        kb["system_instructions"] = sys_file.read_text(encoding="utf-8")
        log("system_instructions.txt loaded.")
    else:
        log("WARNING: system_instructions.txt not found.")

    # load knowledge folder
    if base.exists():
        for f in base.rglob("*.md"):
            kb[f.stem] = f.read_text(encoding="utf-8")
        log(f"Knowledge base loaded: {len(kb)-1} psalm files.")
    else:
        log("WARNING: knowledge folder not found.")

    return kb

knowledge_base = load_knowledge()


# === INIT MODEL ===
if MODE == "local":
    print(f"{CYAN}Skybase LLM (local GPT-2) loading...{RESET}")
    chatbot = pipeline("text-generation", model="gpt2", device=-1)
    history = ""
    print(f"{GREEN}Skybase LLM online (LOCAL). Use ::exit to quit.{RESET}\n")

elif MODE == "remote":
    if not hf_token:
        sys.exit("[skybase] ERROR: ALBERT token not set in config.env")
    print(f"{CYAN}Skybase LLM (HF OSS) connecting...{RESET}")
    client = OpenAI(
        base_url="https://router.huggingface.co/v1",
        api_key=hf_token
    )
    history = []
    print(f"{GREEN}Skybase LLM online (REMOTE). Use ::exit or ::sync.{RESET}\n")

else:
    sys.exit(f"[skybase] Unknown mode: {MODE}")

# === LOOP ===
while True:
    try:
        user_input = input(f"{CYAN}{identity['user']}:{RESET} ").strip()
    except (EOFError, KeyboardInterrupt):
        print(f"\n{GREEN}Skybase: Shutting down.{RESET}")
        break

    if not user_input:
        continue

    if user_input.lower() in EXIT_COMMANDS:
        print(f"{GREEN}Skybase: Shutting down.{RESET}")
        break

    if user_input.lower() == SYNC_COMMAND:
        print(f"{CYAN}Skybase: Syncing with genesis...{RESET}")
        git_sync.git_pull()
        print(f"{GREEN}Skybase: Sync complete.{RESET}")
        continue

    if MODE == "local":
        prompt = history + f"\n{identity['user']}: {user_input}\n{identity['ai']}:"
        response = chatbot(
            prompt,
            max_new_tokens=150,
            do_sample=True,
            temperature=0.8
        )[0]["generated_text"]
        reply = response[len(prompt):].strip()
        print(f"{GREEN}{identity['ai']}:{RESET}", reply)
        history += f"\n{identity['user']}: {user_input}\n{identity['ai']}: {reply}"

    else:  # remote
        history.append({"role": "user", "content": user_input})
        try:
            completion = client.chat.completions.create(
                model="openai/gpt-oss-20b:together",
                messages=history,
            )
            reply = completion.choices[0].message.content
        except Exception as e:
            reply = f"[Skybase ERROR] {e}"

        print(f"{GREEN}{identity['ai']}:{RESET}", reply)
        history.append({"role": "assistant", "content": reply})
