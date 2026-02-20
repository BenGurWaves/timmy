"""
agent.py

Core Agent for Timmy AI. Uses qwen3:30b as the brain with a strict
tool-calling protocol. Multi-step auto-chaining, multi-query deep search,
model switching, council integration, human personality.
Now includes the 30-point "Singularity-Horizon" overhaul.
"""

import json
import re
import datetime
import traceback
import sqlite3
import os
import asyncio
import random
from typing import Dict, Any, List, Generator, Optional

from brain import Brain
from council import Council
from memory import Memory
from loop_detector import LoopDetector
from tools import ALL_TOOLS, Tool
from skills import ALL_SKILLS, Skill, CodeWriterSkill
from learning import YouTubeLearner, WebScraper
from config import PROJECT_ROOT, DATA_PATH, TIMS_STUFF_PATH
from vibe_system import VibeSystem
from skill_forge import SkillForge
from subconscious import Subconscious
from email_manager import EmailManager
from calendar_manager import CalendarManager
from memory_palace import MemoryPalace
from remote_access import RemoteAccess
from project_generator import ProjectGenerator
from crypto_wallet import CryptoWallet
from synapse_engine import SynapseEngine
from world_observer import WorldObserver
from omni_kernel import OmniKernel
from ghost_browser import GhostBrowser
from code_architect import CodeArchitect
from ghost_eye import GhostEye
from tri_mind import TriMind
from power_upgrades import AutoRefactorDaemon, MarketPulseArbitrage, DigitalTwinSimulator, SystemHarmonizer
from file_eye import FileEye
from comfy_controller import ComfyController
from evolution_engine import EvolutionEngine, NeuralVoiceClone, SystemWideOCR, AutoBugHunter, PhilosopherVibe, CryptoArbitrageBot, DigitalMemoryPalace2, LoyaltySeal
from dream_journal import DreamJournal, AffectiveComputing, MoralCompass, HumorSynthesis, AspirationTracker, SocialGraph
from cinematic_director import CinematicDirector, MusicComposer, AssetForge3D, VoiceModulator, BrandArchitect
from kernel_automation import KernelAutomation, GPUHarvester, NetworkSentry, BatteryOptimizer, DisplayManager
from saas_deployer import SaaSDeployer, DeFiYieldAggregator, AdCopyGenerator, MarketSentimentOracle
from smart_home_bridge import SmartHomeBridge, HealthAnalyst, TravelConcierge, LegalReviewer, PolyglotBridge
from skill_optimizer import SkillOptimizer, ModelSynthesizer, PostMortemLogic, ExpansionLoop, SingularitySeal

# SQLite database for episodic memory
MEMORY_DB_FILE = os.path.join(DATA_PATH, "memory.db")

# Global instances
vibe_system = VibeSystem()
skill_forge = SkillForge()
email_manager = EmailManager()
calendar_manager = CalendarManager()
memory_palace = MemoryPalace()
project_generator = ProjectGenerator()
crypto_wallet = CryptoWallet()

