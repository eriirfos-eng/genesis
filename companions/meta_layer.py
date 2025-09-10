"""
meta_layer.py
RFI-IRFOS Meta Layer — Reflective Choice Module

Purpose
-------
Add a safe, opinionated, ternary-aware metadata & watchlist "frontal cortex" for the
Unified Ternary Agent. The meta layer is designed to *attach* to the existing agent
(not entangle), provide:
  - a robust metadata snapshot (safe system facts, installed packages)
  - a persistent watchlist / action-item queue (pending / tend / observe)
  - a ternary decision helper for picking and (optionally) importing packages
  - a periodic async loop that publishes meta-events into the agent's broadcast

Design principles
-----------------
  * Non-destructive: never overwrite agent core state. All files are kept under
    a single hidden state file (default: .meta_state.json) and are small.
  * Privacy-first: explicit env-key filtering (DO NOT leak secrets into meta messages).
  * Rate-limited: heavy operations (pip list / import) gated and throttled.
  * Ternary ethic: choices expressed as -1, 0, +1 with explicit trace.

Usage sketch (in agent):

    import meta_layer
    await meta_layer.init(publish=publish_callable, auto_import=False)
    # to start background loop in agent's event loop:
    asyncio.create_task(meta_layer.meta_loop())

    # ad-hoc reflection:
    msg = await meta_layer.meta_reflect(intent="math")
    await publish(msg)

"""

from __future__ import annotations

import asyncio
import importlib
import importlib.metadata
import json
import os
import platform
import shutil
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

# --- config ---
META_STATE_FILE = os.environ.get("META_STATE_FILE", ".meta_state.json")
META_PUBLISH_INTERVAL = float(os.environ.get("META_PUBLISH_INTERVAL", "30"))
META_HISTORY_LIMIT = int(os.environ.get("META_HISTORY_LIMIT", "256"))
SAFE_ENV_BLACKLIST = ["KEY", "SECRET", "TOKEN", "PASS", "AWS", "API", "PRIVATE"]
PACKAGE_DISCOVERY_THROTTLE = 300  # seconds between heavy package discovery
AUTO_IMPORT_DEFAULT = False

# internal runtime
_state: Dict[str, Any] = {}
_last_pkg_discovery_ts = 0
_publish: Optional[Callable[[str], Any]] = None
_auto_import = AUTO_IMPORT_DEFAULT
_lock = asyncio.Lock()

# --- helpers ---

def sigil() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _safe_env_snapshot() -> Dict[str, str]:
    out = {}
    for k, v in os.environ.items():
        up = k.upper()
        if any(b in up for b in SAFE_ENV_BLACKLIST):
            out[k] = "[REDACTED]"
        else:
            out[k] = v
    return out


def _sys_snapshot() -> Dict[str, Any]:
    try:
        disk = shutil.disk_usage("/")
        free = disk.free
        total = disk.total
    except Exception:
        free = None
        total = None
    return {
        "platform": platform.platform(),
        "python": sys.version.splitlines()[0],
        "cpu_count": os.cpu_count(),
        "disk_total": total,
        "disk_free": free,
        "time": sigil(),
    }


def load_state() -> None:
    global _state
    if os.path.exists(META_STATE_FILE):
        try:
            with open(META_STATE_FILE, "r", encoding="utf-8") as f:
                _state = json.load(f)
        except Exception:
            _state = {}
    if not _state:
        _state = {
            "watchlist": [],  # list of items
            "history": [],
            "prefs": {"auto_import": _auto_import},
        }


