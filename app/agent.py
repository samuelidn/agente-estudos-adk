import datetime
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.environment import LocalEnvironment
from google.adk.models import Gemini
from google.adk.skills import load_skill_from_dir
from google.adk.tools.environment import EnvironmentToolset
from google.adk.tools.skill_toolset import SkillToolset
from google.genai import types

load_dotenv()

# Caminhos absolutos para a pasta de planos e para a skill
BASE_DIR = Path(__file__).resolve().parent.parent
PLANOS_DIR = BASE_DIR / "planos"
PLANOS_DIR.mkdir(parents=True, exist_ok=True)
SKILL_DIR = Path(__file__).resolve().parent / "skills" / "plano-de-estudos"


class FerramentasDeArquivo(EnvironmentToolset):
    """Subclasse do EnvironmentToolset que expõe exclusivamente ReadFile e WriteFile."""

    async def get_tools(self, readonly_context: Any = None):
        tools = await super().get_tools(readonly_context)
        return [t for t in tools if t.name in ("ReadFile", "WriteFile")]


# Configuração dos toolsets
skill = load_skill_from_dir(SKILL_DIR)
skill_toolset = SkillToolset(skills=[skill])
file_toolset = FerramentasDeArquivo(environment=LocalEnvironment(working_dir=PLANOS_DIR))


def get_instruction(context: Any = None) -> str:
    """Instruction provider dinâmico que injeta a data atual."""
    hoje = datetime.date.today().strftime("%Y-%m-%d")
    return (
        "Você é um mentor especialista em estudos responsável por criar e gerenciar planos de estudo personalizados.\n"
        f"A data de hoje é {hoje}. Use esta data como referência para interpretar prazos relativos como 'hoje', 'amanhã' ou 'segunda que vem'.\n"
        "Use a skill 'plano-de-estudos' para guiar sua interação com o usuário, respeitando rigorosamente suas regras de ativação e fluxo de trabalho."
    )


MODEL = os.getenv("MODEL", "gemini-3.8-flash")

root_agent = Agent(
    name="agente_estudos",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=get_instruction,
    tools=[skill_toolset, file_toolset],
)

app = App(
    root_agent=root_agent,
    name="app",
)
