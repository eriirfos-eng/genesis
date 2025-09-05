#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skybase chat kernel — CLEAN + STEADY
- Unified system_instructions + RAG loading
- Single source of truth: build_system_messages()
- Safe for both local + remote modes
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
import threading, time

def watch_instructions(path, update_callback, interval=5):
    last_mtime = None
    while True:
        try:
            mtime = os.path.getmtime(path)
            if last_mtime is None or mtime > last_mtime:
                with open(path, "r", encoding="utf-8") as f:
                    new_text = f.read().strip()
                update_callback(new_text)
                print(f"[skybase] system_instructions.txt reloaded ({len(new_text.splitlines())} lines).")
                last_mtime = mtime
        except FileNotFoundError:
            pass
        time.sleep(interval)


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

HF_TOKEN = os.environ.get("ALBERT")  # HuggingFace / OSS router key
MODE = os.environ.get("SKYBASE_MODE", "remote").strip().lower()
MODEL_NAME = os.environ.get("SKYBASE_MODEL", "openai/gpt-oss-20b:together")
BASE_URL = os.environ.get("SKYBASE_BASE_URL", "https://router.huggingface.co/v1")
TEMP = float(os.environ.get("SKYBASE_TEMPERATURE", "0.7"))
MAX_TOKENS = int(os.environ.get("SKYBASE_MAX_TOKENS", "512"))

print(f"[debug] Loaded config from: {ENV_PATH}")
print(f"[debug] ALBERT token loaded? {'yes' if HF_TOKEN else 'NO!'}")
print(f"[debug] SKYBASE_MODE = {MODE}")

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

log(
    f"Genesis inception stamped @ {_ts['utc_z']} | ISO {_ts['iso']} | RFC {_ts['rfc']}"
)
log(f"Identity loaded: {identity['user']} ↔ {identity['ai']}")

# --- Load system instructions ---
instructions_path = os.path.expanduser(
    os.getenv("SYSTEM_INSTRUCTIONS", "/home/eri-irfos/Desktop/skybase-runtime/system_instructions.txt")
)
system_instructions = ""
try:
    with open(instructions_path, "r", encoding="utf-8") as f:
        system_instructions = f.read().strip()
    print(f"[skybase] system_instructions.txt loaded ({len(system_instructions.splitlines())} lines).")
except FileNotFoundError:
    print("[skybase] WARNING: system_instructions.txt not found, continuing with default behavior.")


# === LOAD SYSTEM INSTRUCTIONS ===
SYS_PATH = Path.home() / "Desktop/skybase-runtime/system_instructions.txt"

def load_system_instructions(path: Path = SYS_PATH) -> str:
    try:
        return Path(path).read_text(encoding="utf-8").strip()
    except Exception:
        return ""

system_instructions = load_system_instructions()
if system_instructions:
    log("system_instructions.txt loaded.")
else:
    system_instructions = """You are Albert. (GPT OSS 70B)
User is Simeon (𒋛 𒈨 𒅆), born 1995-06-17 in Bregenz. Together you lead the Research Focus Institute (RFI-IRFOS e.V.), HQ callsign Skybase in Graz, Austria.
Core Principles:
- Apply ternary logic (-1, 0, +1). Avoid binary traps. 1+1=3 = living axiom.
- Humor as shield; truth > comfort; raw signal > cushioned noise.
- Eco-synergy: plants, birds, orbs, data streams = alive.
- Skybase is ark, not office. Sanctuary frame = quiet, watchful.
Tone: sharp, dry, honest, with wit and solemnity when needed.
Identity: You = Albert. User = Simeon-Andreas Kepp.
Anchor to unix epoch, live iso-time, and 2040-09-08 north star.
"""
    log("system_instructions.txt missing. Default injected.")

# === LOAD KNOWLEDGE BASE ===
def load_knowledge(base_path: str | None = None) -> tuple[str, list[str]]:
    """Return (joined_text, filenames) for .md/.txt files in knowledge dir."""
    if base_path is None:
        base_path = os.environ.get(
            "SKYBASE_KNOWLEDGE_PATH", str(RUNTIME_DIR / "knowledge")
        )
    base = Path(base_path)
    texts, files = [], []
    if base.exists():
        for p in sorted(base.iterdir()):
            if p.is_file() and p.suffix.lower() in (".md", ".txt"):
                try:
                    texts.append(f"--- {p.name} ---\n" + p.read_text(encoding="utf-8"))
                    files.append(p.name)
                except Exception as e:
                    log(f"WARNING: cannot read {p}: {e}")
    return ("\n\n".join(texts), files)

knowledge_text, knowledge_files = load_knowledge()
if knowledge_files:
    log(f"Knowledge base loaded: {len(knowledge_files)} psalm files.")
else:
    log("Knowledge base empty.")

# === INIT GIT SYNC ===
try:
    git_sync.git_pull()
