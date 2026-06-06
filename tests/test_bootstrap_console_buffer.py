from evepilot.bootstrap.preparation.console_buffer import ConsoleBuffer


def test_console_buffer_appends_completed_lines_and_partial_prompt() -> None:
    buffer = ConsoleBuffer()

    buffer.append("Router booting\r\nEnter enable")
    buffer.append(" secret:")

    assert buffer.lines == ["Router booting\r\n"]
    assert buffer.partial == "Enter enable secret:"
    assert buffer.text() == "Router booting\r\nEnter enable secret:"


def test_console_buffer_recent_text_limits_completed_lines() -> None:
    buffer = ConsoleBuffer()

    buffer.append("one\r\ntwo\r\nthree\r\nRouter>")

    assert buffer.recent_text(max_lines=2) == "two\r\nthree\r\nRouter>"


def test_console_buffer_clear_completed_lines_preserves_partial_prompt() -> None:
    buffer = ConsoleBuffer()
    buffer.append("old line\r\nPassword:")

    buffer.clear_completed_lines()

    assert buffer.text() == "Password:"


def test_console_buffer_clear_drops_all_output() -> None:
    buffer = ConsoleBuffer()
    buffer.append("old line\r\nPassword:")

    buffer.clear()

    assert buffer.text() == ""