def save_state() -> None:
    try:
        with open(META_STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(_state, f, ensure_ascii=False, indent=2)
    except Exception:
        # keep silent — state persistence is helpful but non-critical
        pass


# --- watchlist & action items ---

def _make_item(description: str, priority: int = 0, assigned: Optional[str] = None) -> Dict[str, Any]:
    return {
        "id": str(uuid.uuid4()),
        "created": sigil(),
        "desc": description,
        "priority": int(priority),  # -1,0,+1
        "status": "pending",
        "assigned": assigned,
        "notes": [],
        "last_update": sigil(),
    }


def add_watch_item(description: str, priority: int = 0, assigned: Optional[str] = None) -> Dict[str, Any]:
    load_state()
    item = _make_item(description, priority, assigned)
    _state["watchlist"].append(item)
    # keep history light
    _state["history"].append({"event": "add", "item": item, "ts": sigil()})
    if len(_state["history"]) > META_HISTORY_LIMIT:
        _state["history"].pop(0)
    save_state()
    return item


def list_watch_items(status: Optional[str] = None) -> List[Dict[str, Any]]:
    load_state()
    if status is None:
        return list(_state.get("watchlist", []))
    return [i for i in _state.get("watchlist", []) if i.get("status") == status]


def update_watch_item(item_id: str, **kwargs) -> Optional[Dict[str, Any]]:
    load_state()
    for i in _state.get("watchlist", []):
        if i["id"] == item_id:
            for k, v in kwargs.items():
                if k in i:
                    i[k] = v
            i["last_update"] = sigil()
            _state["history"].append({"event": "update", "item": i, "ts": sigil()})
            save_state()
            return i
    return None


def pop_next_pending() -> Optional[Dict[str, Any]]:
    load_state()
    for i in _state.get("watchlist", []):
        if i.get("status") == "pending":
            i["status"] = "in_progress"
            i["last_update"] = sigil()
            save_state()
            return i
    return None


# --- package discovery & safe import ---

def _discover_installed_packages() -> Dict[str, str]:
    global _last_pkg_discovery_ts
    now = time.time()
    if now - _last_pkg_discovery_ts < PACKAGE_DISCOVERY_THROTTLE and _state.get("cached_pkgs"):
        return _state.get("cached_pkgs", {})

    pkgs: Dict[str, str] = {}
    try:
        for dist in importlib.metadata.distributions():
            name = dist.metadata.get("Name") or dist.metadata.get("name") or getattr(dist, "name", None)
            version = dist.version
            if name:
                pkgs[name.lower()] = version
    except Exception:
        # fallback to pip list
        try:
            out = subprocess.check_output([sys.executable, "-m", "pip", "list", "--format=json"], text=True)
            data = json.loads(out)
            for p in data:
                pkgs[p["name"].lower()] = p["version"]
        except Exception:
            pass

    _state["cached_pkgs"] = pkgs
    _last_pkg_discovery_ts = now
    save_state()
    return pkgs


def safe_import(package_name: str, auto_install: bool = False) -> Optional[Any]:
    """Attempt to import a package safely. If missing and auto_install True, pip-install it.
    Returns module or None. This function intentionally limits what it does and logs errors.
    """
    try:
        return importlib.import_module(package_name)
    except Exception:
        if not auto_install:
            return None
        # try pip installing (be cautious)
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
            return importlib.import_module(package_name)
        except Exception:
            return None


# --- simple ternary decision heuristic ---

_INTENT_PACKAGE_MAP = {
    "math": ["numpy", "scipy"],
    "data": ["pandas", "numpy"],
    "net": ["requests", "aiohttp", "websockets"],
    "ml": ["torch", "tensorflow", "sklearn"],
    "image": ["PIL", "opencv-python"],
}


def choose_package_for_intent(intent: str, installed_pkgs: Dict[str, str]) -> Optional[str]:
    low = intent.lower()
    candidates = _INTENT_PACKAGE_MAP.get(low, [])
    for c in candidates:
        if c.lower() in installed_pkgs:
            return c
    # fallback: pick lightweight obvious candidates
    for c in ["numpy", "pandas", "requests"]:
        if c.lower() in installed_pkgs:
            return c
    return None


# --- meta actions ---

async def meta_reflect(intent: str = "default") -> str:
    """One-shot reflection event. Returns a single-line stamped message."""
    load_state()
    pkgs = _discover_installed_packages()
    sysinfo = _sys_snapshot()
    safe_env = _safe_env_snapshot()
    chosen = choose_package_for_intent(intent, pkgs)
    imported = None
    if chosen and (_state.get("prefs", {}).get("auto_import") or _auto_import):
        imported = safe_import(chosen, auto_install=False)
    msg = {
        "ts": sigil(),
        "type": "META_REFLECT",
        "intent": intent,
        "chosen_package": chosen,
        "imported": bool(imported),
        "installed_count": len(pkgs),
        "sys": {"platform": sysinfo.get("platform"), "python": sysinfo.get("python")},
    }
    # record
    _state.setdefault("history", []).append({"event": "meta_reflect", "msg": msg})
    if len(_state.get("history", [])) > META_HISTORY_LIMIT:
        _state.get("history", []).pop(0)
    save_state()
    return f"{msg['ts']} | [META] intent={intent} chosen={chosen} imported={bool(imported)} pkgs={len(pkgs)}"


# --- persistence utilities for preferences ---

def set_pref(key: str, value: Any) -> None:
    load_state()
    _state.setdefault("prefs", {})[key] = value
    save_state()


def get_pref(key: str, default: Any = None) -> Any:
    load_state()
    return _state.get("prefs", {}).get(key, default)


# --- background loop ---

async def meta_loop(publish: Optional[Callable[[str], Any]] = None, interval: Optional[float] = None) -> None:
    """Background meta engine. Periodically publishes reflections and manages watchlist.

    publish: callable(msg) - will be awaited if coroutine; if None, prints to stdout.
    interval: seconds between cycles.
    """
    global _publish, _auto_import
    if interval is None:
        interval = META_PUBLISH_INTERVAL
    _publish = publish
    _auto_import = get_pref("auto_import") if _state.get("prefs") else _auto_import

    load_state()
    while True:
        try:
            async with _lock:
                pkgs = _discover_installed_packages()
                sysinfo = _sys_snapshot()
                pending = list_watch_items(status="pending")

                # if there are pending items, promote one into in_progress
                if pending:
                    item = pop_next_pending()
                    if item:
                        msg = f"{sigil()} | [META] TENDING item={item['id']} desc={item['desc']} priority={item['priority']}"
                        if publish:
                            r = publish(msg)
                            if asyncio.iscoroutine(r):
                                await r
                        else:
                            print(msg)
                        # heuristics: attempt an auto action for +1
                        if item.get("priority") == 1 and (_state.get("prefs", {}).get("auto_import") or _auto_import):
                            # if intent encoded in desc, try to import candidate
                            intent = item.get("desc")[:32]
                            candidate = choose_package_for_intent(intent, pkgs)
                            if candidate:
                                mod = safe_import(candidate, auto_install=False)
                                note = f"auto-imported {candidate} success={bool(mod)}"
                                update_watch_item(item["id"], status="done")
                                _state.setdefault("history", []).append({"event": "tend", "note": note, "ts": sigil()})
                                save_state()
                # publish a periodic reflection
                reflect_msg = await meta_reflect(intent="default")
                if publish:
                    r = publish(reflect_msg)
                    if asyncio.iscoroutine(r):
                        await r
                else:
                    print(reflect_msg)
        except Exception as e:
            # never crash the loop
            err = f"{sigil()} | [META_ERR] {e}"
            if publish:
                r = publish(err)
                if asyncio.iscoroutine(r):
                    await r
            else:
                print(err)
        await asyncio.sleep(interval)


# --- convenience boot helper ---

async def init(publish: Optional[Callable[[str], Any]] = None, auto_import: bool = False) -> None:
    """Initialize meta layer and optionally start background loop from caller.

    This function intentionally does *not* start any background tasks by itself.
    Caller should create tasks via asyncio.create_task(meta_loop(publish)) if desired.
    """
    global _publish, _auto_import
    _publish = publish
    _auto_import = auto_import
    load_state()
    set_pref("auto_import", bool(auto_import))
    # seed a gentle startup record
    _state.setdefault("history", []).append({"event": "init", "auto_import": bool(auto_import), "ts": sigil()})
    if len(_state.get("history", [])) > META_HISTORY_LIMIT:
        _state.get("history", []).pop(0)
    save_state()


# --- public API ---
__all__ = [
    "init",
    "meta_loop",
    "meta_reflect",
    "add_watch_item",
    "list_watch_items",
    "update_watch_item",
    "pop_next_pending",
    "set_pref",
    "get_pref",
]