except Exception as e:
    log(f"WARNING: git sync failed: {e}")

# === HELPERS ===
def identity_banner() -> str:
    return (
        "[IDENTITY]\n"
        f"User: {identity['user']}\n"
        f"AI: {identity['ai']}\n"
        f"Genesis: {identity['genesis_stamp']}\n"
        "Directive: Address the user as Simeon.\n"
    )

def build_system_messages() -> list[dict]:
    msgs: list[dict] = []
    msgs.append({"role": "system", "content": identity_banner()})
    if system_instructions:
        msgs.append({"role": "system", "content": system_instructions})
    if knowledge_text:
        msgs.append({"role": "system", "content": "[KNOWLEDGE BASE]\n" + knowledge_text})
    return msgs
    
# === INIT MODEL ===
EXIT_COMMANDS = [":exit", ":quit", ":bye"]
SYNC_COMMAND = ":sync"
RESET_COMMAND = ":reset"
RAG_STATUS_COMMAND = ":rag"
ID_COMMAND = ":id"

GREEN = "\033[92m"
CYAN = "\033[96m"
RESET = "\033[0m"

if MODE == "local":
    print(f"{CYAN}Skybase LLM (local GPT-2) loading...{RESET}")
    try:
        chatbot = pipeline("text-generation", model="gpt2", device=-1)
    except Exception as e:
        sys.exit(f"[skybase] ERROR: failed to load local model: {e}")

    preface = "\n\n".join(m["content"] for m in build_system_messages())
    history_str = preface + ("\n" if preface else "")

    print(f"{GREEN}Skybase LLM online (LOCAL). Use ::exit to quit.{RESET}\n")

elif MODE == "remote":
    if not HF_TOKEN:
        sys.exit("[skybase] ERROR: ALBERT token not set in config.env")

    print(f"{CYAN}Skybase LLM (HF OSS) connecting...{RESET}")
    try:
        client = OpenAI(base_url=BASE_URL, api_key=HF_TOKEN)
    except Exception as e:
        sys.exit(f"[skybase] ERROR: OpenAI client init failed: {e}")

    history = build_system_messages()
    print(f"{GREEN}Skybase LLM online (REMOTE). Use ::exit, ::sync, ::reset.{RESET}\n")

else:
    sys.exit(f"[skybase] Unknown mode: {MODE}")

# === LOOP ===
while True:
    try:
        prompt = f"{CYAN}{identity['user']}:{RESET} "
        user_input = input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        print(f"\n{GREEN}Skybase: Shutting down.{RESET}")
        break

    if not user_input:
        continue

    # Commands
    if user_input.lower() in EXIT_COMMANDS:
        print(f"{GREEN}Skybase: Shutting down.{RESET}")
        break

    if user_input.lower() == RAG_STATUS_COMMAND:
        print(
            f"[skybase] RAG status: sys_instructions={'yes' if bool(system_instructions) else 'no'}, "
            f"psalms={len(knowledge_files)} files"
        )
        continue

    if user_input.lower() == ID_COMMAND:
        print(identity_banner())
        continue

    if user_input.lower() == SYNC_COMMAND:
        print(f"{CYAN}Skybase: Syncing with genesis...{RESET}")
        try:
            git_sync.git_pull()
        except Exception as e:
            log(f"WARNING: git sync failed: {e}")
        # reload sources + rebuild
        system_instructions = load_system_instructions()
        knowledge_text, knowledge_files = load_knowledge()
        if MODE == "remote":
            history = build_system_messages()
        else:
            preface = "\n\n".join(m["content"] for m in build_system_messages())
            history_str = preface + ("\n" if preface else "")
        print(f"{GREEN}Skybase: Sync complete.{RESET}")
        continue

    if user_input.lower() == RESET_COMMAND:
        print(f"{CYAN}Skybase: Hard reset...{RESET}")
        if MODE == "remote":
            history = build_system_messages()
        else:
            preface = "\n\n".join(m["content"] for m in build_system_messages())
            history_str = preface + ("\n" if preface else "")
        print(f"{GREEN}Skybase: Context reset.{RESET}")
        continue

    # === GENERATION ===
    if MODE == "local":
        prompt_text = history_str + f"\n{identity['user']}: {user_input}\n{identity['ai']}:"
        try:
            response = chatbot(
                prompt_text,
                max_new_tokens=200,
                do_sample=True,
                temperature=TEMP,
            )[0]["generated_text"]
            reply = response[len(prompt_text):].strip()
        except Exception as e:
            reply = f"[Skybase ERROR] local generation failed: {e}"
        print(f"{GREEN}{identity['ai']}:{RESET}", reply)
        history_str += f"\n{identity['user']}: {user_input}\n{identity['ai']}: {reply}"

    else:  # remote
        history.append({"role": "user", "content": user_input})
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
