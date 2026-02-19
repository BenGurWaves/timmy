"""
council.py

Implements the "Council" multi-model debate system. 
All local Ollama models argue with each other to solve complex problems.
They debate, search the web, and reach a consensus before Timmy summarizes.
Now includes dynamic model scanning to adapt to the user's 
Ollama model list.
"""

import json
import time
import re
import subprocess
from typing import List, Dict, Any, Optional, Generator
from brain import Brain
from tools.web_search import WebSearchTool
from config import AVAILABLE_MODELS

class Council:
    def __init__(self, brain: Brain):
        self.brain = brain
        self.web_search = WebSearchTool()
        self.active_models = self._scan_ollama_models()
        self.debate_history: List[Dict[str, str]] = []
        self.max_rounds = 3 # Keep it manageable to avoid crashing
        self.idle_consensus_time = 20 # seconds of idle to reach consensus

    def _scan_ollama_models(self) -> List[str]:
        """Scan local Ollama models to keep the council list updated."""
        try:
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
            if result.returncode == 0:
                # Parse the output to get model names
                lines = result.stdout.strip().split('\n')[1:] # Skip header
                models = [line.split()[0] for line in lines if line]
                print(f"Council scanned {len(models)} models: {models}")
                return models
        except Exception as e:
            print(f"Error scanning Ollama models: {e}")
        return AVAILABLE_MODELS

    def convene(self, problem: str) -> Generator[Dict[str, Any], None, None]:
        """Convene the council to debate a complex problem."""
        yield {"type": "council_status", "text": f"Council convened for: {problem}"}
        
        self.debate_history = [{"role": "system", "content": f"The problem to solve is: {problem}. Debate among yourselves to find the best solution. You can propose web searches if needed."}]
        
        # Select a subset of models for the debate to avoid crashing
        # We'll pick the top 3-4 models if available
        debate_models = self.active_models[:4]
        
        for round_num in range(1, self.max_rounds + 1):
            yield {"type": "council_status", "text": f"Debate Round {round_num}..."}
            
            for model in debate_models:
                yield {"type": "council_status", "text": f"{model} is speaking..."}
                
                # Build the prompt for the current model
                prompt = f"""
                You are {model}, a member of the Council. 
                The current debate history is:
                {self._format_history()}
                
                Provide your perspective on the problem. 
                If you need more information, propose a web search with SEARCH: [query].
                If you agree with a previous point, state why. 
                If you disagree, provide a counter-argument.
                Be concise and human-like in your debate.
                """
                
                try:
                    response = self.brain.think(prompt, model=model)
                    self.debate_history.append({"role": model, "content": response})
                    
                    # Check for search proposal
                    search_match = re.search(r'SEARCH: \[(.*?)\]', response)
                    if search_match:
                        query = search_match.group(1)
                        yield {"type": "council_status", "text": f"{model} is searching for: {query}"}
                        search_result = self.web_search.execute(query)
                        self.debate_history.append({"role": "system", "content": f"Search result for '{query}': {json.dumps(search_result)}"})
                    
                    yield {"type": "council_debate_chunk", "model": model, "text": response}
                    
                except Exception as e:
                    yield {"type": "council_error", "text": f"Error with model {model}: {e}"}
            
            # Check for consensus (simplified: if models are mostly agreeing)
            if self._check_consensus():
                yield {"type": "council_status", "text": "Consensus reached."}
                break
                
        # Final summary by Timmy
        yield {"type": "council_status", "text": "Timmy is summarizing the council's findings..."}
        summary_prompt = f"""
        You are Timmy. Summarize the following council debate and provide the final solution to the user.
        Debate History:
        {self._format_history()}
        """
        summary = self.brain.think(summary_prompt)
        yield {"type": "council_summary", "text": summary}

    def _format_history(self) -> str:
        """Format the debate history for the prompt."""
        return "\n".join([f"{msg['role']}: {msg['content']}" for msg in self.debate_history])

    def _check_consensus(self) -> bool:
        """Check if the council has reached a consensus (placeholder logic)."""
        # In a real implementation, we'd use an LLM to evaluate consensus
        # For now, we'll just limit the rounds.
        return False
