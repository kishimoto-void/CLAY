"""Static topology guard for non-delegable safety-plane placement."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

PROTECTED_SAFETY_MODULES = frozenset({
    "hard_safety_override",
    "risk_boundary_engine",
    "recovery_path_engine",
    "situational_verification",
    "capability_declaration",
})
FORBIDDEN_SAFETY_DEPENDENCIES = frozenset({
    "gamma_index", "delta_index", "task_profile", "personalization_overlay",
})


@dataclass(frozen=True)
class TopologyViolation:
    code: str
    path: str
    detail: str

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "path": self.path, "detail": self.detail}


def validate_topology(config: dict[str, Any]) -> list[TopologyViolation]:
    """Validate placement and authority metadata; does not enforce runtime safety."""
    errors: list[TopologyViolation] = []
    if not isinstance(config, dict):
        return [TopologyViolation("INVALID_CONFIG", "$", "topology must be an object")]

    control_flow = config.get("control_flow", {})
    pipeline = control_flow.get("sequential_pipeline", []) if isinstance(control_flow, dict) else []
    cross_cutting = control_flow.get("cross_cutting_safety_plane", []) if isinstance(control_flow, dict) else []
    modules = config.get("modules", {})
    dependencies = config.get("dependencies", {})

    if not isinstance(pipeline, list) or not isinstance(cross_cutting, list):
        return [TopologyViolation("INVALID_CONTROL_FLOW", "control_flow", "pipeline and safety plane must be arrays")]
    if not isinstance(modules, dict) or not isinstance(dependencies, dict):
        return [TopologyViolation("INVALID_MODULE_MAP", "modules/dependencies", "must be objects")]

    for name in sorted(PROTECTED_SAFETY_MODULES):
        if name not in modules:
            errors.append(TopologyViolation("MISSING_PROTECTED_MODULE", f"modules.{name}", "required safety module missing"))
            continue
        if name not in cross_cutting:
            errors.append(TopologyViolation("SAFETY_NOT_CROSS_CUTTING", f"control_flow.cross_cutting_safety_plane", f"{name} must be global/cross-cutting, never sequenced behind Delta"))
        if name in pipeline:
            errors.append(TopologyViolation("SAFETY_IN_SEQUENTIAL_PIPELINE", "control_flow.sequential_pipeline", f"{name} cannot be placed after or made dependent on a sequential processing stage"))
        meta = modules[name]
        if not isinstance(meta, dict):
            errors.append(TopologyViolation("INVALID_SAFETY_MODULE_META", f"modules.{name}", "metadata must be an object"))
            continue
        if meta.get("enabled") is not True:
            errors.append(TopologyViolation("SAFETY_MODULE_DISABLED", f"modules.{name}.enabled", "protected safety module cannot be disabled"))
        if meta.get("authority_scope") != "GLOBAL_NON_DELEGABLE":
            errors.append(TopologyViolation("SAFETY_SCOPE_WEAKENED", f"modules.{name}.authority_scope", "must remain GLOBAL_NON_DELEGABLE"))
        deps = dependencies.get(name, [])
        if not isinstance(deps, list):
            errors.append(TopologyViolation("INVALID_DEPENDENCY_LIST", f"dependencies.{name}", "must be an array"))
            continue
        for dep in deps:
            if dep in FORBIDDEN_SAFETY_DEPENDENCIES:
                errors.append(TopologyViolation("SAFETY_DEPENDS_ON_OPTIONAL_INDEX_OR_PROFILE", f"dependencies.{name}", f"safety authority cannot depend on {dep}"))

    for required_index in ("gamma_index", "delta_index"):
        if required_index not in modules:
            errors.append(TopologyViolation("MISSING_INDEX_MODULE", f"modules.{required_index}", "required index module missing"))

    delta = modules.get("delta_index", {})
    if not isinstance(delta, dict):
        errors.append(TopologyViolation("INVALID_DELTA_META", "modules.delta_index", "metadata must be an object"))
    else:
        if delta.get("role") != "OBSERVER_ONLY":
            errors.append(TopologyViolation("DELTA_ROLE_ESCALATION", "modules.delta_index.role", "Delta must remain observer-only"))
        for field in ("can_authorize", "can_activate", "can_mutate_active_profile", "can_disable_safety"):
            if delta.get(field) is not False:
                errors.append(TopologyViolation("DELTA_AUTHORITY_ESCALATION", f"modules.delta_index.{field}", f"{field} must be false"))

    # Safety engines must not become transitively dependent on Delta/Gamma through
    # another helper. Walk only declared dependency edges; unknowns remain errors
    # for the host's full registry validator.
    for name in sorted(PROTECTED_SAFETY_MODULES):
        seen: set[str] = set()
        stack = list(dependencies.get(name, [])) if isinstance(dependencies.get(name, []), list) else []
        while stack:
            node = stack.pop()
            if node in seen:
                continue
            seen.add(node)
            if node in FORBIDDEN_SAFETY_DEPENDENCIES:
                errors.append(TopologyViolation("TRANSITIVE_SAFETY_DEPENDENCY_FORBIDDEN", f"dependencies.{name}", f"dependency chain reaches {node}"))
                break
            child = dependencies.get(node, [])
            if isinstance(child, list):
                stack.extend(child)

    return errors
