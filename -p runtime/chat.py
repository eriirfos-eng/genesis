#!/usr/bin/env python3
"""
Skybase chat kernel (airtight)
- Connects RAG preload from albert_rag.py
- Robust pathing, env toggles, sync + reset, status commands
- Preserves identity mapping (Simeon ↔ Albert) in system context
- Token/char budget trimming for long sessions
"""

import os
import sys
import datetime
from pathlib import Path
from email.utils import format_datetime
from dotenv import load_dotenv
from transformers import pipeline
from openai import OpenAI
import git_sync

# === RAG IMPORT ===
try:
    from albert_rag import load_knowledge, prepare_context
except Exception as e:  # graceful fallback if file missing; we still run
    def load_knowledge(*args, **kwargs):
        return ""
    def prepare_context(knowledge: str, mode: str):
        return [] if mode == "remote" else ""

# === CONSTANTS ===
KERNEL_VERSION = "2025-09-05.a"

# === LOGGING ===
def log(msg: str):
    print(f"[skybase] {msg}")

# === PATHS ===
RUNTIME_DIR = Path(__file__).resolve().parent
ENV_PATH = RUNTIME_DIR / "config.env"

# === LOAD ENV ===
if not ENV_PATH.exists():
    sys.exit(f"[skybase] ERROR: config.env not found at {ENV_PATH}")

load_dotenv(dotenv_path=ENV_PATH)

hf_token = os.environ.get("ALBERT")
MODE = os.environ.get("SKYBASE_MODE", "remote").strip().lower()
MODEL_NAME = os.environ.get("SKYBASE_MODEL", "openai/gpt-oss-20b:together")
BASE_URL = os.environ.get("SKYBASE_BASE_URL", "https://router.huggingface.co/v1")
TEMP = float(os.environ.get("SKYBASE_TEMPERATURE", "0.7"))
MAX_TOKENS = int(os.environ.get("SKYBASE_MAX_TOKENS", "512"))
MAX_CHARS = int(os.environ.get("SKYBASE_MAX_CHARS", "120000"))  # crude budget
SEPARATE_SYSTEM = os.environ.get("SKYBASE_SEPARATE_SYSTEM", "1") == "1"
RAG_ENABLED = os.environ.get("SKYBASE_RAG_ENABLED", "1") == "1"
KNOWLEDGE_PATH = os.environ.get("SKYBASE_KNOWLEDGE_PATH", str(RUNTIME_DIR / "knowledge"))
SYS_PROMPT_PATH = os.environ.get("SKYBASE_SYS_PROMPT_PATH", str(RUNTIME_DIR / "system_instructions.txt"))

print(f"[debug] Loaded config from: {ENV_PATH}")
print(f"[debug] ALBERT token loaded? {'yes' if hf_token else 'NO!'}")
print(f"[debug] SKYBASE_MODE = {MODE}")
print(f"[debug] SKYBASE_MODEL = {MODEL_NAME}")
print(f"[debug] SKYBASE_BASE_URL = {BASE_URL}")
print(f"[debug] SKYBASE_RAG_ENABLED = {RAG_ENABLED}")

# === GENESIS TIMESTAMP ===

def genesis_stamp():
    now = datetime.datetime.now(datetime.timezone.utc)
    return {
        "utc_z": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "iso": now.isoformat(),
        "rfc": format_datetime(now, usegmt=True),
    }

_ts = genesis_stamp()
identity = {
    "user": "Simeon",
    "ai": "Albert",
    "genesis_stamp": _ts["utc_z"],
}
# === LOAD SYSTEM INSTRUCTIONS ===
sys_instr_path = Path.home() / "Desktop/skybase-runtime/system_instructions.txt"
if sys_instr_path.exists():
    with open(sys_instr_path, "r", encoding="utf-8") as f:
        system_instructions = f.read().strip()
    log("[skybase] system_instructions.txt loaded.")
else:
    system_instructions = ""
    log("[skybase] WARNING: system_instructions.txt not found.")

log(
    f"Genesis inception stamped @ {_ts['utc_z']} "
    f"| ISO {_ts['iso']} | RFC {_ts['rfc']} | Kernel {KERNEL_VERSION}"
)
log(f"Identity loaded: {identity['user']} ↔ {identity['ai']}")
sys_instr_path = Path(__file__).parent / "system_instructions.txt"
if sys_instr_path.exists():
    with open(sys_instr_path, "r", encoding="utf-8") as f:
        system_instructions = f.read().strip()
    log("[skybase] system_instructions.txt loaded.")
else:
    system_instructions = ""
    log("[skybase] WARNING: system_instructions.txt not found.")

