import datetime
import pytest
from app.agent import FerramentasDeArquivo, app, get_instruction, root_agent


def test_agent_and_app_initialization():
    assert root_agent.name == "agente_estudos"
    assert app.name == "app"
    assert app.root_agent == root_agent


def test_instruction_provider_contains_today():
    hoje = datetime.date.today().strftime("%Y-%m-%d")
    inst = get_instruction()
    assert hoje in inst
    assert "plano-de-estudos" in inst


@pytest.mark.asyncio
async def test_tools_exposure():
    canonical_tools = await root_agent.canonical_tools(None)
    tool_names = [t.name for t in canonical_tools]

    # Skill tools
    assert "load_skill" in tool_names
    assert "load_skill_resource" in tool_names

    # File tools (only ReadFile and WriteFile, no Execute or EditFile)
    assert "ReadFile" in tool_names
    assert "WriteFile" in tool_names
    assert "Execute" not in tool_names
    assert "EditFile" not in tool_names
