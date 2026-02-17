"""
council.py

This module implements the 'Council' system for the Timmy AI agent.
When activated, it queries all available local Ollama models with the same problem,
collects their responses, and then uses the main model to synthesize a combined, best answer.
"""

from typing import List, Dict, Any
from brain import Brain
from config import DEFAULT_MAIN_MODEL, AVAILABLE_MODELS

class Council:
    """
    The Council system orchestrates multiple model queries and synthesizes their responses.
    """

    def __init__(self, brain: Brain):
        self.brain = brain
        self.available_council_models: List[str] = [model for model in AVAILABLE_MODELS if model != DEFAULT_MAIN_MODEL]
        print(f"Council initialized with {len(self.available_council_models)} members.")

    def convene(self, problem_statement: str) -> str:
        """
        Convenes the council to address a complex or uncertain problem.
        Each council member (model) provides an answer, which are then synthesized by the main model.
        """
        print("Council convened for problem:\n" + problem_statement)
        member_responses: Dict[str, str] = {}

        # Query each council member
        for model_name in self.available_council_models:
            print(f"Querying council member: {model_name}...")
            try:
                response = self.brain.think(problem_statement, model=model_name)
                member_responses[model_name] = response
                print(f"Response from {model_name} received.")
            except Exception as e:
                member_responses[model_name] = f"Error: {e}"
                print(f"Error querying {model_name}: {e}")

        # Synthesize responses using the main model
        synthesis_prompt = self._create_synthesis_prompt(problem_statement, member_responses)
        print("Synthesizing council responses with main model...")
        final_answer = self.brain.think(synthesis_prompt, model=DEFAULT_MAIN_MODEL)
        print("Council synthesis complete.")
        return final_answer

    def _create_synthesis_prompt(self, problem: str, responses: Dict[str, str]) -> str:
        """
        Constructs the prompt for the main model to synthesize council members' responses.
        """
        prompt = f"""The following problem was presented to a council of AI models:

Problem: {problem}

Here are their individual responses:

"""
        for model, response in responses.items():
            prompt += f"""--- Model: {model} ---
{response}

"""
        prompt += f"""Based on these responses, please synthesize the best, most comprehensive, and accurate answer to the problem. Identify any common themes, conflicting points, and provide a well-reasoned final conclusion.
"""
        return prompt

