from evepilot.eve_ng.client import parse_nodes_response
from evepilot.eve_ng.models import EveNgNode


def test_eve_ng_node_from_api_parses_console_url() -> None:
    node = EveNgNode.from_api(
        {
            "id": "1",
            "name": "CSR-1",
            "status": "2",
            "type": "qemu",
            "url": "telnet://10.1.2.3:32769",
        }
    )

    assert node.id == 1
    assert node.name == "CSR-1"
    assert node.status == 2
    assert node.type == "qemu"
    assert node.console is not None
    assert node.console.host == "10.1.2.3"
    assert node.console.port == 32769


def test_parse_nodes_response_accepts_mapping_payload() -> None:
    nodes = parse_nodes_response(
        {
            "data": {
                "1": {
                    "name": "CSR-1",
                    "status": 2,
                    "type": "qemu",
                    "url": "telnet://10.1.2.3:32769",
                }
            }
        }
    )

    assert len(nodes) == 1
    assert nodes[0].id == 1
    assert nodes[0].name == "CSR-1"


def test_parse_nodes_response_accepts_html5_console_url() -> None:
    nodes = parse_nodes_response(
        {
            "data": {
                "1": {
                    "name": "CSR-1",
                    "status": 2,
                    "type": "qemu",
                    "console": "telnet",
                    "url": "/html5/#/client/MzI3NjkAYwBteXNxbA==?token=example",
                }
            }
        },
        fallback_host="10.1.2.3",
    )

    assert len(nodes) == 1
    assert nodes[0].console is not None
    assert nodes[0].console.protocol == "telnet"
    assert nodes[0].console.host == "10.1.2.3"
    assert nodes[0].console.port == 32769
