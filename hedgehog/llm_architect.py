from __future__ import annotations

import json
import os
import re

from hedgehog.architect import _make_deterministic_plan_graph
from hedgehog.architect_prompt_compiler import build_plan_graph_response_schema
from hedgehog.architect_prompt_compiler import compile_architect_prompt


class GeminiArchitectError(RuntimeError):
    def __init__(
        self,
        message: str,
        used_llm: bool = False,
        warnings: list[str] | None = None,
    ):
        super().__init__(message)
        self.used_llm = used_llm
        self.warnings = warnings or []


def _config_value(*names: str, allow_config: bool = True) -> str | None:
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    if not allow_config:
        return None
    try:
        import config  # type: ignore
    except ImportError:
        return None
    for name in names:
        value = getattr(config, name, None)
        if value:
            return value
    return None


def _strip_markdown_fences(text: str) -> str:
    stripped = text.strip()
    match = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", stripped, flags=re.DOTALL)
    if match:
        return match.group(1).strip()
    return stripped


def _parse_and_validate_plan_graph(text: str, attractor_packet: dict) -> dict:
    if not text.strip():
        raise ValueError("Gemini Architect returned an empty response.")
    plan_graph = json.loads(_strip_markdown_fences(text))
    validate_plan_graph_contract(plan_graph, attractor_packet)
    return plan_graph


def _retry_prompt(prompt_contract: dict, validation_error: str) -> str:
    return (
        f"{prompt_contract['user_prompt']}\n\n"
        "The previous PlanGraph JSON failed local contract validation.\n"
        f"Validation error: {validation_error}\n"
        "Return corrected PlanGraph JSON only.\n"
        "Do not include markdown.\n"
        "Do not add unsupported top-level fields.\n"
        "All edges must be objects with \"from\" and \"to\".\n"
    )


def _generate_content(client, model_name: str, prompt: str, generation_config: dict):
    try:
        return client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=generation_config,
        )
    except TypeError:
        return client.models.generate_content(
            model=model_name,
            contents=prompt,
        )


def _assert_plan_graph_uses_allowed_vectors(plan_graph: dict, attractor_packet: dict) -> None:
    allowed = {vector["vector_id"] for vector in attractor_packet.get("candidate_vectors", [])}
    for node in plan_graph.get("nodes", []):
        if node.get("vector_id") not in allowed:
            raise ValueError(f"PlanGraph node uses disallowed vector_id: {node.get('vector_id')}")
    forbidden_text = json.dumps(plan_graph, sort_keys=True).lower()
    for key in ("final_output", "raw_user_text"):
        if key in forbidden_text:
            raise ValueError(f"PlanGraph contains forbidden key/text: {key}")


def validate_plan_graph_contract(
    plan_graph: dict,
    attractor_packet: dict | None = None,
) -> None:
    if not isinstance(plan_graph, dict):
        raise ValueError("invalid_plan_graph_contract: plan_graph must be an object")

    required = {
        "plan_id",
        "source_packet_id",
        "time_assumptions",
        "nodes",
        "edges",
        "executor_assignments",
    }
    if attractor_packet and attractor_packet.get("request_id"):
        required.add("request_id")
    missing = sorted(required - set(plan_graph))
    if missing:
        raise ValueError(
            f"invalid_plan_graph_contract: missing required fields: {', '.join(missing)}"
        )

    nodes = plan_graph.get("nodes")
    if not isinstance(nodes, list) or not nodes:
        raise ValueError("invalid_plan_graph_contract: nodes must be a non-empty array")

    allowed_vector_ids = None
    if attractor_packet is not None:
        allowed_vector_ids = {
            vector["vector_id"]
            for vector in attractor_packet.get("candidate_vectors", [])
        }

    node_ids = set()
    for index, node in enumerate(nodes):
        if not isinstance(node, dict):
            raise ValueError(f"invalid_plan_graph_contract: node {index} must be an object")
        node_required = {
            "node_id",
            "vector_id",
            "task",
            "executor_id",
            "depends_on",
            "expected_output",
        }
        node_missing = sorted(node_required - set(node))
        if node_missing:
            raise ValueError(
                "invalid_plan_graph_contract: "
                f"node {index} missing required fields: {', '.join(node_missing)}"
            )
        if allowed_vector_ids is not None and node["vector_id"] not in allowed_vector_ids:
            raise ValueError(
                f"invalid_plan_graph_contract: disallowed vector_id: {node['vector_id']}"
            )
        if not isinstance(node["depends_on"], list):
            raise ValueError("invalid_plan_graph_contract: node depends_on must be an array")
        node_ids.add(node["node_id"])

    if not isinstance(plan_graph.get("edges"), list):
        raise ValueError("invalid_plan_graph_contract: edges must be an array")
    for edge in plan_graph["edges"]:
        if not isinstance(edge, dict) or "from" not in edge or "to" not in edge:
            raise ValueError("invalid_plan_graph_contract: edge must include from and to")
        if edge["from"] not in node_ids or edge["to"] not in node_ids:
            raise ValueError("invalid_plan_graph_contract: edge references unknown node")

    assignments = plan_graph.get("executor_assignments")
    if not isinstance(assignments, list) or not assignments:
        raise ValueError(
            "invalid_plan_graph_contract: executor_assignments must be a non-empty array"
        )
    assigned = set()
    for assignment in assignments:
        if not isinstance(assignment, dict):
            raise ValueError("invalid_plan_graph_contract: executor assignment must be an object")
        for field in ("executor_id", "node_ids", "mode"):
            if field not in assignment:
                raise ValueError(
                    f"invalid_plan_graph_contract: executor assignment missing {field}"
                )
        if not isinstance(assignment["node_ids"], list):
            raise ValueError("invalid_plan_graph_contract: assignment node_ids must be an array")
        assigned.update(assignment["node_ids"])
    if not assigned.issubset(node_ids):
        raise ValueError("invalid_plan_graph_contract: assignment references unknown node")

    adjacency = {node_id: [] for node_id in node_ids}
    for edge in plan_graph["edges"]:
        source = edge["from"]
        target = edge["to"]
        if source == target:
            raise ValueError(
                "invalid_plan_graph_contract: local PlanGraph must be a DAG; cycle/self-loop detected"
            )
        adjacency[source].append(target)

    visited = set()
    active = set()

    def visit(node_id: str) -> None:
        if node_id in active:
            raise ValueError(
                "invalid_plan_graph_contract: local PlanGraph must be a DAG; cycle detected"
            )
        if node_id in visited:
            return
        active.add(node_id)
        for child in adjacency[node_id]:
            visit(child)
        active.remove(node_id)
        visited.add(node_id)

    for node_id in node_ids:
        visit(node_id)

    forbidden_text = json.dumps(plan_graph, sort_keys=True).lower()
    for key in ("final_output", "answer", "raw_user_text"):
        if key in forbidden_text:
            raise ValueError(f"invalid_plan_graph_contract: forbidden key/text: {key}")


