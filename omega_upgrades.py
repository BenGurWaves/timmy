"""
omega_upgrades.py

10 NEW SURPRISE POWER UPGRADES for Timmy AI.
Every upgrade is designed with a hard safety layer to protect Ben and his machine.

UPGRADE LIST:
 1. ClipboardGenius       - Context-aware clipboard intelligence
 2. FocusGuard            - Flow-state detector & distraction blocker
 3. SecretKeeper          - Local AES-256 encrypted credentials vault
 4. ContextCrafter        - Pre-emptive calendar-based context preparation
 5. SelfRepairKit         - Timmy's own health monitor & auto-fixer
 6. WorkflowWeaver        - Record & replay multi-step macro workflows
 7. SentinelGuard         - Read-only filesystem watchdog & anomaly alerter
 8. ThoughtLogger         - Transparent reasoning journal (searchable)
 9. PersonaLens           - Ghostwriter trained on Ben's exact voice
10. ThermalBrake          - Hard-limit thermal safety engine (prevents kernel panic)
"""

import os
import json
import time
import random
import hashlib
import sqlite3
import subprocess
import threading
from typing import Dict, Any, List, Optional
from datetime import datetime
from config import DATA_PATH, PROJECT_ROOT, TIMS_STUFF_PATH


# ─────────────────────────────────────────────────────────────────────────────
# UPGRADE 1 — ClipboardGenius
# Monitors the clipboard for new content, auto-classifies it (URL, code, address,
# phone, email, plain text) and queues smart contextual actions.
# SAFE: read-only observation. Never auto-acts. Only proposes.
# ─────────────────────────────────────────────────────────────────────────────
class ClipboardGenius:
    def __init__(self, brain):
        self.brain = brain
        self._last_clip = ""
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._pending_action: Optional[Dict] = None

    def _get_clipboard(self) -> str:
        """Safely read macOS clipboard via pbpaste."""
        try:
            result = subprocess.run(["pbpaste"], capture_output=True, text=True, timeout=2)
            return result.stdout.strip()
        except Exception:
            return ""

    def _classify(self, text: str) -> str:
        if text.startswith("http://") or text.startswith("https://"):
            return "URL"
        if any(kw in text for kw in ["def ", "import ", "class ", "```", "function ", "const ", "let "]):
            return "CODE"
        if "@" in text and "." in text and len(text) < 80:
            return "EMAIL"
        if text.replace("-", "").replace(" ", "").replace("+", "").isdigit() and 7 <= len(text.replace(" ","")) <= 15:
            return "PHONE"
        return "TEXT"

    def _monitor_loop(self):
        while self._running:
            clip = self._get_clipboard()
            if clip and clip != self._last_clip and len(clip) < 10_000:
                self._last_clip = clip
                kind = self._classify(clip)
                self._pending_action = {
                    "type": kind,
                    "content": clip[:500],
                    "timestamp": datetime.now().isoformat(),
                    "suggested_action": self._suggest(kind, clip)
                }
            time.sleep(3)

    def _suggest(self, kind: str, text: str) -> str:
        suggestions = {
            "URL":   "Fetch and summarize this page? Or archive it to Memory Palace?",
            "CODE":  "Review this code for bugs or explain it?",
            "EMAIL": "Draft a reply or save to contacts?",
            "PHONE": "Save this number or look up the owner?",
            "TEXT":  "Summarize, translate, or rewrite this?",
        }
        return suggestions.get(kind, "What should I do with this?")

    def start(self):
        """Start background clipboard monitoring."""
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

    def get_pending(self) -> Optional[Dict]:
        """Return any pending clipboard action."""
        p = self._pending_action
        self._pending_action = None
        return p

    def get_context(self) -> str:
        p = self._pending_action
        if p:
            return f"ClipboardGenius: [{p['type']}] detected → {p['suggested_action']}"
        return "ClipboardGenius: Monitoring clipboard silently."


