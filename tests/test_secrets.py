import base64
import os
import secrets
import subprocess
import sys
import tomllib

import pytest

from scripts.check_secrets import check_config, encrypted_value
from scripts.secrets_init import initialize


@pytest.fixture
def secret_workspace(tmp_path):
    config = tmp_path / "fnox.toml"
    config.write_text(
        'default_provider = "age"\n[providers.age]\ntype = "age"\nrecipients = []\n[secrets]\n'
    )
    key = tmp_path / "identity" / "age.txt"
    env = {"PATH": os.environ["PATH"]}
    env.update(FNOX_CONFIG_DIR=str(tmp_path / "fnox-config"), FNOX_AGE_KEY_FILE=str(key))
    return config, key, env


def test_initialization_preserves_existing_identity(secret_workspace):
    config, key, _ = secret_workspace
    assert initialize(config, key)
    original_key, original_config = key.read_bytes(), config.read_bytes()
    assert not initialize(config, key)
    assert key.read_bytes() == original_key
    assert config.read_bytes() == original_config
    assert key.stat().st_mode & 0o777 == 0o600


def test_different_recipient_is_not_silently_added(secret_workspace, tmp_path):
    config, key, _ = secret_workspace
    initialize(config, key)
    original = config.read_bytes()
    with pytest.raises(ValueError, match="existing recipients preserved"):
        initialize(config, tmp_path / "different-age.txt")
    assert config.read_bytes() == original


def test_fnox_round_trip_and_batch_format(secret_workspace):
    config, key, env = secret_workspace
    initialize(config, key)
    sample = secrets.token_urlsafe(32)
    prefix = ["fnox", "--no-daemon", "--non-interactive", "-c", str(config)]

    def call(args, input=None):
        result = subprocess.run(
            [*prefix, *args],
            cwd=config.parent,
            env=env,
            input=input,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        assert result.returncode == 0, "fnox operation failed (output suppressed to protect values)"
        assert sample not in result.stdout + result.stderr
        return result

    call(["set", "MICRT_SYNTHETIC", "--provider", "age"], input=sample)
    individual = tomllib.loads(config.read_text())["secrets"]["MICRT_SYNTHETIC"]["value"]
    assert base64.b64decode(individual).startswith(b"age-encryption.org/v1\n")
    assert check_config(tomllib.loads(config.read_text()))
    env["MICRT_EXPECTED"] = sample
    call(
        [
            "exec",
            "--",
            sys.executable,
            "-c",
            "import os; assert os.environ['MICRT_SYNTHETIC'] == os.environ['MICRT_EXPECTED']",
        ]
    )
    call(["reencrypt", "--provider", "age", "--force"])
    document = tomllib.loads(config.read_text())
    value = document["secrets"]["MICRT_SYNTHETIC"]["value"]
    assert value.startswith("fnox-age-batch-v1:")
    assert check_config(document)
    call(
        [
            "exec",
            "--",
            sys.executable,
            "-c",
            "import os; assert os.environ['MICRT_SYNTHETIC'] == os.environ['MICRT_EXPECTED']",
        ]
    )
    assert sample not in config.read_text()


@pytest.mark.parametrize(
    "entry",
    [
        "plain",
        {"value": "plain", "provider": "age"},
        {"default": "plain"},
        {"provider": "unregistered", "value": "opaque"},
    ],
)
def test_plaintext_and_unknown_providers_rejected(entry):
    config = {"providers": {"age": {"type": "age"}}, "secrets": {"EXAMPLE": entry}}
    assert not check_config(config)
    assert not check_config({"profiles": {"test": config}})


@pytest.mark.parametrize(
    "value", [None, "", "not base64", "fnox-age-batch-v1:bad:bad", "fnox-age-batch-v1:"]
)
def test_malformed_ciphertext_rejected(value):
    assert not encrypted_value(value)
