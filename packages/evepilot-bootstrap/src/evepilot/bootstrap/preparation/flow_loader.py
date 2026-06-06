"""Bootstrap flow loading."""

from __future__ import annotations

from functools import lru_cache
from importlib.resources import files
from importlib.resources.abc import Traversable
from pathlib import Path
from typing import Any

import yaml

from evepilot.bootstrap.errors import bootstrap_flow_invalid_error
from evepilot.bootstrap.errors import bootstrap_flow_not_found_error
from evepilot.bootstrap.preparation.flow_validator import validate_flow_definition
from evepilot.bootstrap.preparation.models import (
    FlowAction,
    FlowDefinition,
    FlowSummary,
    FlowStartup,
    FlowStateMarker,
    FlowStep,
)
from evepilot.core.logging import get_logger

BUILT_IN_FLOWS_PACKAGE = "evepilot.bootstrap.preparation.flows"
log = get_logger(__name__)


def load_flow(source: str) -> FlowDefinition:
    """Load a bootstrap flow from a built-in name or filesystem path."""

    if source.startswith("built-in:"):
        flow_name = source.removeprefix("built-in:")
        log.debug(
            "bootstrap_flow_load_selected_builtin",
            extra={"flow_name": flow_name},
        )
        return load_builtin_flow(flow_name)
    log.debug("bootstrap_flow_load_selected_path", extra={"source": source})
    return load_flow_from_path(Path(source))


def load_builtin_flow(name: str) -> FlowDefinition:
    """Load a built-in bootstrap flow by name."""

    registry = discover_builtin_flow_resources()
    return _load_builtin_flow_from_registry(name, registry)


def list_builtin_flows() -> list[FlowSummary]:
    """List available built-in bootstrap flows."""

    registry = discover_builtin_flow_resources()
    summaries = [
        _flow_summary_from_resource(name, resource)
        for name, resource in sorted(registry.items())
    ]
    log.debug(
        "bootstrap_builtin_flows_listed",
        extra={"flow_count": len(summaries)},
    )
    return summaries


def read_builtin_flow_text(name: str) -> str:
    """Read the original YAML text for a built-in bootstrap flow."""

    registry = discover_builtin_flow_resources()
    flow_resource = registry.get(name)
    if flow_resource is None:
        raise bootstrap_flow_not_found_error(source=f"built-in:{name}")
    log.debug(
        "bootstrap_builtin_flow_text_read",
        extra={"flow_name": name, "resource": flow_resource.name},
    )
    return _read_resource_text(flow_resource)


def load_builtin_flow_from_package(name: str, package: str) -> FlowDefinition:
    """Load a built-in bootstrap flow from a resource package."""

    registry = discover_builtin_flow_resources_from_package(package)
    return _load_builtin_flow_from_registry(name, registry)


def _load_builtin_flow_from_registry(
    name: str,
    registry: dict[str, Traversable],
) -> FlowDefinition:
    """Load a selected built-in flow resource and validate its public name."""

    flow_resource = registry.get(name)
    if flow_resource is None:
        raise bootstrap_flow_not_found_error(source=f"built-in:{name}")
    log.debug(
        "bootstrap_builtin_flow_load_started",
        extra={"flow_name": name, "resource": flow_resource.name},
    )
    flow = _load_flow_from_resource(flow_resource)
    if flow.name != name:
        raise bootstrap_flow_invalid_error(
            reason="builtin_flow_name_mismatch",
            details={
                "reference": name,
                "flow_name": flow.name,
                "resource": flow_resource.name,
            },
        )
    log.debug(
        "bootstrap_builtin_flow_loaded",
        extra={
            "flow_name": flow.name,
            "version": flow.version,
            "resource": flow_resource.name,
        },
    )
    return flow


@lru_cache(maxsize=1)
def discover_builtin_flow_resources() -> dict[str, Traversable]:
    """Discover built-in YAML flow resources from package resources."""

    return discover_builtin_flow_resources_from_package(BUILT_IN_FLOWS_PACKAGE)


def discover_builtin_flow_resources_from_package(package: str) -> dict[str, Traversable]:
    """Discover built-in YAML flow resources from a resource package."""

    registry: dict[str, Traversable] = {}
    for flow_file in _iter_yaml_resources(files(package)):
        flow_name = _flow_name_from_resource(flow_file)
        if flow_name in registry:
            raise bootstrap_flow_invalid_error(
                reason="duplicate_builtin_flow_name",
                details={"name": flow_name},
            )
        registry[flow_name] = flow_file
    log.debug(
        "bootstrap_builtin_flow_resources_discovered",
        extra={"package": package, "flow_count": len(registry)},
    )
    return registry


def load_flow_from_path(path: Path) -> FlowDefinition:
    """Load a bootstrap flow from a YAML file."""

    if not path.exists():
        raise bootstrap_flow_not_found_error(source=str(path))
    log.debug("bootstrap_flow_file_load_started", extra={"path": str(path)})
    return load_flow_from_text(path.read_text(encoding="utf-8"), source=str(path))


def load_flow_from_text(text: str, *, source: str = "<string>") -> FlowDefinition:
    """Load a bootstrap flow from YAML text."""

    try:
        raw_flow = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise bootstrap_flow_invalid_error(
            reason="invalid_yaml",
            details={"source": source},
        ) from exc

    if not isinstance(raw_flow, dict):
        raise bootstrap_flow_invalid_error(
            reason="invalid_flow_shape",
            details={"source": source},
        )

    flow = _flow_from_mapping(raw_flow)
    validate_flow_definition(flow)
    log.debug(
        "bootstrap_flow_loaded",
        extra={
            "source": source,
            "flow_name": flow.name,
            "version": flow.version,
            "state_count": len(flow.states),
            "step_count": len(flow.steps),
        },
    )
    return flow


