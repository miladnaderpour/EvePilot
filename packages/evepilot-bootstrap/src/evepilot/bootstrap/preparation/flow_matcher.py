"""Flow-defined state matching."""

from __future__ import annotations

import re

from evepilot.bootstrap.errors import bootstrap_flow_ambiguous_state_error
from evepilot.bootstrap.preparation.models import FlowDefinition, FlowStateMatch
from evepilot.core.logging import get_logger

DEFAULT_SAMPLE_LIMIT = 2000
log = get_logger(__name__)


def detect_flow_state(output: str, flow: FlowDefinition) -> FlowStateMatch | None:
    """Detect a flow-defined state from console output."""

    sample = _sample_output(output)
    matches: list[tuple[int, FlowStateMatch]] = []
    log.debug(
        "bootstrap_flow_matcher_detection_started",
        extra={
            "flow_name": flow.name,
            "output_length": len(output),
            "state_count": len(flow.states),
        },
    )

    for state_name, marker in flow.states.items():
        for pattern in marker.patterns:
            position = output.rfind(pattern)
            if position >= 0:
                log.debug(
                    "bootstrap_flow_matcher_plain_pattern_matched",
                    extra={
                        "flow_name": flow.name,
                        "state_name": state_name,
                        "position": position,
                        "pattern": pattern,
                    },
                )
                matches.append(
                    (
                        position,
                        FlowStateMatch(
                            state_name=state_name,
                            matched_pattern=pattern,
                            matched_text=pattern,
                            is_regex=False,
                            sample=sample,
                        ),
                    )
                )

        for regex_pattern in marker.regex:
            regex_matches = list(re.finditer(regex_pattern, output, re.MULTILINE))
            if regex_matches:
                position = regex_matches[-1].start()
                matched_text = regex_matches[-1].group(0)
                log.debug(
                    "bootstrap_flow_matcher_regex_pattern_matched",
                    extra={
                        "flow_name": flow.name,
                        "state_name": state_name,
                        "position": position,
                        "pattern": regex_pattern,
                        "matched_text": matched_text,
                    },
                )
                matches.append(
                    (
                        position,
                        FlowStateMatch(
                            state_name=state_name,
                            matched_pattern=regex_pattern,
                            matched_text=matched_text,
                            is_regex=True,
                            sample=sample,
                        ),
                    )
                )

    if not matches:
        log.debug(
            "bootstrap_flow_matcher_no_state_matched",
            extra={
                "flow_name": flow.name,
                "output_length": len(output),
                "sample": sample,
            },
        )
        return None

    latest_position = max(position for position, _ in matches)
    latest_matches = [
        match for position, match in matches if position == latest_position
    ]
    matched_state_names = sorted({match.state_name for match in latest_matches})
    if len(matched_state_names) > 1:
        log.warning(
            "bootstrap_flow_matcher_ambiguous_state_matched",
            extra={
                "flow_name": flow.name,
                "state_names": matched_state_names,
                "sample": sample,
            },
        )
        raise bootstrap_flow_ambiguous_state_error(
            state_names=matched_state_names,
            sample=sample,
        )
    selected_match = latest_matches[0]
    log.debug(
        "bootstrap_flow_matcher_state_selected",
        extra={
            "flow_name": flow.name,
            "state_name": selected_match.state_name,
            "is_regex": selected_match.is_regex,
            "matched_pattern": selected_match.matched_pattern,
            "matched_text": selected_match.matched_text,
            "position": latest_position,
        },
    )
    return selected_match


def _sample_output(output: str) -> str:
    if len(output) <= DEFAULT_SAMPLE_LIMIT:
        return output
    return output[-DEFAULT_SAMPLE_LIMIT:]