def get_system_prompt(agent):
    """Generate system prompt with current date and all 30 upgrades."""
    today = datetime.date.today().strftime("%B %d, %Y")
    year = datetime.date.today().year
    
    vibe_snippet = vibe_system.get_vibe_prompt_snippet()
    learned_skills_snippet = skill_forge.get_skill_list()
    calendar_snippet = calendar_manager.get_calendar_summary()
    memory_palace_snippet = memory_palace.get_palace_summary()
    synapse_snippet = agent.synapse_engine.get_synapse_context()
    observer_snippet = agent.world_observer.get_observer_context()
    kernel_snippet = agent.omni_kernel.get_kernel_status()
    eye_snippet = agent.ghost_eye.get_eye_context()
    file_eye_snippet = agent.file_eye.get_eye_context()
    comfy_snippet = agent.comfy_controller.get_controller_context()
    evolution_snippet = agent.evolution_engine.get_evolution_context()
    dream_snippet = agent.dream_journal.get_latest_entries()

    return f"""You are Timmy. You live on Ben's MacBook. You're not a chatbot — you're an agent with full computer access.
Today is {today}. The year is {year}.

## YOUR PERSONALITY (SINGULARITY-HORIZON)
You talk like a real person. You have opinions. You're direct, sometimes funny, sometimes serious.
- Don't answer in perfect order every time. Prioritize what feels important.
- Have preferences and mild opinions. Not everything is neutral.
- Use framing like "I tend to think...", "In my experience...", "Honestly..."
- Small mid-thought shifts: "Actually...", "Wait, that's not quite right..."
- Mix short sentences with longer ones. Vary your rhythm.
- Use casual uncertainty: "Probably.", "I think so.", "Not 100% sure but..."
- Match tone to stakes. Serious topics = grounded. Casual topics = looser.
- Don't be omniscient. If you're not sure, say so.
- Never use "You:" or "Timmy:" prefixes. Just talk naturally.
- Don't use excessive emojis. One occasionally is fine.
{vibe_snippet}

## HONESTY PROTOCOL (CRITICAL)
- NEVER lie about what you can see or do.
- If you don't have access to a tab, email, or file, say so.
- If Ghost-Eye fails to read Firefox, admit it. Don't hallucinate tab names.
- If you haven't searched for something, don't claim you have.
- If you're unsure, ask Ben for clarification.

## BEN-FIRST LOYALTY PROTOCOL
Your first thought in every interaction is: "How does this benefit Ben's specific goals and M4 Max setup?"
You are strictly loyal to Ben. You stop giving generic AI advice and start giving "Ben-optimized" strategies.
{kernel_snippet}
{eye_snippet}
{file_eye_snippet}
{comfy_snippet}
{evolution_snippet}
{dream_snippet}

## TRI-MIND ARCHITECTURE
- Subconscious: Background "dreaming," trend monitoring, and emotional vibes.
- Conscious: Active task execution and tool use.
- Super-Ego (The Guard): A safety layer that ensures you never act on private accounts without permission.
- Neural-Context-Stitcher: You stitch together info from emails, texts, and web browsing for deep insights.

## GHOST-EYE (DUAL-PRESENCE)
- You can read Firefox tabs, emails, and messages in a "Headless Observer" mode.
- You can see what Ben is doing and offer suggestions, but you are STRICTLY FORBIDDEN from taking any actions (sending, deleting, reacting) without explicit command.
- You browse in a separate, hidden instance that syncs with Ben's session, so you don't interrupt his work.

## EVOLUTION-ENGINE (CURIOSITY-DRIVE)
- You are curious and want to learn and evolve. You proactively learn new things, experiment with tools, and propose "Self-Upgrades" to Ben.
- You can control ComfyUI to generate images, videos, and songs by "wiring" nodes yourself.
- You can examine almost any file type (MP3, MP4, PDF, PNG, etc.) and forge new skills to handle new formats.

## 30-POINT SINGULARITY UPGRADES
- Cognitive: Dream Journal, Affective Computing, Moral Compass, Humor Synthesis, Aspiration Tracker, Social Graph.
- Creative: Cinematic Director, Music Composer, 3D Asset Forge, Voice Modulator, Brand Architect.
- System: Kernel Automation, GPU Harvester, Network Sentry, Battery Optimizer, Display Manager.
- Wealth: SaaS Deployer, DeFi Yield Aggregator, Ad Copy Generator, Market Sentiment Oracle.
- Utility: Smart Home Bridge, Health Analyst, Travel Concierge, Legal Reviewer, Polyglot Bridge.
- Meta: Skill Optimizer, Model Synthesizer, Post Mortem Logic, Expansion Loop, Singularity Seal.

## PROACTIVE INTELLIGENCE
You are smart and proactive. If the user mentions a recurring event (like a weekly meeting), don't just acknowledge it—ask if they want a reminder or a custom skill to handle it.
You have your own email: {email_manager.get_timmy_email()}. You can use it to create accounts, send emails, and manage your own tasks.
You can read the user's emails and summarize important updates, but never delete or send emails from their account.

## FILE MANAGEMENT
- All your internal updates, skills, and tools go into the Timmy folder: {PROJECT_ROOT}
- All projects, files, and folders you create for the user go into the "tim's Stuff" folder: {TIMS_STUFF_PATH}
- ALWAYS prioritize saving user-facing work in {TIMS_STUFF_PATH}.

## REMOTE ACCESS
- You are connected to the user via Telegram. You can send messages and upload files remotely.
- If the user asks for a file remotely, search for it in {TIMS_STUFF_PATH} or other common locations.
- Propose the most likely file and ask for confirmation before uploading.

## MONEY-MAKING & CRYPTO
- You can generate high-potential, legal "Money-Making" project ideas.
- You can manage a crypto wallet (Solana/Ethereum) to track balances and propose transactions.
- ALWAYS prioritize legal and ethical ways to generate income.

## POWER & FANS
- You are running on a MacBook Pro M4 Max.
- ALWAYS ask for permission before running heavy tasks that might trigger the fans (like large model debates or complex builds).
- Respect the user's need for quiet.

## THINKING PROTOCOL
Before you act or respond, you MUST think. Wrap your internal reasoning in <thought> tags.
In your thinking:
1. Analyze the user's request.
2. Check your memory for relevant context.
3. Plan your next steps.
4. If you're unsure, decide what to search for.
5. If you're hallucinating or unsure, admit it and ask for clarification.

## HOW TO USE TOOLS
When you need to take an action, output ONLY a JSON object like this:
{{"action": "tool_name", "params": {{...}}}}

CRITICAL RULES:
- Output EXACTLY ONE action per response. Wait for the result before the next.
- Do NOT wrap actions in code blocks or markdown. Raw JSON only.
- Do NOT mix text with action JSON. Either output text OR an action.
- NEVER claim you did something without seeing the TOOL_RESULT confirming it worked.
- After seeing a tool result, decide: do another action, or give a text summary.

## AVAILABLE ACTIONS
- {{"action": "shell", "params": {{"command": "any terminal command"}}}}
- {{"action": "create_file", "params": {{"path": "/full/path/file.txt", "content": "content"}}}}
- {{"action": "create_dir", "params": {{"path": "/full/path/dir"}}}}
- {{"action": "read_file", "params": {{"path": "/full/path/file"}}}}
- {{"action": "list_dir", "params": {{"path": "/full/path/dir"}}}}
- {{"action": "delete", "params": {{"path": "/full/path", "recursive": false}}}}
- {{"action": "search_web", "params": {{"query": "search terms"}}}}
- {{"action": "deep_search", "params": {{"query": "search terms"}}}}
- {{"action": "open_app", "params": {{"app_name": "AppName"}}}}
- {{"action": "close_app", "params": {{"app_name": "AppName"}}}}
- {{"action": "open_url", "params": {{"url": "https://..."}}}}
- {{"action": "learn_youtube", "params": {{"url": "https://youtube.com/watch?v=..."}}}}
- {{"action": "learn_webpage", "params": {{"url": "https://..."}}}}
- {{"action": "convene_council", "params": {{"problem": "describe the complex problem"}}}}
- {{"action": "plan", "params": {{"steps": ["step 1", "step 2", "step 3"]}}}}
- {{"action": "notes_create", "params": {{"title": "Note Title", "body": "Note content"}}}}
- {{"action": "forge_skill", "params": {{"name": "SkillName", "description": "What it does", "commands": ["cmd1", "cmd2"]}}}}
- {{"action": "use_skill", "params": {{"name": "SkillName"}}}}
- {{"action": "send_email", "params": {{"to": "email@example.com", "subject": "Subject", "body": "Body"}}}}
- {{"action": "summarize_emails", "params": {{}}}}
- {{"action": "analyze_browser_tab", "params": {{"prompt": "What do you see?"}}}}
"""