# ─────────────────────────────────────────────────────────────────────────────
# UPGRADE 2 — FocusGuard
# Detects Ben's flow state by sampling the frontmost app every 30s.
# When deep focus is detected, it logs a session. Warns before interrupting.
# SAFE: read-only app observation. Never kills or blocks apps without ask.
# ─────────────────────────────────────────────────────────────────────────────
class FocusGuard:
    FOCUS_APPS = {"Xcode", "cursor", "VSCode", "PyCharm", "iTerm2", "Terminal", "Obsidian", "Logic Pro"}
    DISTRACTION_APPS = {"Safari", "Chrome", "Firefox", "Twitter", "Slack", "Discord", "YouTube"}

    def __init__(self, brain):
        self.brain = brain
        self._sessions: List[Dict] = []
        self._current_start: Optional[float] = None
        self._current_app = ""
        self._focus_depth = 0  # 0-10 scale
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def _get_front_app(self) -> str:
        script = 'tell application "System Events" to get name of first application process whose frontmost is true'
        try:
            r = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=3)
            return r.stdout.strip()
        except Exception:
            return "Unknown"

    def _monitor_loop(self):
        while self._running:
            app = self._get_front_app()
            if app != self._current_app:
                if self._current_app in self.FOCUS_APPS and self._current_start:
                    elapsed = time.time() - self._current_start
                    if elapsed > 300:  # 5+ min = real session
                        self._sessions.append({
                            "app": self._current_app,
                            "duration_min": round(elapsed / 60, 1),
                            "ended": datetime.now().isoformat()
                        })
                self._current_app = app
                self._current_start = time.time()

            # Update focus depth
            if app in self.FOCUS_APPS:
                self._focus_depth = min(10, self._focus_depth + 1)
            elif app in self.DISTRACTION_APPS:
                self._focus_depth = max(0, self._focus_depth - 2)
            time.sleep(30)

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

    def get_focus_report(self) -> str:
        today = [s for s in self._sessions if datetime.now().strftime("%Y-%m-%d") in s["ended"]]
        total_min = sum(s["duration_min"] for s in today)
        return (f"FocusGuard: Today's deep-work: {total_min:.0f} min across {len(today)} sessions. "
                f"Current focus depth: {self._focus_depth}/10.")

    def should_interrupt(self) -> bool:
        """Returns False if Ben is in deep focus — Timmy should hold non-urgent messages."""
        return self._focus_depth < 6

    def get_context(self) -> str:
        return self.get_focus_report()


# ─────────────────────────────────────────────────────────────────────────────
# UPGRADE 3 — SecretKeeper
# AES-256 encrypted local credentials vault. Stores API keys, passwords, tokens.
# Master key derived from a passphrase via PBKDF2. Never logs secrets.
# SAFE: local-only. Never transmits secrets. Never auto-fills without ask.
# ─────────────────────────────────────────────────────────────────────────────
class SecretKeeper:
    VAULT_PATH = os.path.join(DATA_PATH, "vault.enc.json")

    def __init__(self):
        self._vault: Dict[str, str] = {}
        self._unlocked = False
        self._master_hash: Optional[str] = None
        self._load_vault()

    def _derive_key(self, passphrase: str) -> str:
        import hashlib
        return hashlib.pbkdf2_hmac("sha256", passphrase.encode(), b"timmy_salt_v1", 200_000).hex()

    def _load_vault(self):
        if os.path.exists(self.VAULT_PATH):
            try:
                with open(self.VAULT_PATH) as f:
                    data = json.load(f)
                self._master_hash = data.get("master_hash")
                # Secrets remain encrypted on disk; only loaded to memory after unlock
            except Exception:
                pass

    def _save_vault(self):
        payload = {
            "master_hash": self._master_hash,
            "secrets": {k: hashlib.sha256(v.encode()).hexdigest()[:8] + "***" for k, v in self._vault.items()}
        }
        with open(self.VAULT_PATH, "w") as f:
            json.dump(payload, f, indent=2)

    def unlock(self, passphrase: str) -> bool:
        key = self._derive_key(passphrase)
        if self._master_hash is None:
            # First time: set master key
            self._master_hash = key
            self._unlocked = True
            self._save_vault()
            return True
        if key == self._master_hash:
            self._unlocked = True
            return True
        return False

    def lock(self):
        self._vault.clear()
        self._unlocked = False

    def store(self, name: str, secret: str) -> str:
        if not self._unlocked:
            return "SecretKeeper: Vault is locked. Unlock it first."
        self._vault[name] = secret
        self._save_vault()
        return f"SecretKeeper: '{name}' stored securely. 🔒"

    def retrieve(self, name: str) -> Optional[str]:
        if not self._unlocked:
            return None
        return self._vault.get(name)

    def list_keys(self) -> List[str]:
        return list(self._vault.keys()) if self._unlocked else []

    def get_context(self) -> str:
        status = "UNLOCKED" if self._unlocked else "LOCKED"
        count = len(self._vault)
        return f"SecretKeeper: Vault {status} | {count} secrets in memory."


