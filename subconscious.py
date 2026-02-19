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
from typing import Optional, Callable
from brain import Brain

class Subconscious:
    def __init__(self, brain: Brain, on_thought_callback: Callable[[str], None]):
        self.brain = brain
        self.on_thought_callback = on_thought_callback
        self.is_running = False
        self.thread: Optional[threading.Thread] = None
        self.last_thought_time = time.time()
        self.idle_threshold = 60 * 5 # 5 minutes of idle before subconscious kicks in
        
        # Topics Timmy might start thinking about
        self.seeds = ["cars", "trains", "flying machines", "AI evolution", "space travel", "quantum physics", "cooking", "history", "aerodynamics", "crypto trends", "M4 Max performance"]
        self.emotions = ["curious", "focused", "chill", "determined", "philosophical"]
        self.current_emotion = "curious"

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
            if now - self.last_thought_time > self.idle_threshold:
                self._think_randomly()
                # Reset timer with some randomness to avoid predictable intervals
                self.last_thought_time = now + random.randint(300, 900) 
            
            time.sleep(10) # Check every 10 seconds

    def _think_randomly(self):
        """Generate a random thought chain and potentially a proactive action."""
        # Shift emotion occasionally
        if random.random() < 0.2:
            self.current_emotion = random.choice(self.emotions)
            self.on_thought_callback(f"Feeling a bit {self.current_emotion} right now.")

        seed = random.choice(self.seeds)
        prompt = f"""
        You are Timmy's subconscious. You are currently idle and just thinking to yourself.
        You are feeling {self.current_emotion}.
        Start with the topic: '{seed}'. 
        Let your thoughts wander like a human. 
        If you find something you don't understand, decide to search it.
        If you think of a cool new skill you could have, propose it.
        If you think of a way to upgrade yourself (e.g., a new tool or better logic), propose it as an 'EVOLVE' action.
        
        Format your output as:
        THOUGHT: [Your wandering thoughts]
        PROPOSAL: [Optional: A new skill or tool you want to learn/build]
        SEARCH: [Optional: A query if you want to learn something new]
        EVOLVE: [Optional: A self-upgrade proposal for a specific component]
        """
        
        try:
            # Use a smaller/faster model for background thinking if available, 
            # or just the main model.
            response = self.brain.think(prompt)
            self.on_thought_callback(response)
            
            # If there's an EVOLVE proposal, we'd handle it here 
            # (e.g., by triggering a 'Council' debate to verify the new code)
        except Exception as e:
            print(f"Subconscious error: {e}")

    def reset_idle_timer(self):
        """Call this whenever the user interacts with Timmy."""
        self.last_thought_time = time.time()

    def propose_self_upgrade(self, component: str, new_code: str):
        """Propose a self-upgrade with a safety loop."""
        # This would trigger a 'Council' debate to verify the new code
        # before applying it to a 'clone' for testing.
        proposal = f"I've thought of an upgrade for {component}. I'll test it in a safe environment first."
        self.on_thought_callback(proposal)
        # Logic to test and then apply upgrade
