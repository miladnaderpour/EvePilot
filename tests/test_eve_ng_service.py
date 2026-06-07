import pytest

from evepilot.core.models import ConsoleEndpoint
from evepilot.eve_ng.errors import EveNgConsoleError
from evepilot.eve_ng.models import EveNgNode
from evepilot.eve_ng.service import get_node, get_node_console, list_nodes


class FakeEveNgClient:
    def __init__(self, nodes: list[EveNgNode]) -> None:
        self.nodes = nodes

    def get_lab_nodes(self, lab_path: str) -> list[EveNgNode]:
        return self.nodes

    def get_node_by_name(self, lab_path: str, node_name: str) -> EveNgNode:
        for node in self.nodes:
            if node.name == node_name:
                return node
        raise AssertionError(f"Unexpected node lookup: {node_name}")


def test_list_nodes_returns_public_schema() -> None:
    result = list_nodes(
        eve_ng_client=FakeEveNgClient([_node()]),  # type: ignore[arg-type]
        lab_path="EIGRP/Basics.unl",
    )

    assert result.nodes[0].name == "CSR-1"
    assert result.nodes[0].console is not None
    assert result.nodes[0].console.port == 32769


def test_get_node_returns_public_schema() -> None:
    result = get_node(
        eve_ng_client=FakeEveNgClient([_node()]),  # type: ignore[arg-type]
        lab_path="EIGRP/Basics.unl",
        node_name="CSR-1",
    )

    assert result.name == "CSR-1"
    assert result.console is not None
    assert result.console.host == "10.1.2.3"


def test_get_node_console_returns_console_schema() -> None:
    result = get_node_console(
        eve_ng_client=FakeEveNgClient([_node()]),  # type: ignore[arg-type]
        lab_path="EIGRP/Basics.unl",
        node_name="CSR-1",
    )

    assert result.node == "CSR-1"
    assert result.console.protocol == "telnet"


def test_get_node_console_rejects_node_without_console() -> None:
    with pytest.raises(EveNgConsoleError) as exc_info:
        get_node_console(
            eve_ng_client=FakeEveNgClient([EveNgNode(id=1, name="CSR-1")]),  # type: ignore[arg-type]
            lab_path="EIGRP/Basics.unl",
            node_name="CSR-1",
        )

    assert exc_info.value.code == "eve_ng.console_url_missing"


def _node() -> EveNgNode:
    return EveNgNode(
        id=1,
        name="CSR-1",
        status=2,
        type="qemu",
        url="telnet://10.1.2.3:32769",
        console=ConsoleEndpoint(protocol="telnet", host="10.1.2.3", port=32769),
    )
