from dotenv import load_dotenv
load_dotenv("config.env")

import os
import sys
from transformers import pipeline
from openai import OpenAI
import git_sync

# Sync repo at startup
git_sync.git_pull()

# === CONFIG ===
EXIT_COMMANDS = ["::exit", "::quit", "::bye"]

MODE = os.environ.get("SKYBASE_MODE", "remote")  # default: remote
hf_token = os.environ.get("HF_TOKEN"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)

# === COLORS ===
GREEN = "\033[92m"
CYAN = "\033[96m"
RESET = "\033[0m"

# === INIT ===
if MODE == "local":
    print(f"{CYAN}Skybase LLM (local GPT-2) loading...{RESET}")
    chatbot = pipeline("text-generation", model="gpt2", device=-1)
    history = ""
    print(f"{GREEN}Skybase LLM online (LOCAL). Use ::exit to quit.{RESET}\n")

elif MODE == "remote":
    if not hf_token:
        sys.exit("ERROR: HF_TOKEN not set. Add it to config.env or export it.")
    print(f"{CYAN}Skybase LLM (HF OSS) connecting...{RESET}")
    client = OpenAI(
        base_url="https://router.huggingface.co/v1",
        api_key=hf_token
    )
    history = []
    print(f"{GREEN}Skybase LLM online (REMOTE). Use ::exit to quit.{RESET}\n")

else:
    sys.exit(f"Unknown mode: {MODE}")


# === LOOP ===
while True:
    try:
        user_input = input(f"{CYAN}You:{RESET} ").strip()
    except (EOFError, KeyboardInterrupt):
        print(f"\n{GREEN}Skybase: Shutting down.{RESET}")
        break

    if user_input.lower() in EXIT_COMMANDS:
        print(f"{GREEN}Skybase: Shutting down.{RESET}")
        break

    if MODE == "local":
        # prepend history for context
        prompt = history + f"\nYou: {user_input}\nSkybase:"
        response = chatbot(
            prompt,
            max_new_tokens=150,
            do_sample=True,
            temperature=0.8
        )[0]["generated_text"]
        reply = response[len(prompt):].strip()
        print(f"{GREEN}Skybase:{RESET}", reply)
        history += f"\nYou: {user_input}\nSkybase: {reply}"

    else:  # remote
        history.append({"role": "user", "content": user_input})
        completion = client.chat.completions.create(
            model="openai/gpt-oss-20b:together",
            messages=history,
        )
        reply = completion.choices[0].message.content
        print(f"{GREEN}Skybase:{RESET}", reply)
        history.append({"role": "assistant", "content": reply})