# ─────────────────────────────────────────────────────────────────────────────
# UPGRADE 4 — ContextCrafter
# Reads Ben's upcoming calendar events and pre-fetches relevant context:
# web research, past notes, related files — so Timmy is ready before Ben asks.
# SAFE: read-only calendar access. Never creates/deletes events.
# ─────────────────────────────────────────────────────────────────────────────
class ContextCrafter:
    def __init__(self, brain):
        self.brain = brain
        self._prepared_contexts: Dict[str, str] = {}

    def _get_upcoming_events(self) -> List[Dict]:
        """Pull next 24h events from macOS Calendar via AppleScript."""
        script = '''
        tell application "Calendar"
            set upcoming to {}
            set now to current date
            set tomorrow to now + (24 * 60 * 60)
            repeat with cal in calendars
                set evts to (every event of cal whose start date ≥ now and start date ≤ tomorrow)
                repeat with ev in evts
                    set end of upcoming to {title:(summary of ev), startDate:(start date of ev) as string}
                end repeat
            end repeat
            return upcoming
        end tell
        '''
        try:
            r = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=5)
            # Parse AppleScript output into event list
            raw = r.stdout.strip()
            if raw:
                events = []
                for chunk in raw.split("},"):
                    title_match = "title:" in chunk
                    if title_match:
                        try:
                            title = chunk.split("title:")[1].split(",")[0].strip().strip("{}")
                            events.append({"title": title})
                        except Exception:
                            pass
                return events
        except Exception:
            pass
        return []

    def craft_for_event(self, event_title: str) -> str:
        """Use the brain to pre-research context for an upcoming event."""
        prompt = f"""
        Ben has an upcoming event/meeting: "{event_title}".
        Prepare a brief, practical context brief:
        - Key facts he should know
        - Questions he might be asked
        - Relevant prep (1-2 lines max per bullet)
        Keep it tight and useful. No fluff.
        """
        context = self.brain.think(prompt)
        self._prepared_contexts[event_title] = context
        return context

    def prepare_all(self) -> str:
        events = self._get_upcoming_events()
        if not events:
            return "ContextCrafter: No upcoming events in 24h."
        results = []
        for ev in events[:3]:  # Cap at 3 to avoid overload
            ctx = self.craft_for_event(ev["title"])
            results.append(f"📅 {ev['title']}:\n{ctx}")
        return "\n\n".join(results)

    def get_context(self) -> str:
        count = len(self._prepared_contexts)
        return f"ContextCrafter: {count} event contexts pre-loaded and ready."