def _iter_yaml_resources(resource_root: Traversable) -> list[Traversable]:
    return sorted(
        (
            resource
            for resource in resource_root.iterdir()
            if resource.is_file() and resource.name.endswith((".yaml", ".yml"))
        ),
        key=lambda resource: resource.name,
    )


def _load_flow_from_resource(resource: Traversable) -> FlowDefinition:
    return load_flow_from_text(_read_resource_text(resource), source=str(resource))


def _flow_summary_from_resource(name: str, resource: Traversable) -> FlowSummary:
    flow = _load_flow_from_resource(resource)
    if flow.name != name:
        raise bootstrap_flow_invalid_error(
            reason="builtin_flow_name_mismatch",
            details={
                "reference": name,
                "flow_name": flow.name,
                "resource": resource.name,
            },
        )
    return FlowSummary(
        name=flow.name,
        source="built-in",
        version=flow.version,
        description=flow.description,
    )


def _read_resource_text(resource: Traversable) -> str:
    with resource.open("r", encoding="utf-8") as stream:
        return stream.read()


def _flow_name_from_resource(resource: Traversable) -> str:
    return resource.name.rsplit(".", maxsplit=1)[0]


def _flow_from_mapping(raw_flow: dict[str, Any]) -> FlowDefinition:
    """Convert a raw flow mapping into a flow definition."""

    try:
        name = str(raw_flow["name"])
        version = int(raw_flow["version"])
    except KeyError as exc:
        raise bootstrap_flow_invalid_error(
            reason="missing_required_field",
            details={"field": str(exc)},
        ) from exc

    raw_states = raw_flow.get("states", {})
    raw_steps = raw_flow.get("steps", [])
    if not isinstance(raw_states, dict):
        raise bootstrap_flow_invalid_error(reason="invalid_states_shape")
    if not isinstance(raw_steps, list):
        raise bootstrap_flow_invalid_error(reason="invalid_steps_shape")

    return FlowDefinition(
        name=name,
        version=version,
        description=_optional_str(raw_flow.get("description")),
        startup=_startup_from_mapping(raw_flow.get("startup", {})),
        variables=_dict_or_empty(raw_flow.get("variables", {})),
        states={
            state_name: _state_marker_from_mapping(state_name, raw_marker)
            for state_name, raw_marker in raw_states.items()
        },
        steps=[_step_from_mapping(raw_step) for raw_step in raw_steps],
    )


def _startup_from_mapping(raw_startup: object) -> FlowStartup:
    if raw_startup is None:
        return FlowStartup()
    if not isinstance(raw_startup, dict):
        raise bootstrap_flow_invalid_error(reason="invalid_startup_shape")
    return FlowStartup(
        initial_read_seconds=float(raw_startup.get("initial_read_seconds", 3.0)),
        send_enter_if_no_output=bool(raw_startup.get("send_enter_if_no_output", True)),
        wake_enter=str(raw_startup.get("wake_enter", "\r\n")),
        wake_attempts=int(raw_startup.get("wake_attempts", 3)),
        read_after_wake_seconds=float(raw_startup.get("read_after_wake_seconds", 2.0)),
    )


def _state_marker_from_mapping(
    state_name: str,
    raw_marker: object,
) -> FlowStateMarker:
    if not isinstance(raw_marker, dict):
        raise bootstrap_flow_invalid_error(
            reason="invalid_state_marker_shape",
            details={"state_name": state_name},
        )
    return FlowStateMarker(
        name=state_name,
        patterns=_string_list(raw_marker.get("patterns", [])),
        regex=_string_list(raw_marker.get("regex", [])),
    )


def _step_from_mapping(raw_step: object) -> FlowStep:
    if not isinstance(raw_step, dict):
        raise bootstrap_flow_invalid_error(reason="invalid_step_shape")
    try:
        name = str(raw_step["name"])
        action = FlowAction(str(raw_step["action"]))
    except KeyError as exc:
        raise bootstrap_flow_invalid_error(
            reason="missing_required_field",
            details={"field": str(exc)},
        ) from exc
    except ValueError as exc:
        raise bootstrap_flow_invalid_error(
            reason="unsupported_action",
            details={"action": raw_step.get("action")},
        ) from exc

    return FlowStep(
        name=name,
        action=action,
        when_state=_optional_str(raw_step.get("when_state")),
        send=_optional_str(raw_step.get("send")),
        send_secret=_optional_str(raw_step.get("send_secret")),
        expect=_optional_str(raw_step.get("expect")),
        expect_regex=_optional_str(raw_step.get("expect_regex")),
        timeout_seconds=int(raw_step.get("timeout_seconds", 30)),
        optional=bool(raw_step.get("optional", False)),
        next=_optional_str(raw_step.get("next")),
        mark_ready=bool(raw_step.get("mark_ready", False)),
    )


def _string_list(value: object) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise bootstrap_flow_invalid_error(reason="expected_string_list")
    return [str(item) for item in value]


def _dict_or_empty(value: object) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise bootstrap_flow_invalid_error(reason="expected_mapping")
    return value


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    return str(value)
