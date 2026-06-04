"""EVE-NG-specific errors and error factories."""

from evepilot.core.exceptions import EvePilotError


class EveNgError(EvePilotError):
    """Base error for EVE-NG integration failures."""


class EveNgApiError(EveNgError):
    """EVE-NG API request or response error."""


class EveNgAuthError(EveNgApiError):
    """EVE-NG authentication error."""


class EveNgNotFoundError(EveNgError):
    """EVE-NG resource not found error."""


class EveNgConsoleError(EveNgApiError):
    """EVE-NG console endpoint error."""


def auth_failed_error(*, status_code: int) -> EveNgAuthError:
    """Build the error used when EVE-NG authentication fails."""

    return EveNgAuthError(
        code="eve_ng.auth_failed",
        message="Failed to authenticate to EVE-NG.",
        details={"status_code": status_code},
        status_code=status_code,
    )


def request_failed_error(*, lab_path: str, status_code: int) -> EveNgApiError:
    """Build the error used when an EVE-NG API request fails."""

    return EveNgApiError(
        code="eve_ng.request_failed",
        message="Failed to fetch EVE-NG lab nodes.",
        details={"lab_path": lab_path, "status_code": status_code},
        status_code=status_code,
    )


def invalid_response_error() -> EveNgApiError:
    """Build the error used when an EVE-NG response has an unsupported shape."""

    return EveNgApiError(
        code="eve_ng.invalid_response",
        message="EVE-NG nodes response has an unsupported shape.",
    )


def lab_not_found_error(*, lab_path: str) -> EveNgNotFoundError:
    """Build the error used when an EVE-NG lab cannot be found."""

    return EveNgNotFoundError(
        code="eve_ng.lab_not_found",
        message="EVE-NG lab was not found.",
        details={"lab_path": lab_path},
        status_code=404,
    )


def node_not_found_error(*, lab_path: str, node_name: str) -> EveNgNotFoundError:
    """Build the error used when an EVE-NG node cannot be found."""

    return EveNgNotFoundError(
        code="eve_ng.node_not_found",
        message="EVE-NG node was not found.",
        details={"lab_path": lab_path, "node_name": node_name},
        status_code=404,
    )


def console_url_missing_error(*, lab_path: str, node_name: str) -> EveNgConsoleError:
    """Build the error used when a node has no console URL."""

    return EveNgConsoleError(
        code="eve_ng.console_url_missing",
        message="EVE-NG node does not have a console URL.",
        details={"lab_path": lab_path, "node_name": node_name},
    )


def console_url_invalid_error(*, url: str, reason: str) -> EveNgConsoleError:
    """Build the error used when a console URL cannot be parsed."""

    return EveNgConsoleError(
        code="eve_ng.console_url_invalid",
        message=f"Console URL is invalid: {reason}.",
        details={"url": url, "reason": reason},
    )