def _gemini_plan_graph(
    attractor_packet: dict,
    model: str | None,
    allow_config: bool,
) -> tuple[dict, str, list[str]]:
    api_key = _config_value(
        "GEMINI_API_KEY",
        "GOOGLE_API_KEY",
        "GOOGLE_GEMINI_API_KEY",
        allow_config=allow_config,
    )
    if not api_key:
        if allow_config:
            raise GeminiArchitectError(
                "Gemini API key is missing from environment or local config.py.",
                used_llm=False,
            )
        raise GeminiArchitectError(
            "Gemini API key is missing from environment and config lookup is disabled."
            ,
            used_llm=False,
        )

    model_name = model or _config_value("GEMINI_MODEL", allow_config=allow_config) or "gemini-3.5-flash"
    try:
        from google import genai  # type: ignore
    except ImportError as exc:
        raise GeminiArchitectError(
            "Gemini dependency is missing: google-genai.",
            used_llm=False,
        ) from exc

    prompt_contract = compile_architect_prompt(attractor_packet)
    generation_config = {
        "response_mime_type": "application/json",
        "response_json_schema": build_plan_graph_response_schema(),
    }
    client = genai.Client(api_key=api_key)
    try:
        response = _generate_content(
            client,
            model_name,
            prompt_contract["user_prompt"],
            {
                **generation_config,
                "system_instruction": prompt_contract["system_prompt"],
            },
        )
        first_text = getattr(response, "text", "") or ""
        plan_graph = _parse_and_validate_plan_graph(first_text, attractor_packet)
    except Exception as exc:
        first_error = str(exc)
        try:
            retry_response = _generate_content(
                client,
                model_name,
                _retry_prompt(prompt_contract, first_error),
                {
                    **generation_config,
                    "system_instruction": prompt_contract["system_prompt"],
                },
            )
            retry_text = getattr(retry_response, "text", "") or ""
            plan_graph = _parse_and_validate_plan_graph(retry_text, attractor_packet)
        except Exception as retry_exc:
            raise GeminiArchitectError(
                str(retry_exc),
                used_llm=True,
                warnings=["retry_failed"],
            ) from retry_exc
        return plan_graph, model_name, ["retry_applied"]
    return plan_graph, model_name, []


def make_plan_graph_with_llm(
    *,
    attractor_packet: dict,
    provider: str = "mock",
    model: str | None = None,
    allow_config: bool = True,
) -> dict:
    prompt_contract = compile_architect_prompt(attractor_packet)
    if provider == "mock":
        plan_graph = _make_deterministic_plan_graph(attractor_packet)
        validate_plan_graph_contract(plan_graph, attractor_packet)
        return {
            "status": "completed",
            "provider": "mock",
            "model": model or "mock_architect_v1",
            "used_llm": False,
            "plan_graph": plan_graph,
            "error": None,
            "warnings": [],
            "prompt_contract": prompt_contract,
        }

    if provider != "gemini":
        return {
            "status": "error",
            "provider": provider,
            "model": model or "unknown",
            "used_llm": False,
            "plan_graph": None,
            "error": f"Unsupported Architect provider: {provider}",
            "warnings": ["unsupported_provider"],
            "fallback": "deterministic",
            "prompt_contract": prompt_contract,
        }

    try:
        plan_graph, model_name, warnings = _gemini_plan_graph(
            attractor_packet,
            model,
            allow_config,
        )
    except GeminiArchitectError as exc:
        return {
            "status": "error",
            "provider": "gemini",
            "model": model or _config_value("GEMINI_MODEL", allow_config=allow_config) or "gemini-3.5-flash",
            "used_llm": exc.used_llm,
            "plan_graph": None,
            "error": str(exc),
            "warnings": ["gemini_architect_unavailable", *exc.warnings],
            "fallback": "deterministic",
            "prompt_contract": prompt_contract,
        }
    except Exception as exc:
        return {
            "status": "error",
            "provider": "gemini",
            "model": model or _config_value("GEMINI_MODEL", allow_config=allow_config) or "gemini-3.5-flash",
            "used_llm": False,
            "plan_graph": None,
            "error": str(exc),
            "warnings": ["gemini_architect_unavailable"],
            "fallback": "deterministic",
            "prompt_contract": prompt_contract,
        }

    return {
        "status": "completed",
        "provider": "gemini",
        "model": model_name,
        "used_llm": True,
        "plan_graph": plan_graph,
        "error": None,
        "warnings": warnings,
        "prompt_contract": prompt_contract,
    }
