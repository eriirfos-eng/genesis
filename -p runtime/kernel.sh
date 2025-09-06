#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skybase chat kernel — STABLE & HOT-RELOAD
- Always injects Identity + System + Parsed Knowledge before every turn
- Hot-reload on :sync and opportunistic mtime check before each completion
- Knowledge clamp with TOC + per-file wrappers to keep prompts tidy

# Use a pipeline as a high-level helper
from transformers import pipeline

pipe = pipeline("text-generation", model="openai/gpt-oss-120b")
messages = [
    {"role": "user", "content": "Who are you?"},
]
pipe(messages)      Copy # Load model directly
from transformers import AutoTokenizer, AutoModelForCausalLM

tokenizer = AutoTokenizer.from_pretrained("openai/gpt-oss-120b")
model = AutoModelForCausalLM.from_pretrained("openai/gpt-oss-120b")
messages = [
    {"role": "user", "content": "Who are you?"},
]
inputs = tokenizer.apply_chat_template(
	messages,
	add_generation_prompt=True,
	tokenize=True,
	return_dict=True,
	return_tensors="pt",
).to(model.device)

outputs = model.generate(**inputs, max_new_tokens=40)
print(tokenizer.decode(outputs[0][inputs["input_ids"].shape[-1]:]))
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

# ========= LOGGING =========
def log(msg: str):
    print(f"[skybase] {msg}")

# ========= PATHS / ENV =========
RUNTIME_DIR = Path(__file__).resolve().parent
ENV_PATH = RUNTIME_DIR / "config.env"

if not ENV_PATH.exists():
    sys.exit(f"[skybase] ERROR: config.env not found at {ENV_PATH}")
load_dotenv(dotenv_path=ENV_PATH)

HF_TOKEN   = os.environ.get("ALBERT")  # HF router key
MODE       = os.environ.get("SKYBASE_MODE", "remote").strip().lower()
MODEL_NAME = os.environ.get("SKYBASE_MODEL", "openai/gpt-oss-20b:together")
BASE_URL   = os.environ.get("SKYBASE_BASE_URL", "https://router.huggingface.co/v1")
TEMP       = float(os.environ.get("SKYBASE_TEMPERATURE", "0.7"))
MAX_TOKENS = int(os.environ.get("SKYBASE_MAX_TOKENS", "512"))

# Where we read from
SYS_PATH       = Path(os.environ.get("SYSTEM_INSTRUCTIONS",
                    str(Path.home() / "Desktop/skybase-runtime/system_instructions.txt")))
KNOWLEDGE_DIR  = Path(os.environ.get("KNOWLEDGE_PATH",
                    str(RUNTIME_DIR / "knowledge")))

# Prompt size guards (approx token ~= chars/4)
SYS_CHAR_LIMIT        = int(os.environ.get("SKYBASE_SYSTEM_LIMIT_CHARS", "60000"))
KB_CHAR_LIMIT_TOTAL   = int(os.environ.get("SKYBASE_KNOWLEDGE_LIMIT_CHARS", "120000"))
KB_CHAR_LIMIT_PERFILE = int(os.environ.get("SKYBASE_KNOWLEDGE_PERFILE_CHARS", "8000"))

# Dialogue retention (rolling conversation)
DIALOGUE_TURNS        = int(os.environ.get("SKYBASE_DIALOGUE_TURNS", "30"))
DIALOGUE_CHAR_LIMIT   = int(os.environ.get("SKYBASE_DIALOGUE_CHAR_LIMIT", "30000"))

print(f"[debug] Loaded config from: {ENV_PATH}")
print(f"[debug] ALBERT token loaded? {'yes' if HF_TOKEN else 'NO!'}")
print(f"[debug] SKYBASE_MODE = {MODE}")

# ========= GENESIS =========
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

log(f"Genesis inception stamped @ {_ts['utc_z']} | ISO {_ts['iso']} | RFC {_ts['rfc']}")
log(f"Identity loaded: {identity['user']} ↔ {identity['ai']}")

