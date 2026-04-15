"""Build signed Android AAB with passwords loaded from .secrets.toml via Dynaconf."""

import os
import subprocess
import sys
from pathlib import Path

from dynaconf import Dynaconf

PROJECT_ROOT = Path(__file__).resolve().parent.parent

signing = Dynaconf(
    environments=True,
    load_dotenv=False,
    settings_files=[str(PROJECT_ROOT / ".secrets.toml")],
    env="signing",
)

keystore_pwd = signing.get("ANDROID_KEYSTORE_PASSWORD")
key_pwd = signing.get("ANDROID_KEY_PASSWORD")

if not keystore_pwd or not key_pwd:
    sys.exit(
        "Missing signing passwords in .secrets.toml [signing] section:\n"
        "  ANDROID_KEYSTORE_PASSWORD, ANDROID_KEY_PASSWORD"
    )

env = {
    **os.environ,
    "FLET_ANDROID_SIGNING_KEY_STORE_PASSWORD": str(keystore_pwd),
    "FLET_ANDROID_SIGNING_KEY_PASSWORD": str(key_pwd),
}

extra_args = sys.argv[1:] or ["-v"]
cmd = ["fs-build", "aab", *extra_args]

print(f"Running: {' '.join(cmd)}", flush=True)
result = subprocess.run(cmd, cwd=PROJECT_ROOT, env=env)
sys.exit(result.returncode)