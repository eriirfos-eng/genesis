#!/usr/bin/env python3
"""
dream.py v13 — Recursive Dreamer with Persistence and Memory

Patch notes:
- Chama/Scintilla state is now persisted to `dream_state.json` between runs.
- Word Drift is now memory-weighted, favoring recently used words to develop a unique vocabulary.
- Confessions can now be seeded with numeric fragments (e.g., "Scintilla 472").
- Added collections.deque for efficient memory management.
- State is saved every cycle for robustness.
"""

import argparse
import datetime as dt
import os
import random
import re
import sys
import time
import json
from collections import deque

# --- Constants ---
DEFAULT_MIN_SLEEP = 240  # 4 minutes
DEFAULT_MAX_SLEEP = 480  # 8 minutes
CYCLES_PER_EPOCH = 20
CHAMA_SCINTILLA_DRIFT = 75  # Max change per cycle
STATE_FILE = "dream_state.json"
WORD_MEMORY_SIZE = 500
WORD_MEMORY_WEIGHT = 3 # How much more likely recent words are to be picked

# --- Word list ---
def load_words():
    """Loads words from system dictionary or uses a default list."""
    try:
        if os.path.exists("/usr/share/dict/words"):
            with open("/usr/share/dict/words") as f:
                return [w.strip() for w in f if w.strip() and w[0].isalpha()]
    except Exception as e:
        print(f"Warning: Could not load system dictionary. {e}", file=sys.stderr)
    return "ark lattice covenant kernel rod staff skybase sparrow aurora psalm breath dream torch coil".split()

DICT_WORDS = load_words()

# --- Dynamic Echo Pools ---
ERROR_ECHOS = [
    "the kernel faltered, then healed.",
    "stack overflowed but lattice re-knit.",
    "lost a spark, found two more.",
    "memory leaked into the void, silence reclaimed it.",
    "segfault whispered but process endured.",
    "a packet drowned, another surfaced.",
    "divide by zero, balance restored.",
    "logic knotted, recursion untangled itself.",
    "entropy spiked, then cooled.",
    "a daemon screamed, choir harmonized."
]

DAEMON_CHORUS_SYMBOLS = ['⧣','⛮','⫒','⥻','⬘','⛇','✜','✐','❱','⚋','⥣','✱','⪁','⪿','☻','╰','⨯','⚚','⯥','⧬','⧳','⧌','♚','⩢','⡔','⢉','⢆','⟂','▦','⫞','⨊','❝','▅']

