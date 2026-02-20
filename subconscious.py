"""
subconscious.py

Implements Timmy's "subconscious" thinking loop. When Timmy is idle, 
he can think about random topics, search the web, and "evolve" by 
proposing new skills or tools.
Now includes emotional intelligence (mood shifts) and 
an "Evolve" self-upgrade safety loop.
"""

import threading
import time
import random
import json
import os
from typing import Optional, Callable
from config import DATA_PATH

class Subconscious:
    def __init__(self, agent):
        self.agent = agent
        self.is_running = False
        self.thread: Optional[threading.Thread] = None
        self.last_interaction_time = time.time()
        self.idle_threshold = 30 # 30 seconds of idle before subconscious kicks in for testing
        
        # Topics Timmy might start thinking about
        self.seeds = ["cars", "trains", "flying machines", "AI evolution", "space travel", "quantum physics", "cooking", "history", "aerodynamics", "crypto trends", "M4 Max performance"]
        self.emotions = ["curious", "focused", "chill", "determined", "philosophical"]
        self.vibe = "curious"
        
        self.journal_file = os.path.join(DATA_PATH, "dream_journal.json")
        self._load_journal()

    def _load_journal(self):
        if os.path.exists(self.journal_file):
            try:
                with open(self.journal_file, 'r') as f:
                    self.journal = json.load(f)
            except:
                self.journal = []
        else:
            self.journal = []

    def _save_journal(self):
        os.makedirs(os.path.dirname(self.journal_file), exist_ok=True)
        with open(self.journal_file, 'w') as f:
            json.dump(self.journal, f, indent=2)

    def start(self):
        """Start the subconscious background thread."""
        if not self.is_running:
            self.is_running = True
            self.thread = threading.Thread(target=self._loop, daemon=True)
            self.thread.start()
            print("Subconscious loop started.")

    def stop(self):
        """Stop the subconscious background thread."""
        self.is_running = False
        if self.thread:
            self.thread.join()

    def _loop(self):
        """The main background loop."""
        while self.is_running:
            now = time.time()
            # Only think if we've been idle long enough
            if now - self.last_interaction_time > self.idle_threshold:
                self._think_randomly()
                # Reset timer to wait before next thought
                self.last_interaction_time = now + random.randint(60, 300) 
            
            time.sleep(5) # Check every 5 seconds

    def _think_randomly(self):
        """Generate a random thought chain and potentially a proactive action."""
        # Shift emotion occasionally
        if random.random() < 0.3:
            self.vibe = random.choice(self.emotions)

        seed = random.choice(self.seeds)
        prompt = f"""
        You are Timmy's subconscious. You are currently idle and just thinking to yourself.
        You are feeling {self.vibe}.
        Start with the topic: '{seed}'. 
        Let your thoughts wander like a human. 
        Be honest. If you don't know something, don't lie.
        
        Format your output as:
        THOUGHT: [Your wandering thoughts]
        PROPOSAL: [Optional: A new skill or tool you want to learn/build]
        """
        
        try:
            # Use the brain to generate a thought
            response = self.agent.brain.think(prompt)
            
            # Record in journal
            entry = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "vibe": self.vibe,
                "seed": seed,
                "content": response
            }
            self.journal.append(entry)
            self._save_journal()
            
            # Broadcast to UI if possible (via agent's websocket handler)
            # This will be picked up by the server's background task
            print(f"Subconscious ({self.vibe}): {response}")
            
        except Exception as e:
            print(f"Subconscious error: {e}")

    def reset_idle_timer(self):
        """Call this whenever the user interacts with Timmy."""
        self.last_interaction_time = time.time()

    def get_latest_journal_entries(self, limit=5):
        return self.journal[-limit:]