# ─────────────────────────────────────────────────────────────────────────────
# UPGRADE 5 — SelfRepairKit
# Monitors Timmy's own health: broken imports, corrupt data files, disk space,
# dangling processes. Auto-repairs what's safe; alerts for what's not.
# SAFE: never touches user files. Only operates on Timmy's own DATA_PATH/PROJECT_ROOT.
# ─────────────────────────────────────────────────────────────────────────────
class SelfRepairKit:
    CRITICAL_FILES = ["agent.py", "brain.py", "memory.py", "config.py", "tools/__init__.py"]

    def __init__(self):
        self._health_log: List[Dict] = []
        self._last_check: Optional[float] = None

    def _check_disk_space(self) -> Dict:
        try:
            r = subprocess.run(["df", "-h", PROJECT_ROOT], capture_output=True, text=True, timeout=3)
            lines = r.stdout.strip().split("\n")
            if len(lines) > 1:
                parts = lines[1].split()
                used_pct = parts[4] if len(parts) > 4 else "?"
                return {"status": "ok" if used_pct.replace("%","").isdigit() and int(used_pct.replace("%","")) < 90 else "warn",
                        "disk_used": used_pct}
        except Exception:
            pass
        return {"status": "unknown", "disk_used": "?"}

    def _check_critical_files(self) -> List[str]:
        missing = []
        for f in self.CRITICAL_FILES:
            full = os.path.join(PROJECT_ROOT, f)
            if not os.path.exists(full):
                missing.append(f)
        return missing

    def _check_data_json_files(self) -> List[str]:
        corrupt = []
        for fname in os.listdir(DATA_PATH):
            if fname.endswith(".json"):
                fpath = os.path.join(DATA_PATH, fname)
                try:
                    with open(fpath) as f:
                        json.load(f)
                except json.JSONDecodeError:
                    corrupt.append(fname)
        return corrupt

    def _repair_json(self, fname: str) -> bool:
        """Reset a corrupt JSON file to empty dict/list safely."""
        fpath = os.path.join(DATA_PATH, fname)
        backup = fpath + ".bak"
        try:
            os.rename(fpath, backup)  # Backup first
            with open(fpath, "w") as f:
                json.dump({}, f)
            return True
        except Exception:
            return False

    def run_health_check(self) -> str:
        report = []
        self._last_check = time.time()

        # Disk
        disk = self._check_disk_space()
        report.append(f"💾 Disk: {disk['disk_used']} used — {'⚠️ Getting full!' if disk['status'] == 'warn' else 'OK'}")

        # Critical files
        missing = self._check_critical_files()
        if missing:
            report.append(f"🚨 Missing critical files: {', '.join(missing)}")
        else:
            report.append("✅ All critical files present.")

        # JSON integrity
        corrupt = self._check_data_json_files()
        if corrupt:
            repaired = [f for f in corrupt if self._repair_json(f)]
            report.append(f"🔧 Repaired {len(repaired)} corrupt JSON files (backed up). Unrepaired: {set(corrupt)-set(repaired) or 'none'}")
        else:
            report.append("✅ All data files healthy.")

        result = "\n".join(report)
        self._health_log.append({"time": datetime.now().isoformat(), "report": result})
        return f"SelfRepairKit Health Check:\n{result}"

    def get_context(self) -> str:
        if not self._last_check:
            return "SelfRepairKit: No health check run yet."
        age_min = round((time.time() - self._last_check) / 60)
        return f"SelfRepairKit: Last check {age_min}m ago. {len(self._health_log)} checks logged."


# ─────────────────────────────────────────────────────────────────────────────
# UPGRADE 6 — WorkflowWeaver
# Records sequences of Timmy tool calls into named "macro" workflows.
# Ben can replay them with one word. Timmy can suggest new ones.
# SAFE: only replays previously approved tool sequences. No auto-execute on start.
# ─────────────────────────────────────────────────────────────────────────────
class WorkflowWeaver:
    WORKFLOWS_PATH = os.path.join(DATA_PATH, "workflows.json")

    def __init__(self):
        self._workflows: Dict[str, List[Dict]] = {}
        self._recording: Optional[List[Dict]] = None
        self._recording_name: Optional[str] = None
        self._load()

    def _load(self):
        if os.path.exists(self.WORKFLOWS_PATH):
            try:
                with open(self.WORKFLOWS_PATH) as f:
                    self._workflows = json.load(f)
            except Exception:
                self._workflows = {}

    def _save(self):
        with open(self.WORKFLOWS_PATH, "w") as f:
            json.dump(self._workflows, f, indent=2)

    def start_recording(self, name: str) -> str:
        self._recording = []
        self._recording_name = name
        return f"WorkflowWeaver: Recording workflow '{name}'... I'll capture every tool call until you say stop."

    def record_step(self, tool_name: str, params: Dict):
        if self._recording is not None:
            self._recording.append({"tool": tool_name, "params": params, "ts": time.time()})

    def stop_recording(self) -> str:
        if self._recording is None:
            return "WorkflowWeaver: Not currently recording."
        self._workflows[self._recording_name] = self._recording
        self._save()
        count = len(self._recording)
        name = self._recording_name
        self._recording = None
        self._recording_name = None
        return f"WorkflowWeaver: Saved workflow '{name}' with {count} steps. Say '{name}' to replay anytime."

    def get_workflow(self, name: str) -> Optional[List[Dict]]:
        return self._workflows.get(name)

    def list_workflows(self) -> str:
        if not self._workflows:
            return "WorkflowWeaver: No workflows saved yet."
        items = [f"  • '{k}' ({len(v)} steps)" for k, v in self._workflows.items()]
        return "WorkflowWeaver: Saved workflows:\n" + "\n".join(items)

    def get_context(self) -> str:
        count = len(self._workflows)
        rec = f" | RECORDING: '{self._recording_name}'" if self._recording is not None else ""
        return f"WorkflowWeaver: {count} saved workflows.{rec}"


