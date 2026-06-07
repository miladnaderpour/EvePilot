"""Public EVE-NG service use cases."""

from evepilot.eve_ng.client import EveNgClient
from evepilot.eve_ng.errors import console_url_missing_error
from evepilot.eve_ng.schemas import (
    EveNgConsoleEndpoint,
    EveNgNodeConsoleResult,
    EveNgNodeResult,
    EveNgNodesResult,
)


def list_nodes(*, eve_ng_client: EveNgClient, lab_path: str) -> EveNgNodesResult:
    """List nodes in an EVE-NG lab."""

    return EveNgNodesResult(
        nodes=[
            EveNgNodeResult.from_domain(node)
            for node in eve_ng_client.get_lab_nodes(lab_path)
        ]
    )


def get_node(
    *,
    eve_ng_client: EveNgClient,
    lab_path: str,
    node_name: str,
) -> EveNgNodeResult:
    """Return one EVE-NG node by name."""

    return EveNgNodeResult.from_domain(
        eve_ng_client.get_node_by_name(lab_path, node_name)
    )


def get_node_console(
    *,
    eve_ng_client: EveNgClient,
    lab_path: str,
    node_name: str,
) -> EveNgNodeConsoleResult:
    """Return one EVE-NG node console endpoint."""

    node = eve_ng_client.get_node_by_name(lab_path, node_name)
    if node.console is None:
        raise console_url_missing_error(lab_path=lab_path, node_name=node_name)

    return EveNgNodeConsoleResult(
        node=node.name,
        console=EveNgConsoleEndpoint.from_domain(node.console),
    )