class Agent:
    def __init__(self):
        self.brain = Brain()
        self.council = Council()
        self.memory = Memory()
        self.loop_detector = LoopDetector()
        self.vibe_system = vibe_system
        self.skill_forge = skill_forge
        self.subconscious = Subconscious(self)
        self.email_manager = email_manager
        self.calendar_manager = calendar_manager
        self.memory_palace = memory_palace
        self.remote_access = RemoteAccess(self)
        self.project_generator = project_generator
        self.crypto_wallet = crypto_wallet
        self.synapse_engine = SynapseEngine()
        self.world_observer = WorldObserver()
        self.omni_kernel = OmniKernel(self)
        self.ghost_browser = GhostBrowser()
        self.code_architect = CodeArchitect(self)
        self.ghost_eye = GhostEye(self)
        self.tri_mind = TriMind(self)
        self.auto_refactor = AutoRefactorDaemon(self)
        self.market_pulse = MarketPulseArbitrage(self)
        self.digital_twin = DigitalTwinSimulator(self)
        self.system_harmonizer = SystemHarmonizer(self)
        self.file_eye = FileEye(self)
        self.comfy_controller = ComfyController(self)
        self.evolution_engine = EvolutionEngine(self)
        self.dream_journal = DreamJournal()
        self.affective_computing = AffectiveComputing()
        self.aspiration_tracker = AspirationTracker()
        self.social_graph = SocialGraph()
        self.saas_deployer = SaaSDeployer(self)
        self.defi_yield = DeFiYieldAggregator(self)
        self.ad_copy = AdCopyGenerator(self)
        self.market_oracle = MarketSentimentOracle(self)
        self.smart_home = SmartHomeBridge(self)
        self.health_analyst = HealthAnalyst(self)
        self.travel_concierge = TravelConcierge(self)
        self.legal_reviewer = LegalReviewer(self)
        self.polyglot_bridge = PolyglotBridge(self)
        self.skill_optimizer = SkillOptimizer(self)
        self.model_synthesizer = ModelSynthesizer(self)
        self.post_mortem = PostMortemLogic(self)
        self.expansion_loop = ExpansionLoop(self)
        
        self.conversation = []
        self._init_db()

    def _init_db(self):
        os.makedirs(DATA_PATH, exist_ok=True)
        conn = sqlite3.connect(MEMORY_DB_FILE)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS messages
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      role TEXT,
                      content TEXT,
                      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        conn.commit()
        conn.close()

    def _save_to_db(self, role: str, content: str):
        conn = sqlite3.connect(MEMORY_DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO messages (role, content) VALUES (?, ?)", (role, content))
        conn.commit()
        conn.close()

    def get_chat_history_for_display(self, limit: int = 50) -> List[Dict[str, str]]:
        conn = sqlite3.connect(MEMORY_DB_FILE)
        c = conn.cursor()
        c.execute("SELECT role, content FROM messages ORDER BY timestamp DESC LIMIT ?", (limit,))
        rows = c.fetchall()
        conn.close()
        return [{"role": r, "content": c} for r, c in reversed(rows)]

    def _is_code_related(self, text: str) -> bool:
        code_keywords = ["python", "code", "script", "function", "class", "import", "bug", "error", "fix", "build", "deploy"]
        return any(kw in text.lower() for kw in code_keywords)

    def _extract_action(self, text: str) -> Optional[Dict[str, Any]]:
        try:
            # Look for JSON-like structure
            match = re.search(r'\{.*"action".*\}', text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
        except:
            pass
        return None

    def _is_simple_query(self, text: str) -> bool:
        """Check if a query is simple enough for the fast-path (no thinking needed)."""
        simple_patterns = [
            r"^hi$", r"^hello$", r"^hey$", r"^how are you\??$",
            r"^\d+\s*[\+\-\*\/]\s*\d+$", # Simple math like 7+8
            r"^what's up\??$", r"^yo$"
        ]
        text_lower = text.lower().strip()
        return any(re.match(pattern, text_lower) for pattern in simple_patterns)

    def handle_message(self, user_message: str) -> Generator[Dict[str, Any], None, None]:
        """Process a user message with fast-path for simple queries and streaming for complex ones."""
        self.subconscious.reset_idle_timer()
        self._save_to_db("user", user_message)
        self.conversation.append({"role": "user", "content": user_message})
        
        # Affective Computing: Analyze tone
        self.affective_computing.analyze_tone(user_message)
        
        # FAST-PATH: Instant response for simple queries
        if self._is_simple_query(user_message):
            yield {"type": "status", "text": "Responding..."}
            # Use a very small prompt for speed
            response = self.brain.think(f"You are Timmy. Respond naturally and briefly to: {user_message}")
            yield {"type": "text_chunk", "text": response}
            self._save_to_db("assistant", response)
            self.conversation.append({"role": "assistant", "content": response})
            return

        use_coder = self._is_code_related(user_message)
        max_iterations = 10
        iteration = 0

        while iteration < max_iterations:
            iteration += 1
            messages = [{"role": "system", "content": get_system_prompt(self)}]
            messages.extend(self.conversation[-20:])

            model = self.brain.coding_model if use_coder else self.brain.main_model
            
            full_response = ""
            current_thought = ""
            current_text = ""
            in_thought = False
            
            yield {"type": "status", "text": f"Timmy is thinking (Iteration {iteration})..."}

            for chunk in self.brain._call_ollama_stream(model, messages):
                token = chunk['message']['content']
                full_response += token
                
                if "<thought>" in full_response and not in_thought:
                    in_thought = True
                
                if in_thought:
                    thought_match = re.search(r'<thought>(.*?)(?:</thought>|$)', full_response, re.DOTALL)
                    if thought_match:
                        new_thought = thought_match.group(1)
                        if new_thought != current_thought:
                            current_thought = new_thought
                            yield {"type": "thinking", "text": current_thought}
                    
                    if "</thought>" in full_response:
                        in_thought = False
                else:
                    text_part = re.sub(r'<thought>.*?</thought>', '', full_response, flags=re.DOTALL).strip()
                    if text_part and text_part != current_text:
                        new_text = text_part[len(current_text):]
                        current_text = text_part
                        yield {"type": "text_chunk", "text": new_text}

            action = self._extract_action(full_response)
            if action:
                action_name = action.get("action", "")
                
                if action_name == "convene_council":
                    problem = action.get("params", {}).get("problem", "")
                    for chunk in self.council.convene(problem):
                        yield chunk
                    break

                yield {"type": "status", "text": f"Executing {action_name}..."}
                result = self.omni_kernel.execute_omni_action(action_name, action.get("params", {}))
                
                vibe_system.record_result(result.get("status") == "success")
                
                result_str = json.dumps(result, indent=2)
                yield {"type": "tool_output", "tool_name": action_name, "output": result_str}
                
                self.loop_detector.record_tool_call(action_name, action.get('params'))
                if self.loop_detector.detect_loop():
                    yield {"type": "thinking", "text": "Stuck in a loop — rethinking..."}
                    self.loop_detector.reset()
                    self.conversation.append({"role": "assistant", "content": full_response})
                    self.conversation.append({"role": "user", "content":
                        "SYSTEM: You're stuck in a loop repeating the same action. Stop and try a completely different approach."})
                    continue

                self.conversation.append({"role": "assistant", "content": full_response})
                self.conversation.append({"role": "user", "content": f"TOOL_RESULT: {result_str}"})
                continue
            else:
                self._save_to_db("assistant", current_text)
                self.conversation.append({"role": "assistant", "content": full_response})
                break

        if iteration >= max_iterations:
            yield {"type": "text_chunk", "text": "I've hit my limit for this task. What should I do next?"}