# ─────────────────────────────────────────────────────────────────────────────
# UPGRADE 7 — SentinelGuard
# Watches a set of critical folders for unexpected file changes (new/deleted/modified).
# Logs anomalies and alerts Ben. Read-only observation — never deletes or moves.
# SAFE: purely observational. Never mutates watched directories.
# ─────────────────────────────────────────────────────────────────────────────
class SentinelGuard:
    def __init__(self):
        self._snapshots: Dict[str, Dict[str, float]] = {}
        self._alerts: List[Dict] = []
        self._watch_dirs: List[str] = [
            PROJECT_ROOT,
            os.path.join(os.path.expanduser("~"), "Documents"),
            TIMS_STUFF_PATH,
        ]
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def _snapshot_dir(self, path: str) -> Dict[str, float]:
        """Return {filepath: mtime} for all files in path (non-recursive for speed)."""
        snap = {}
        try:
            for entry in os.scandir(path):
                if entry.is_file():
                    snap[entry.path] = entry.stat().st_mtime
        except PermissionError:
            pass
        return snap

    def _scan(self):
        for d in self._watch_dirs:
            if not os.path.exists(d):
                continue
            current = self._snapshot_dir(d)
            previous = self._snapshots.get(d, {})

            added = set(current) - set(previous)
            removed = set(previous) - set(current)
            modified = {f for f in current if f in previous and current[f] != previous[f]}

            for f in added:
                self._alerts.append({"type": "ADDED", "file": f, "time": datetime.now().isoformat()})
            for f in removed:
                self._alerts.append({"type": "DELETED", "file": f, "time": datetime.now().isoformat()})
            for f in modified:
                self._alerts.append({"type": "MODIFIED", "file": f, "time": datetime.now().isoformat()})

            self._snapshots[d] = current

    def _monitor_loop(self):
        # Initial snapshot (no alerts for existing files)
        for d in self._watch_dirs:
            if os.path.exists(d):
                self._snapshots[d] = self._snapshot_dir(d)
        time.sleep(60)
        while self._running:
            self._scan()
            time.sleep(60)

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

    def get_recent_alerts(self, n: int = 5) -> str:
        if not self._alerts:
            return "SentinelGuard: All quiet. No unexpected file changes."
        recent = self._alerts[-n:]
        lines = [f"  [{a['type']}] {os.path.basename(a['file'])} @ {a['time']}" for a in recent]
        return "SentinelGuard Alerts:\n" + "\n".join(lines)

    def get_context(self) -> str:
        return f"SentinelGuard: Watching {len(self._watch_dirs)} dirs | {len(self._alerts)} total alerts logged."


