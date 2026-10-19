"""Domain Skill Registry and loader for MEIA Knowledge Graph POC.

Parses modular SKILL.md files to dynamically configure routing policies,
Trident visual quotas, LoC reader budgets, epistemic guardrails, and
executive dossier synthesis instructions.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml

from src.config import SKILLS_DIR


@dataclass
class SkillDefinition:
    """Represents a validated domain skill loaded from a SKILL.md file."""
    name: str
    description: str
    route_profiles: List[str]
    guardrails: List[str]
    workflow_steps: List[str]
    parameters: Dict[str, Any]
    sections: Dict[str, str]
    raw_markdown: str
    path: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "route_profiles": self.route_profiles,
            "guardrails": self.guardrails,
            "workflow_steps": self.workflow_steps,
            "parameters": self.parameters,
            "sections": list(self.sections.keys()),
            "path": self.path,
        }


class SkillRegistry:
    """Registry that discovers, parses, and activates domain skill files."""

    def __init__(self, root_dir: Optional[Path] = None):
        self.root_dir = root_dir or SKILLS_DIR
        self._skills: Dict[str, SkillDefinition] = {}
        self.load_all_skills()

    def load_all_skills(self) -> None:
        """Scan SKILLS_DIR for all SKILL.md files and parse them."""
        self._skills.clear()
        if not self.root_dir.is_dir():
            return

        for skill_file in self.root_dir.glob("**/SKILL.md"):
            try:
                skill_def = self._parse_skill_file(skill_file)
                if skill_def:
                    self._skills[skill_def.name] = skill_def
            except Exception as exc:
                # Log or preserve parsing errors without failing entire registry
                print(f"[WARN] Failed to load skill file {skill_file}: {exc}")

    def _parse_skill_file(self, path: Path) -> Optional[SkillDefinition]:
        content = path.read_text(encoding="utf-8")
        frontmatter = {}
        markdown_body = content

        # Check for YAML frontmatter
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                try:
                    frontmatter = yaml.safe_load(parts[1]) or {}
                    markdown_body = parts[2].strip()
                except Exception as exc:
                    print(f"[WARN] YAML parsing failed for {path}: {exc}")

        name = frontmatter.get("name") or path.parent.name
        description = frontmatter.get("description", "")
        route_profiles = frontmatter.get("route_profiles", [])

        # Extract markdown sections by ## Header
        sections: Dict[str, str] = {}
        current_section = "intro"
        current_lines: List[str] = []

        for line in markdown_body.splitlines():
            m = re.match(r"^##\s+(.+)$", line)
            if m:
                if current_lines:
                    sections[current_section] = "\n".join(current_lines).strip()
                    current_lines = []
                current_section = m.group(1).strip().lower()
            else:
                current_lines.append(line)
        if current_lines:
            sections[current_section] = "\n".join(current_lines).strip()

        # Extract bullet points from Guardrails
        guardrails: List[str] = []
        guardrail_text = sections.get("guardrails", "")
        for line in guardrail_text.splitlines():
            line_str = line.strip()
            if line_str.startswith("-") or line_str.startswith("*"):
                guardrails.append(line_str.lstrip("-* ").strip())

        # Extract workflow steps
        workflow_steps: List[str] = []
        workflow_text = sections.get("workflow", "")
        for line in workflow_text.splitlines():
            line_str = line.strip()
            if re.match(r"^\d+\.\s+", line_str) or line_str.startswith("-"):
                workflow_steps.append(re.sub(r"^\d+\.\s+|- \s*", "", line_str).strip())

        # Extract extra parameters from frontmatter
        parameters = {k: v for k, v in frontmatter.items() if k not in {"name", "description", "route_profiles"}}

        return SkillDefinition(
            name=name,
            description=description,
            route_profiles=route_profiles,
            guardrails=guardrails,
            workflow_steps=workflow_steps,
            parameters=parameters,
            sections=sections,
            raw_markdown=content,
            path=str(path),
        )

    def get_skill(self, name: str) -> Optional[SkillDefinition]:
        return self._skills.get(name)

    def list_skills(self) -> List[SkillDefinition]:
        return list(self._skills.values())

    def get_skills_for_route(self, route_profile: str) -> List[SkillDefinition]:
        """Return all skills applicable to a given route profile."""
        matching = []
        for skill in self._skills.values():
            if not skill.route_profiles or route_profile in skill.route_profiles:
                matching.append(skill)
        return matching

    def get_retrieval_parameters(self, route_profile: str) -> Dict[str, Any]:
        """Aggregate retrieval controls (e.g. visual quota, LoC arm) from active skills."""
        params: Dict[str, Any] = {
            "visual_quota": 1,
            "ocr_token_budget": 160,
            "loc_reader_arm": "ARM_C_HYBRID_OCR",
            "native_scope_enabled": True,
            "composed_graph_ops": True,
        }
        for skill in self.get_skills_for_route(route_profile):
            for k, v in skill.parameters.items():
                params[k] = v
        return params

    def build_system_prompt_extension(self, route_profile: str) -> str:
        """Compose skill-derived instruction rules into an authoritative LLM prompt chunk."""
        skills = self.get_skills_for_route(route_profile)
        if not skills:
            return ""

        chunks = ["\n[ACTIVE DOMAIN SKILL RULES & GUARDRAILS]:"]
        for skill in skills:
            chunks.append(f"\n--- SKILL: {skill.name.upper()} ---")
            if skill.description:
                chunks.append(f"Scope: {skill.description}")
            if skill.guardrails:
                chunks.append("Mandatory Guardrails:")
                for g in skill.guardrails:
                    chunks.append(f"  * {g}")
            if skill.workflow_steps:
                chunks.append("Synthesis Guidelines:")
                for step in skill.workflow_steps:
                    chunks.append(f"  * {step}")

        return "\n".join(chunks)


# Global singleton instance
_GLOBAL_SKILL_REGISTRY: Optional[SkillRegistry] = None


def get_skill_registry() -> SkillRegistry:
    global _GLOBAL_SKILL_REGISTRY
    if _GLOBAL_SKILL_REGISTRY is None:
        _GLOBAL_SKILL_REGISTRY = SkillRegistry()
    return _GLOBAL_SKILL_REGISTRY
