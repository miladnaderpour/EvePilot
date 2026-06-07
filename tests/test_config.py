from pydantic import SecretStr

from evepilot.core.config import Settings


def test_settings_load_explicit_values() -> None:
    settings = Settings(
        _env_file=None,
        eve_ng_url="http://10.1.2.3",
        eve_ng_username="admin",
        eve_ng_password=SecretStr("eve"),
    )

    assert settings.app_name == "EvePilot"
    assert settings.eve_ng_url == "http://10.1.2.3"
    assert settings.eve_ng_username == "admin"
    assert settings.eve_ng_password.get_secret_value() == "eve"
    assert settings.eve_ng_verify_ssl is False
    assert settings.log_output == "stdout"
    assert settings.log_file_path == "logs/evepilot.log"
    assert settings.log_targets_json is None


def test_settings_load_uppercase_case_sensitive_env(monkeypatch) -> None:
    monkeypatch.setenv("EVEPILOT_EVE_NG_URL", "http://10.1.2.3")
    monkeypatch.setenv("EVEPILOT_EVE_NG_USERNAME", "admin")
    monkeypatch.setenv("EVEPILOT_EVE_NG_PASSWORD", "eve")
    monkeypatch.setenv("EVEPILOT_EVE_NG_VERIFY_SSL", "false")

    settings = Settings(_env_file=None)

    assert settings.eve_ng_url == "http://10.1.2.3"
    assert settings.eve_ng_username == "admin"
    assert settings.eve_ng_password.get_secret_value() == "eve"
    assert settings.eve_ng_verify_ssl is False
    assert Settings.model_config["case_sensitive"] is True
