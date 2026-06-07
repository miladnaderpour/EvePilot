"""Bootstrap preparation variable resolution."""

from __future__ import annotations

import os
import re
from collections.abc import Mapping
from typing import Any

from evepilot.bootstrap.errors import bootstrap_flow_run_error
from evepilot.bootstrap.preparation.models import FlowDefinition
from evepilot.core.logging import get_logger

ENV_PREFIX = "EVEPILOT_BOOTSTRAP_"

log = get_logger(__name__)


def resolve_flow_variables(
    flow: FlowDefinition,
    *,
    environ: Mapping[str, str] | None = None,
) -> dict[str, str]:
    """Resolve flow variables from environment variables."""

    env = environ or os.environ
    resolved: dict[str, str] = {}

    for variable_name, raw_definition in flow.variables.items():
        definition = _variable_definition(variable_name, raw_definition)
        env_name = variable_env_name(variable_name)
        value = env.get(env_name)

        if value is None:
            if definition["required"]:
                log.error(
                    "bootstrap_flow_variable_missing",
                    extra={
                        "flow_name": flow.name,
                        "variable_name": variable_name,
                        "env_name": env_name,
                    },
                )
                raise bootstrap_flow_run_error(
                    reason="missing_variable",
                    details={
                        "flow_name": flow.name,
                        "variable": variable_name,
                        "env_name": env_name,
                    },
                )

            log.debug(
                "bootstrap_flow_variable_not_set",
                extra={
                    "flow_name": flow.name,
                    "variable_name": variable_name,
                    "env_name": env_name,
                },
            )
            continue

        resolved[variable_name] = value
        log.debug(
            "bootstrap_flow_variable_resolved",
            extra={
                "flow_name": flow.name,
                "variable_name": variable_name,
                "env_name": env_name,
                "secret": definition["secret"],
            },
        )

    return resolved


def variable_env_name(variable_name: str) -> str:
    """Return the environment variable name for a flow variable."""

    normalized = re.sub(r"[^A-Za-z0-9]+", "_", variable_name).strip("_").upper()
    return f"{ENV_PREFIX}{normalized}"


def _variable_definition(variable_name: str, raw_definition: object) -> dict[str, bool]:
    if raw_definition is None:
        return {"required": False, "secret": False}

    if not isinstance(raw_definition, dict):
        raise bootstrap_flow_run_error(
            reason="invalid_variable_definition",
            details={"variable": variable_name},
        )

    return {
        "required": _bool_field(raw_definition, "required", variable_name),
        "secret": _bool_field(raw_definition, "secret", variable_name),
    }


def _bool_field(
    raw_definition: Mapping[Any, Any],
    field_name: str,
    variable_name: str,
) -> bool:
    value = raw_definition.get(field_name, False)
    if not isinstance(value, bool):
        raise bootstrap_flow_run_error(
            reason="invalid_variable_definition",
            details={"variable": variable_name, "field": field_name},
        )
    return value
