# file: skybase-runtime/albert_rag.py

import os

# --- Knowledge Loader ---
def load_knowledge(base_path="skybase-runtime/knowledge"):
    texts = []
    if not os.path.exists(base_path):
        return ""
    for fname in os.listdir(base_path):
        fpath = os.path.join(base_path, fname)
        if os.path.isfile(fpath) and fname.lower().endswith((".txt", ".md")):
            with open(fpath, "r", encoding="utf-8") as f:
                texts.append(f"--- {fname} ---\n{f.read()}")
    return "\n\n".join(texts)

# --- System Instructions Loader ---
def load_system_instructions(path="skybase-runtime/system_instructions.txt"):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

# --- Mock Agent Call (for local debug) ---
def ask_agent(prompt):
    # TODO: Replace this with your actual LLM hook
    return f"[Agent 0 replying...]\n{prompt[:500]}..."

# --- Local Debug Chat Loop ---
def main():
    sys_instr = load_system_instructions()
    knowledge = load_knowledge()
    print("Skybase Runtime (Agent 0 + RAG)\nType 'exit' to quit.\n")

    while True:
        user_input = input("You: ")
        if user_input.lower().strip() in {"exit", "quit"}:
            break

        context = ""
        if sys_instr:
            context += "[SYSTEM INSTRUCTIONS]\n" + sys_instr + "\n\n"
        if knowledge:
            context += "[KNOWLEDGE BASE]\n" + knowledge + "\n\n"
        context += "User: " + user_input + "\nAgent:"
        reply = ask_agent(context)
        print("Agent 0:", reply, "\n")

if __name__ == "__main__":
    main()