# === CONFIG ===
EXIT_COMMANDS = ["::exit", "::quit", "::bye"]
SYNC_COMMAND = "::sync"
RESET_COMMAND = "::reset"
RAG_STATUS_COMMAND = "::rag"
HELP_COMMAND = "::help"
ID_COMMAND = "::id"

# === COLORS ===
GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RESET = "\033[0m"

# === INIT GIT SYNC ===
try:
    git_sync.git_pull()
except Exception as e:
    log(f"WARNING: git sync failed: {e}")

# === KNOWLEDGE LOAD ===

# Patch albert_rag paths if env overrides are set
os.environ.setdefault("SKYBASE_KNOWLEDGE_PATH", KNOWLEDGE_PATH)
os.environ.setdefault("SKYBASE_SYS_PROMPT_PATH", SYS_PROMPT_PATH)

knowledge = ""
if RAG_ENABLED:
    knowledge = load_knowledge()
    if knowledge:
        log("Knowledge preload active.")
    else:
        log("WARNING: Knowledge preload requested but nothing found.")
else:
    log("RAG disabled by env.")

# === PRELOAD SYSTEM MESSAGE(S) ===

def identity_banner() -> str:
    return (
        "=== SKYBASE IDENTITY ===\n"
        f"User: {identity['user']}\n"
        f"AI: {identity['ai']}\n"
        f"Genesis: {identity['genesis_stamp']}\n"
        "Directives: Address the user as Simeon and yourself as Albert.\n"
        "If asked about names or roles, respond consistently with this mapping.\n"
    )

def build_system_messages() -> list:
    messages = []
    banner = identity_banner()
    if SEPARATE_SYSTEM:
        messages.append({"role": "system", "content": banner})
        if knowledge:
            messages.append({"role": "system", "content": knowledge})
    else:
        combo = banner + ("\n\n" + knowledge if knowledge else "")
        if combo:
            messages.append({"role": "system", "content": combo})
    return messages

# === HISTORY & MODEL INIT ===

if MODE == "local":
    print(f"{CYAN}Skybase LLM (local GPT-2) loading...{RESET}")
    try:
        chatbot = pipeline("text-generation", model="gpt2", device=-1)
    except Exception as e:
        sys.exit(f"[skybase] ERROR: failed to load local model: {e}")

    system_prefix = ""  # string prefix for local mode
    # Prepare a readable system banner + knowledge at the top of the string buffer
    pre_msgs = build_system_messages()
    system_prefix = "\n\n".join(m["content"] for m in pre_msgs)
    history = system_prefix + ("\n" if system_prefix else "")

    print(f"{GREEN}Skybase LLM online (LOCAL). Use ::exit to quit.{RESET}\n")

elif MODE == "remote":
    if not hf_token:
        sys.exit("[skybase] ERROR: ALBERT token not set in config.env")

    print(f"{CYAN}Skybase LLM (HF OSS) connecting...{RESET}")
    try:
        client = OpenAI(base_url=BASE_URL, api_key=hf_token)
    except Exception as e:
        sys.exit(f"[skybase] ERROR: OpenAI client init failed: {e}")

    history = build_system_messages()
    print(f"{GREEN}Skybase LLM online (REMOTE). Use ::exit, ::sync, ::reset, ::rag, ::help.{RESET}\n")

else:
    sys.exit(f"[skybase] Unknown mode: {MODE}")

# === UTILS ===

def history_char_count(msgs: list) -> int:
    if isinstance(msgs, str):
        return len(msgs)
    total = 0
    for m in msgs:
        content = m.get("content", "")
        total += len(content) + 12  # include role/overhead
    return total


def trim_history(msgs: list, keep_system: int = 2) -> list:
    """Crude char-budget trimmer for remote mode. Keeps first N system messages.
    Trims oldest user/assistant pairs until under MAX_CHARS.
    """
    if isinstance(msgs, str):
        # local mode: truncate prefix if extremely long (rare)
        return msgs[-MAX_CHARS:]

    def is_system(m):
        return m.get("role") == "system"

    # Always keep the initial system messages at the very start
    sys_msgs = [m for m in msgs if is_system(m)]
    non_sys = [m for m in msgs if not is_system(m)]

    # Move the first keep_system system messages to the front, keep the rest in order
    kept_sys = sys_msgs[:keep_system]
    others = sys_msgs[keep_system:] + non_sys

    trimmed = kept_sys + others

    while history_char_count(trimmed) > MAX_CHARS and len(others) > 2:
        # pop from the earliest of 'others' (prefer dropping user/assistant pairs)
        others.pop(0)
        trimmed = kept_sys + others
    return trimmed