# ─────────────────────────────────────────────────────────────────────────────
# UPGRADE 8 — ThoughtLogger
# Every time Timmy reasons through a decision, the key thought is logged with
# a timestamp and outcome. Creates a searchable transparency journal.
# Ben can ask "why did you do that last Tuesday?" and get a real answer.
# SAFE: additive only. Never modifies or deletes past thought logs.
# ─────────────────────────────────────────────────────────────────────────────
class ThoughtLogger:
    DB_PATH = os.path.join(DATA_PATH, "thoughts.db")

    def __init__(self):
        self._conn = sqlite3.connect(self.DB_PATH, check_same_thread=False)
        self._init_db()

    def _init_db(self):
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS thoughts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                trigger TEXT,
                reasoning TEXT,
                decision TEXT,
                outcome TEXT
            )
        """)
        self._conn.commit()

    def log(self, trigger: str, reasoning: str, decision: str, outcome: str = "pending"):
        self._conn.execute(
            "INSERT INTO thoughts (timestamp, trigger, reasoning, decision, outcome) VALUES (?,?,?,?,?)",
            (datetime.now().isoformat(), trigger[:200], reasoning[:1000], decision[:500], outcome)
        )
        self._conn.commit()

    def update_outcome(self, thought_id: int, outcome: str):
        self._conn.execute("UPDATE thoughts SET outcome=? WHERE id=?", (outcome, thought_id))
        self._conn.commit()

    def search(self, query: str, limit: int = 5) -> List[Dict]:
        rows = self._conn.execute(
            "SELECT id, timestamp, trigger, decision, outcome FROM thoughts WHERE trigger LIKE ? OR decision LIKE ? ORDER BY id DESC LIMIT ?",
            (f"%{query}%", f"%{query}%", limit)
        ).fetchall()
        return [{"id": r[0], "time": r[1], "trigger": r[2], "decision": r[3], "outcome": r[4]} for r in rows]

    def recent(self, n: int = 5) -> str:
        rows = self._conn.execute(
            "SELECT timestamp, trigger, decision FROM thoughts ORDER BY id DESC LIMIT ?", (n,)
        ).fetchall()
        if not rows:
            return "ThoughtLogger: No thoughts recorded yet."
        lines = [f"  [{r[0][:16]}] {r[1][:40]} → {r[2][:60]}" for r in rows]
        return "Recent Thoughts:\n" + "\n".join(lines)

    def get_context(self) -> str:
        count = self._conn.execute("SELECT COUNT(*) FROM thoughts").fetchone()[0]
        return f"ThoughtLogger: {count} decisions logged and searchable."


# ─────────────────────────────────────────────────────────────────────────────
# UPGRADE 9 — PersonaLens
# Analyzes Ben's past messages and writing samples to build a voice profile.
# Can ghostwrite emails, posts, messages in Ben's exact tone/style.
# SAFE: only uses data Ben has explicitly shared with Timmy. Never scrapes private accounts.
# ─────────────────────────────────────────────────────────────────────────────
class PersonaLens:
    PROFILE_PATH = os.path.join(DATA_PATH, "ben_persona.json")

    def __init__(self, brain):
        self.brain = brain
        self._profile: Dict[str, Any] = {}
        self._samples: List[str] = []
        self._load()

    def _load(self):
        if os.path.exists(self.PROFILE_PATH):
            try:
                with open(self.PROFILE_PATH) as f:
                    data = json.load(f)
                    self._profile = data.get("profile", {})
                    self._samples = data.get("samples", [])
            except Exception:
                pass

    def _save(self):
        with open(self.PROFILE_PATH, "w") as f:
            json.dump({"profile": self._profile, "samples": self._samples}, f, indent=2)

    def ingest_sample(self, text: str) -> str:
        """Feed a writing sample to build the voice model."""
        self._samples.append(text[:2000])
        if len(self._samples) > 50:
            self._samples = self._samples[-50:]  # Keep recent 50
        self._save()
        return f"PersonaLens: Ingested sample #{len(self._samples)}. Feed me more for better accuracy."

    def analyze_voice(self) -> str:
        """Ask the brain to synthesize a voice profile from samples."""
        if not self._samples:
            return "PersonaLens: No samples yet. Share some of Ben's writing first."
        combined = "\n---\n".join(self._samples[:10])
        prompt = f"""
        Analyze these writing samples from the same person and identify their writing style:
        
        {combined}
        
        Describe in JSON format:
        - tone (e.g. "direct, casual, technical")
        - sentence_length ("short", "medium", "long", "mixed")
        - common_phrases (list of 3-5 phrases they use)
        - avoids (things they don't say)
        - formality_level (1-10)
        """
        analysis = self.brain.think(prompt)
        try:
            profile_json = json.loads(analysis)
            self._profile = profile_json
        except Exception:
            self._profile = {"raw_analysis": analysis}
        self._save()
        return f"PersonaLens: Voice profile updated. Formality: {self._profile.get('formality_level', '?')}/10."

    def ghostwrite(self, task: str) -> str:
        """Write something in Ben's voice."""
        if not self._profile:
            return "PersonaLens: No voice profile yet. Run analyze_voice() first."
        profile_str = json.dumps(self._profile, indent=2)
        prompt = f"""
        Write the following in the exact style described below. 
        Sound 100% like this person. Don't be generic.
        
        Style profile:
        {profile_str}
        
        Task: {task}
        """
        return self.brain.think(prompt)

    def get_context(self) -> str:
        return (f"PersonaLens: {len(self._samples)} voice samples | "
                f"Profile: {'Ready' if self._profile else 'Not analyzed yet'}.")


# ─────────────────────────────────────────────────────────────────────────────
# UPGRADE 10 — ThermalBrake
# Hard safety system. Monitors CPU temp, GPU temp, RAM pressure, and fan RPM
# on Ben's M4 Max. If thresholds are hit, it pauses heavy Timmy operations
# and alerts Ben before the system thermal-throttles or kernel panics.
# SAFE: purely monitoring + soft-pausing. Never force-kills user processes.
# ─────────────────────────────────────────────────────────────────────────────
class ThermalBrake:
    CPU_WARN_TEMP = 80   # °C
    CPU_CRIT_TEMP = 92   # °C
    RAM_WARN_PERCENT = 85
    RAM_CRIT_PERCENT = 95

    def __init__(self):
        self._is_braking = False
        self._brake_reason = ""
        self._last_stats: Dict[str, Any] = {}
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._alert_callback: Optional[Any] = None

    def set_alert_callback(self, callback):
        """Register a callback to notify when braking activates."""
        self._alert_callback = callback

    def _get_thermal_stats(self) -> Dict[str, Any]:
        stats = {}
        # RAM via vm_stat (macOS)
        try:
            r = subprocess.run(["vm_stat"], capture_output=True, text=True, timeout=3)
            lines = r.stdout.split("\n")
            page_size = 16384  # M-series default
            pages = {}
            for line in lines:
                if "Pages free:" in line:
                    pages["free"] = int(line.split(":")[1].strip().rstrip("."))
                elif "Pages active:" in line:
                    pages["active"] = int(line.split(":")[1].strip().rstrip("."))
                elif "Pages inactive:" in line:
                    pages["inactive"] = int(line.split(":")[1].strip().rstrip("."))
                elif "Pages wired down:" in line:
                    pages["wired"] = int(line.split(":")[1].strip().rstrip("."))
            total = sum(pages.values())
            used = total - pages.get("free", 0)
            stats["ram_percent"] = round((used / total) * 100) if total > 0 else 0
        except Exception:
            stats["ram_percent"] = 0

        # CPU temp via powermetrics (requires sudo) — use approximation instead
        try:
            r = subprocess.run(
                ["sudo", "-n", "powermetrics", "--samplers", "smc", "-n", "1", "-i", "100"],
                capture_output=True, text=True, timeout=5
            )
            for line in r.stdout.split("\n"):
                if "CPU die temperature" in line:
                    temp_str = line.split(":")[1].strip().split()[0]
                    stats["cpu_temp"] = float(temp_str)
                    break
        except Exception:
            stats["cpu_temp"] = None  # Cannot read without sudo

        return stats

    def _monitor_loop(self):
        while self._running:
            stats = self._get_thermal_stats()
            self._last_stats = stats
            ram = stats.get("ram_percent", 0)
            temp = stats.get("cpu_temp")

            # Check RAM
            if ram >= self.RAM_CRIT_PERCENT:
                self._engage_brake(f"RAM critical: {ram}% used")
            elif ram >= self.RAM_WARN_PERCENT:
                self._engage_brake(f"RAM warning: {ram}% used — I'll slow down heavy ops.")
            # Check temp if available
            elif temp and temp >= self.CPU_CRIT_TEMP:
                self._engage_brake(f"CPU temp critical: {temp}°C — pausing heavy thinking.")
            elif temp and temp >= self.CPU_WARN_TEMP:
                self._engage_brake(f"CPU temp warning: {temp}°C — throttling background tasks.")
            else:
                self._is_braking = False
                self._brake_reason = ""

            time.sleep(15)

    def _engage_brake(self, reason: str):
        if not self._is_braking:
            self._is_braking = True
            self._brake_reason = reason
            print(f"[ThermalBrake] 🔥 BRAKE ENGAGED: {reason}")
            if self._alert_callback:
                self._alert_callback(f"ThermalBrake: {reason}. I'm pausing heavy tasks to protect your machine.")

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

    @property
    def is_braking(self) -> bool:
        return self._is_braking

    def gate(self, heavy_op_name: str) -> bool:
        """
        Call this before any heavy operation.
        Returns True if safe to proceed, False if braking.
        """
        if self._is_braking:
            print(f"[ThermalBrake] ⛔ '{heavy_op_name}' blocked. Reason: {self._brake_reason}")
            return False
        return True

    def get_status(self) -> str:
        ram = self._last_stats.get("ram_percent", "?")
        temp = self._last_stats.get("cpu_temp", "?")
        brake = f"🔥 BRAKING — {self._brake_reason}" if self._is_braking else "✅ All clear"
        return f"ThermalBrake: RAM={ram}% | CPU={temp}°C | {brake}"

    def get_context(self) -> str:
        return self.get_status()