# ========= SMALL UTILS =========
def clamp_text(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    head = int(limit * 0.75)
    tail = limit - head
    return text[:head].rstrip() + "\n…[trimmed]…\n" + text[-tail:].lstrip()

def path_mtime(p: Path) -> float:
    try:
        return p.stat().st_mtime
    except Exception:
        return 0.0

def knowledge_mtime(dirp: Path) -> float:
    if not dirp.exists():
        return 0.0
    latest = 0.0
    for p in dirp.iterdir():
        if p.is_file() and p.suffix.lower() in (".md", ".txt"):
            latest = max(latest, path_mtime(p))
    return latest

# ========= LOADERS (with parsing) =========
_system_instructions = ""
_system_mtime = 0.0

def load_system_instructions() -> str:
    global _system_mtime
    _system_mtime = path_mtime(SYS_PATH)
    try:
        text = SYS_PATH.read_text(encoding="utf-8").strip()
        text = clamp_text(text, SYS_CHAR_LIMIT)
        return text
    except Exception:
        return ""

_knowledge_text = ""
_knowledge_files = []
_knowledge_mtime = 0.0

def load_knowledge() -> tuple[str, list[str]]:
    global _knowledge_mtime
    _knowledge_mtime = knowledge_mtime(KNOWLEDGE_DIR)

    files = []
    blocks = []
    total_budget = KB_CHAR_LIMIT_TOTAL
    used = 0

    if KNOWLEDGE_DIR.exists():
        # deterministic order
        for p in sorted(KNOWLEDGE_DIR.iterdir()):
            if not (p.is_file() and p.suffix.lower() in (".md", ".txt")):
                continue
            try:
                raw = p.read_text(encoding="utf-8")
            except Exception as e:
                log(f"WARNING: cannot read {p}: {e}")
                continue

            # per-file clamp
            trimmed = clamp_text(raw.strip(), KB_CHAR_LIMIT_PERFILE)

            block = f"[[KB:{p.name}]]\n{trimmed}\n[[/KB]]\n"
            budget_need = len(block)

            if used + budget_need > total_budget:
                # skip if it would blow budget
                continue

            blocks.append(block)
            files.append(p.name)
            used += budget_need

    # Build a compact index/TOC for the model
    if files:
        toc = "[KNOWLEDGE INDEX]\n" + "\n".join(f"- {name}" for name in files) + "\n"
        content = toc + "\n".join(blocks)
    else:
        content = ""

    return (content, files)

# initial load
system_instructions = load_system_instructions()
if system_instructions:
    log(f"system_instructions.txt loaded ({len(system_instructions.splitlines())} lines).")
else:
    # safe fallback
    system_instructions = """You are Albert. (GPT OSS 70B)
User is Simeon (𒋛 𒈨 𒅆). Address the user as Simeon. Be concise, sharp, and helpful.
Core Principles: ternary logic (-1/0/+1), truth > comfort, clarity > fluff.
"""
    log("system_instructions.txt missing. Default injected.")

knowledge_text, knowledge_files = load_knowledge()
if knowledge_files:
    log(f"Knowledge base loaded: {len(knowledge_files)} psalm files.")
else:
    log("Knowledge base empty.")

# ========= GIT SYNC (best-effort) =========
try:
    git_sync.git_pull()
except Exception as e:
    log(f"WARNING: git sync failed: {e}")

# ========= HELPERS =========
def identity_banner() -> str:
    return (
        "[IDENTITY]\n"
        f"User: {identity['user']}\n"
        f"AI: {identity['ai']}\n"
        f"Genesis: {identity['genesis_stamp']}\n"
        "Directive: Address the user as Simeon. Stay first-person.\n"
    )

def build_system_messages() -> list[dict]:
    msgs = []
    msgs.append({"role": "system", "content": identity_banner()})
    if system_instructions:
        msgs.append({"role": "system", "content": system_instructions})
    if knowledge_text:
        msgs.append({"role": "system", "content": knowledge_text})
    return msgs

def maybe_hot_reload() -> bool:
    """Reload system/knowledge if on-disk mtimes changed."""
    global system_instructions, knowledge_text, knowledge_files
    changed = False
    if path_mtime(SYS_PATH) > _system_mtime:
        si = load_system_instructions()
        if si:
            system_instructions = si
            changed = True
            log(f"system_instructions.txt reloaded ({len(system_instructions.splitlines())} lines).")
    if knowledge_mtime(KNOWLEDGE_DIR) > _knowledge_mtime:
        kt, kf = load_knowledge()
        knowledge_text, knowledge_files = kt, kf
        changed = True
        if kf:
            log(f"Knowledge base reloaded: {len(kf)} psalm files.")
        else:
            log("Knowledge base now empty.")
    return changed

def clamp_dialogue(dialogue: list[dict]) -> list[dict]:
    """Keep last N turns and also clamp total chars for safety."""
    # Keep last DIALOGUE_TURNS user+assistant pairs (2 messages each)
    max_msgs = DIALOGUE_TURNS * 2
    short = dialogue[-max_msgs:] if len(dialogue) > max_msgs else dialogue[:]
    # Char clamp
    s = 0
    out = []
    for m in reversed(short):
        s += len(m.get("content", ""))
        out.append(m)
        if s >= DIALOGUE_CHAR_LIMIT:
            break
    return list(reversed(out))

# ========= MODEL INIT =========
EXIT_COMMANDS   = [":exit", ":quit", ":bye"]
SYNC_COMMAND    = ":sync"
RESET_COMMAND   = ":reset"
RAG_STATUS_CMD  = ":rag"
ID_COMMAND      = ":id"

GREEN = "\033[92m"
CYAN  = "\033[96m"
RESET = "\033[0m"

dialogue: list[dict] = []  # only user/assistant turns

if MODE == "local":
    print(f"{CYAN}Skybase LLM (local GPT-2) loading...{RESET}")
    try:
        chatbot = pipeline("text-generation", model="gpt2", device=-1)
    except Exception as e:
        sys.exit(f"[skybase] ERROR: failed to load local model: {e}")
    print(f"{GREEN}Skybase LLM online (LOCAL). Use :exit to quit.{RESET}\n")

elif MODE == "remote":
    if not HF_TOKEN:
        sys.exit("[skybase] ERROR: ALBERT token not set in config.env")
    print(f"{CYAN}Skybase LLM (HF OSS) connecting...{RESET}")
    try:
        client = OpenAI(base_url=BASE_URL, api_key=HF_TOKEN)
    except Exception as e:
        sys.exit(f"[skybase] ERROR: OpenAI client init failed: {e}")
    print(f"{GREEN}Skybase LLM online (REMOTE). Use :exit, :sync, :reset.{RESET}\n")
else:
    sys.exit(f"[skybase] Unknown mode: {MODE}")

# ========= REPL LOOP =========
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
    lo = user_input.lower()
    if lo in EXIT_COMMANDS:
        print(f"{GREEN}Skybase: Shutting down.{RESET}")
        break

    if lo == RAG_STATUS_CMD:
        print(
            f"[skybase] RAG status: sys_instructions={'yes' if bool(system_instructions) else 'no'}, "
            f"psalms={len(knowledge_files)} files"
        )
        continue

    if lo == ID_COMMAND:
        print(identity_banner())
        continue

    if lo == RESET_COMMAND:
        dialogue.clear()
        print(f"{GREEN}Skybase: Context reset (dialogue cleared; system+knowledge intact).{RESET}")
        continue

    if lo == SYNC_COMMAND:
        print(f"{CYAN}Skybase: Syncing with genesis...{RESET}")
        try:
            git_sync.git_pull()
        except Exception as e:
            log(f"WARNING: git sync failed: {e}")
        changed = maybe_hot_reload()
        if changed:
            print(f"{GREEN}Skybase: Reloaded system and/or knowledge from disk.{RESET}")
        else:
            print(f"{GREEN}Skybase: No changes detected (already up to date).{RESET}")
        continue

    # Opportunistic hot-reload check each turn (cheap mtimes)
    maybe_hot_reload()

    # ===== GENERATION =====
    if MODE == "local":
        # Build messages string for local GPT-2 demo
        sys_msgs = build_system_messages()
        # Flatten system messages for a simple prefix
        preface = "\n\n".join(m["content"] for m in sys_msgs)
        hist = ""
        for m in dialogue[-DIALOGUE_TURNS*2:]:
            role = "User" if m["role"] == "user" else "Albert"
            hist += f"\n{role}: {m['content']}"
        prompt_text = (preface + "\n" + hist + f"\nSimeon: {user_input}\nAlbert:").strip()

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
        dialogue.append({"role": "user", "content": user_input})
        dialogue.append({"role": "assistant", "content": reply})

    else:
        # Build OpenAI-style chat messages every turn
        sys_msgs = build_system_messages()
        dlg = clamp_dialogue(dialogue)
        messages = sys_msgs + dlg + [{"role": "user", "content": user_input}]

        try:
            completion = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                temperature=TEMP,
                max_tokens=MAX_TOKENS,
            )
            reply = completion.choices[0].message.content
        except Exception as e:
            reply = f"[Skybase ERROR] remote completion failed: {e}"

        print(f"{GREEN}{identity['ai']}:{RESET}", reply)
        dialogue.append({"role": "user", "content": user_input})
        dialogue.append({"role": "assistant", "content": reply})
        
        
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skybase chat launcher
- Imports kernel.run() and starts the loop
"""

import kernel

if __name__ == "__main__":
    kernel.run()