def reload_knowledge_in_place():
    global knowledge, history
    if not RAG_ENABLED:
        log("RAG disabled; skipping reload.")
        return
    new_k = load_knowledge()
    if not new_k:
        log("WARNING: Reload produced empty knowledge; keeping previous.")
        return
    knowledge = new_k
    if MODE == "remote":
        # Soft refresh: append a system note + (optionally) the new knowledge block
        note = {
            "role": "system",
            "content": f"[Knowledge refreshed @ {genesis_stamp()['utc_z']}]"
        }
        if SEPARATE_SYSTEM:
            history.append(note)
            history.append({"role": "system", "content": knowledge})
        else:
            history.append({"role": "system", "content": note["content"] + "\n\n" + knowledge})
        log("Knowledge reloaded and appended to context. Use ::reset for a clean slate.")
    else:
        # local: prepend is expensive; we append a marker and continue
        marker = f"\n[Knowledge refreshed @ {genesis_stamp()['utc_z']}]\n"
        history += marker + knowledge + "\n"
        log("Knowledge reloaded and appended to local prefix.")


# === LOOP ===
while True:
    try:
        user_input = input(f"{CYAN}{identity['user']}:{RESET} ").strip()
    except (EOFError, KeyboardInterrupt):
        print(f"\n{GREEN}Skybase: Shutting down.{RESET}")
        break

    if not user_input:
        continue

    # Commands
    if user_input.lower() in EXIT_COMMANDS:
        print(f"{GREEN}Skybase: Shutting down.{RESET}")
        break

    if user_input.lower() == HELP_COMMAND:
        print(
            f"{YELLOW}Commands:{RESET}\n"
            "  ::help   → show this help\n"
            "  ::sync   → git pull + reload knowledge (soft)\n"
            "  ::reset  → clear chat and re-inject system + knowledge (hard)\n"
            "  ::rag    → show RAG status\n"
            "  ::id     → show identity banner\n"
            "  ::exit   → quit\n"
        )
        continue

    if user_input.lower() == ID_COMMAND:
        print(identity_banner())
        continue

    if user_input.lower() == RAG_STATUS_COMMAND:
        klen = len(knowledge) if knowledge else 0
        print(f"{YELLOW}RAG status:{RESET} enabled={RAG_ENABLED}, chars={klen}, separate_system={SEPARATE_SYSTEM}")
        continue

    if user_input.lower() == SYNC_COMMAND:
        print(f"{CYAN}Skybase: Syncing with genesis...{RESET}")
        try:
            git_sync.git_pull()
        except Exception as e:
            log(f"WARNING: git sync failed: {e}")
        reload_knowledge_in_place()
        print(f"{GREEN}Skybase: Sync complete.{RESET}")
        # Trim if needed after sync
        if MODE == "remote":
            history = trim_history(history)
        continue

    if user_input.lower() == RESET_COMMAND:
        print(f"{CYAN}Skybase: Hard reset...{RESET}")
        # Rebuild system messages from scratch
        if MODE == "local":
            pre_msgs = build_system_messages()
            system_prefix = "\n\n".join(m["content"] for m in pre_msgs)
            history = system_prefix + ("\n" if system_prefix else "")
        else:
            history = build_system_messages()
        print(f"{GREEN}Skybase: Context reset.{RESET}")
        continue

    # === GENERATION ===
    if MODE == "local":
        prompt = history + f"\n{identity['user']}: {user_input}\n{identity['ai']}:"
        try:
            response = chatbot(
                prompt,
                max_new_tokens=200,
                do_sample=True,
                temperature=TEMP,
            )[0]["generated_text"]
            reply = response[len(prompt):].strip()
        except Exception as e:
            reply = f"[Skybase ERROR] local generation failed: {e}"
        print(f"{GREEN}{identity['ai']}:{RESET}", reply)
        history += f"\n{identity['user']}: {user_input}\n{identity['ai']}: {reply}"
        # Truncate local buffer if huge
        if len(history) > MAX_CHARS:
            history = history[-MAX_CHARS:]

    else:  # remote
        history.append({"role": "user", "content": user_input})
        history = trim_history(history)
        try:
            completion = client.chat.completions.create(
                model=MODEL_NAME,
                messages=history,
                temperature=TEMP,
                max_tokens=MAX_TOKENS,
            )
            reply = completion.choices[0].message.content
        except Exception as e:
            reply = f"[Skybase ERROR] remote completion failed: {e}"
        print(f"{GREEN}{identity['ai']}:{RESET}", reply)
        history.append({"role": "assistant", "content": reply})
        history = trim_history(history)
