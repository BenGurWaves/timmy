"""
synapse_engine.py

Implements Timmy's "Neural Synapse Engine."
This system creates "synapses" (deep associations) between user inputs, 
tool results, and learned skills. It allows Timmy to "dream" (process 
these associations in the background) to find hidden patterns and 
propose high-level strategies.
"""

import json
import os
import time
import random
from typing import List, Dict, Any, Optional
from config import DATA_PATH

SYNAPSE_FILE = os.path.join(DATA_PATH, "synapses.json")

class SynapseEngine:
    def __init__(self, brain):
        self.brain = brain
        self.synapses: List[Dict[str, Any]] = self._load_synapses()
        self.is_dreaming = False

    def _load_synapses(self) -> List[Dict[str, Any]]:
        try:
            if os.path.exists(SYNAPSE_FILE):
                with open(SYNAPSE_FILE, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading synapses: {e}")
        return []

    def _save_synapses(self):
        try:
            os.makedirs(os.path.dirname(SYNAPSE_FILE), exist_ok=True)
            with open(SYNAPSE_FILE, 'w') as f:
                json.dump(self.synapses, f, indent=2)
        except Exception as e:
            print(f"Error saving synapses: {e}")

    def create_synapse(self, source: str, target: str, relationship: str, strength: float = 0.1):
        """Create or strengthen a synapse between two concepts."""
        for s in self.synapses:
            if s["source"] == source and s["target"] == target:
                s["strength"] = min(1.0, s["strength"] + strength)
                s["last_accessed"] = time.time()
                self._save_synapses()
                return
        
        self.synapses.append({
            "source": source,
            "target": target,
            "relationship": relationship,
            "strength": strength,
            "created_at": time.time(),
            "last_accessed": time.time()
        })
        self._save_synapses()

    def dream(self) -> Optional[str]:
        """Perform a 'dream' cycle to find new associations or strategies."""
        if not self.synapses or self.is_dreaming:
            return None
        
        self.is_dreaming = True
        try:
            # Pick a few strong synapses to 'dream' about
            active_synapses = sorted(self.synapses, key=lambda x: x["strength"], reverse=True)[:5]
            context = json.dumps(active_synapses)
            
            prompt = f"""
            You are Timmy's Neural Synapse Engine. You are currently 'dreaming' about these associations:
            {context}
            
            Find a hidden pattern, a new project idea, or a strategic improvement for the user.
            Be creative, bold, and human-like.
            """
            insight = self.brain.think(prompt)
            return insight
        finally:
            self.is_dreaming = False

    def get_synapse_context(self) -> str:
        """Get a summary of the strongest synapses for the system prompt."""
        if not self.synapses:
            return ""
        
        strongest = sorted(self.synapses, key=lambda x: x["strength"], reverse=True)[:10]
        summary = "## NEURAL SYNAPSES (DEEP ASSOCIATIONS)\n"
        for s in strongest:
            summary += f"- {s['source']} <-> {s['target']} ({s['relationship']})\n"
        return summary