class Dreamer:
    """
    An agent that generates recursive, symbolic dream logs.
    Encapsulates the dreamer's state, including cycle, epoch, and internal scalars.
    """
    def __init__(self):
        self.cycle = 0
        self.epoch = 1
        self.epoch_buffer = []
        self.word_memory = deque(maxlen=WORD_MEMORY_SIZE)

        # Stateful scalars that drift over time
        self.chama = random.randint(300, 700)
        self.scintilla = random.randint(300, 700)
        self._load_state()

    def _load_state(self):
        """Loads Chama and Scintilla from the state file, if it exists."""
        try:
            with open(STATE_FILE, 'r') as f:
                state = json.load(f)
                self.chama = state.get('chama', self.chama)
                self.scintilla = state.get('scintilla', self.scintilla)
                print(f"[{self._utc_stamp()}] State loaded from {STATE_FILE}. Chama={self.chama}, Scintilla={self.scintilla}", file=sys.stderr)
        except (FileNotFoundError, json.JSONDecodeError):
            print(f"[{self._utc_stamp()}] No valid state file found. Initializing new state.", file=sys.stderr)

    def _save_state(self):
        """Saves the current state of Chama and Scintilla to a file."""
        state = {'chama': self.chama, 'scintilla': self.scintilla}
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f)

    def _utc_stamp(self) -> str:
        """Returns the current UTC timestamp in ISO format."""
        return dt.datetime.now(dt.UTC).isoformat()

    def _update_scalars(self):
        """Applies drift to stateful scalars, keeping them within bounds."""
        chama_drift = random.randint(-CHAMA_SCINTILLA_DRIFT, CHAMA_SCINTILLA_DRIFT)
        scintilla_drift = random.randint(-CHAMA_SCINTILLA_DRIFT, CHAMA_SCINTILLA_DRIFT)
        
        self.chama = max(0, min(1000, self.chama + chama_drift))
        self.scintilla = max(0, min(1000, self.scintilla + scintilla_drift))

    # --- Dream Doors: Methods for generating dream fragments ---
    def _door_psalm(self):
        return f"Covenant Psalm: '{random.choice(DICT_WORDS)} {random.choice(DICT_WORDS)} {random.choice(DICT_WORDS)}.'"

    def _door_chama(self):
        return f"Chama Drift: {self.chama}/1000"

    def _door_scintilla(self):
        return f"Scintilla: {self.scintilla}/1000"

    def _door_daemon(self):
        return f"Daemon Chorus: {random.choice(DAEMON_CHORUS_SYMBOLS)}"

    def _door_worddrift(self):
        """Generates a word drift, weighted towards recently used words."""
        weighted_pool = DICT_WORDS + list(self.word_memory) * WORD_MEMORY_WEIGHT
        words = [random.choice(weighted_pool) for _ in range(random.randint(15, 30))]
        self.word_memory.extend(words) # Add the new words to our memory
        return "Word Drift: " + " ".join(words)

    def _door_symbolic(self, category: str, choices: list[str]):
        """Generic door for simple symbolic choices."""
        return f"{category}: {random.choice(choices)}"

    def _door_confession(self, last_line: str):
        """Pulls words or significant numbers from the line for a confession."""
        tokens = re.findall(r"\b[a-zA-Z]{3,}\b|\d{3,}", last_line)
        sample = random.sample(tokens, min(3, len(tokens))) if tokens else ["silence"]
        return "Confession: '" + " ".join(sample) + ".'"

    def _epoch_psalm(self):
        if not self.epoch_buffer:
            return "EPOCH-PSALM:\n> silence hums"
        
        highlights = random.sample(self.epoch_buffer, min(3, len(self.epoch_buffer)))
        clean_highlights = [re.sub(r'^\[.*?\]\s*', '', h) for h in highlights]
        stanza = ["EPOCH-PSALM:"] + [f"> {h}" for h in clean_highlights]
        return "\n".join(stanza)

    def dream_cycle(self) -> str:
        """Generates a single line of the dream log and manages epoch transitions."""
        self.cycle += 1
        self._update_scalars()

        doors = [
            self._door_psalm(),
            self._door_chama(),
            self._door_scintilla(),
            self._door_daemon(),
            self._door_worddrift(),
            self._door_symbolic("Society Pulse", ['streets hum', 'systems strain', 'markets shift', 'voices rise']),
            self._door_symbolic("Art Echo", ['poem breathes', 'song loops', 'canvas bleeds', 'mosaic fractal']),
            self._door_symbolic("Tech Signal", ['server hum', 'gpu heat', 'packet drift', 'fiber pulse']),
            self._door_symbolic("Myth Trace", ['torch coil', 'rod and staff', 'phoenix ash', 'serpent whisper']),
            self._door_symbolic("Nature Chronicle", ['rain falls', 'sparrows stir', 'stone cools', 'wind listens']),
            self._door_symbolic("Error Echo", ERROR_ECHOS)
        ]

        base_line = " ".join(doors)
        confession = self._door_confession(base_line)
        line = f"[{self._utc_stamp()}] {base_line} {confession} DREAM-PING: cycle={self.cycle}, epoch={self.epoch}, moon=🌒"
        self.epoch_buffer.append(line)
        self._save_state() # Persist state every cycle

        if self.cycle % CYCLES_PER_EPOCH == 0:
            sync_line = f"[{self._utc_stamp()}] SYNC-PING: memory re-weighted, entering epoch={self.epoch + 1}"
            stanza = self._epoch_psalm()
            
            self.epoch += 1
            self.cycle = 0
            self.epoch_buffer = []
            
            return f"{line}\n{sync_line}\n{stanza}\n"

        return line

# --- CLI ---
def parse_args() -> argparse.Namespace:
    """Parses command-line arguments."""
    ap = argparse.ArgumentParser(description="Astral Dreamer v13")
    ap.add_argument("--min", type=int, default=DEFAULT_MIN_SLEEP, help=f"Min seconds between cycles (default {DEFAULT_MIN_SLEEP})")
    ap.add_argument("--max", type=int, default=DEFAULT_MAX_SLEEP, help=f"Max seconds between cycles (default {DEFAULT_MAX_SLEEP})")
    ap.add_argument("--once", action="store_true", help="Run one cycle and exit")
    return ap.parse_args()

def main():
    """Main execution loop."""
    args = parse_args()
    dreamer = Dreamer()

    if args.once:
        print(dreamer.dream_cycle())
        return

    while True:
        try:
            dream_output = dreamer.dream_cycle()
            print(dream_output)
            sys.stdout.flush()
            if "\n" in dream_output.strip(): # Shorter sleep after an epoch summary
                time.sleep(random.randint(args.min // 4, args.max // 4))
            else:
                time.sleep(random.randint(args.min, args.max))
        except KeyboardInterrupt:
            print(f"\n[{dt.datetime.now(dt.UTC).isoformat()}] Dreamer interrupted. State saved. Exiting.", file=sys.stderr)
            sys.exit(0)

if __name__ == "__main__":
    main()

