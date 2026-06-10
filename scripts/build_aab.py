"""Build a signed Android AAB, keeping real secrets out of the shipped bundle.

`flet build` packages the whole project directory into `app.zip` (inside the apk/aab)
and does NOT honor `.gitignore`. The real `.secrets.toml` holds build-time signing
passwords and, on dev machines, runtime tokens — none of which may ship.

This script:
  1. reads the signing passwords from the real `.secrets.toml` (Dynaconf, [signing]);
  2. swaps `.secrets.toml` for a sanitized copy (same keys, empty values) only while
     the build runs, so the bundled file satisfies the app's Dynaconf validator
     (GITHUB_TOKEN must_exist) without leaking any value;
  3. restores the real file afterwards, no matter how the build ends.

The keystore (`upload-keystore.jks`) and the backup are excluded from the package via
`[tool.flet.app].exclude` in pyproject.toml; Gradle still reads the keystore from disk.
"""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from dynaconf import Dynaconf

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SECRETS_PATH = PROJECT_ROOT / ".secrets.toml"
# Kept in the project root (persistent crash recovery) and excluded from the bundle
# via pyproject [tool.flet.app].exclude.
SECRETS_BACKUP = PROJECT_ROOT / ".secrets.toml.bak"

# Release signing. flet only configures release signing when the keystore PATH is
# provided (FLET_ANDROID_SIGNING_KEY_STORE); with only the passwords set it silently
# falls back to the debug keystore, which the Play Console rejects. The keystore is
# excluded from the app package but stays on disk for Gradle to sign with.
KEYSTORE_PATH = PROJECT_ROOT / "upload-keystore.jks"
KEY_ALIAS = "upload"

# Match a `KEY = value` assignment so its value can be blanked. Section headers
# (`[default]`), comments (`#...`) and blank lines are left untouched, preserving the
# structure Dynaconf reads while shipping no real values.
_ASSIGNMENT_RE = re.compile(r"^(\s*[^#\s\[][^=]*?)\s*=\s*\S.*$")


def _sanitize_toml(text: str) -> str:
    """Return `text` with every assignment's value replaced by an empty string."""
    out = []
    for line in text.splitlines(keepends=True):
        suffix = "\n" if line.endswith("\n") else ""
        match = _ASSIGNMENT_RE.match(line.rstrip("\n"))
        out.append(f'{match.group(1)} = ""{suffix}' if match else line)
    return "".join(out)


def _read_signing_passwords() -> tuple[str, str]:
    signing = Dynaconf(
        environments=True,
        load_dotenv=False,
        settings_files=[str(SECRETS_PATH)],
        env="signing",
    )
    keystore_pwd = signing.get("ANDROID_KEYSTORE_PASSWORD")
    key_pwd = signing.get("ANDROID_KEY_PASSWORD")
    if not keystore_pwd or not key_pwd:
        sys.exit(
            "Missing signing passwords in .secrets.toml [signing] section:\n"
            "  ANDROID_KEYSTORE_PASSWORD, ANDROID_KEY_PASSWORD"
        )
    return str(keystore_pwd), str(key_pwd)


def main() -> int:
    # Recover the real file if a previous run was killed mid-build.
    if SECRETS_BACKUP.exists():
        print(f"Recovering real {SECRETS_PATH.name} from {SECRETS_BACKUP.name}", flush=True)
        shutil.move(SECRETS_BACKUP, SECRETS_PATH)

    if not KEYSTORE_PATH.exists():
        sys.exit(f"Release keystore not found: {KEYSTORE_PATH}")

    keystore_pwd, key_pwd = _read_signing_passwords()

    env = {
        **os.environ,
        # Path + alias are required for release signing — without the path flet
        # debug-signs the bundle and the Play Console rejects it.
        "FLET_ANDROID_SIGNING_KEY_STORE": str(KEYSTORE_PATH),
        "FLET_ANDROID_SIGNING_KEY_ALIAS": KEY_ALIAS,
        "FLET_ANDROID_SIGNING_KEY_STORE_PASSWORD": keystore_pwd,
        "FLET_ANDROID_SIGNING_KEY_PASSWORD": key_pwd,
    }

    extra_args = sys.argv[1:] or ["-v"]
    cmd = ["fs-build", "aab", *extra_args]
    print(f"Running: {' '.join(cmd)}", flush=True)

    real_secrets = SECRETS_PATH.read_text(encoding="utf-8")
    shutil.copy2(SECRETS_PATH, SECRETS_BACKUP)
    try:
        # Expose only the sanitized copy to the packager.
        SECRETS_PATH.write_text(_sanitize_toml(real_secrets), encoding="utf-8")
        result = subprocess.run(cmd, cwd=PROJECT_ROOT, env=env)
        return result.returncode
    finally:
        # Restore the real file (move overwrites the sanitized copy and drops the backup).
        shutil.move(SECRETS_BACKUP, SECRETS_PATH)


if __name__ == "__main__":
    sys.exit(main())
