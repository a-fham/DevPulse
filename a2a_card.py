from pydantic import BaseModel
from typing import List


class Skill(BaseModel):
    id: str
    description: str
    tags: List[str]


class AgentCard(BaseModel):
    name: str
    description: str
    version: str
    endpoint: str
    skills: List[Skill]


DEVPULSE_CARD = AgentCard(
    name="DevPulse",
    description="Agentic GitHub intelligence assistant backed by a real MCP server.",
    version="1.0.0",
    endpoint="http://localhost:9001/devpulse",
    skills=[
        Skill(
            id="repo_info",
            description="Look up live stats, search, and contributors for a GitHub repository",
            tags=["github", "repository", "stars", "contributors", "search"],
        ),
        Skill(
            id="issue_triage",
            description="List and triage open issues for a GitHub repository",
            tags=["github", "issues", "triage", "bugs"],
        ),
        Skill(
            id="release_notes",
            description="Get the latest release/version info for a GitHub repository",
            tags=["github", "release", "version", "changelog"],
        ),
    ],
)


class AgentRegistry:
    def __init__(self):
        self.agents: list[AgentCard] = []

    def register(self, card: AgentCard):
        self.agents.append(card)

    def discover(self, tag: str) -> list[str]:
        return [a.name for a in self.agents for s in a.skills if tag in s.tags]


def demo():
    registry = AgentRegistry()
    registry.register(DEVPULSE_CARD)

    print("Registered agents:")
    for a in registry.agents:
        print(f"  - {a.name}: {[s.id for s in a.skills]}")

    print("\nAn external agent searching for who can triage GitHub issues:")
    matches = registry.discover("triage")
    print(f"  discover('triage') -> {matches}")

    print("\nAn external agent searching for release/version info:")
    matches = registry.discover("release")
    print(f"  discover('release') -> {matches}")

    print("\nFull card as published (this is all an external agent ever sees):")
    print(DEVPULSE_CARD.model_dump_json(indent=2))


if __name__ == "__main__":
    demo()
