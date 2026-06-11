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

# Build-time Dynaconf environment marker. `--env <name>` writes this module into the
# bundle so the packaged app resolves that env at runtime (mobile has no OS env vars, so
# ENV_FOR_DYNACONF can't do it). config.py imports it; absent -> default/test AdMob IDs.
# It MUST ship (not excluded in pyproject), is generated per build, and is .gitignored.
BUILD_ENV_PATH = PROJECT_ROOT / "_build_env.py"

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


# Environments defined in settings.toml / .secrets.toml. A typo here (e.g. "prod") would
# silently ship the wrong env's config — exactly the bug this whole mechanism prevents —
# so an unknown value is a hard error.
KNOWN_ENVS = frozenset({"development", "homologation", "production", "testing", "mobile"})


def _extract_env_flag(argv: list[str]) -> tuple[str | None, list[str]]:
    """Pull `--env <name>` / `--env=<name>` out of argv; return (env, remaining args)."""
    env: str | None = None
    rest: list[str] = []
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--env":
            if i + 1 >= len(argv):
                sys.exit("--env requires a value, e.g. --env production")
            env, i = argv[i + 1], i + 2
            continue
        if arg.startswith("--env="):
            env, i = arg.split("=", 1)[1], i + 1
            continue
        rest.append(arg)
        i += 1
    if env is not None and env not in KNOWN_ENVS:
        sys.exit(f"Unknown --env '{env}'. Known: {', '.join(sorted(KNOWN_ENVS))}")
    return env, rest


def main() -> int:
    # Recover the real file if a previous run was killed mid-build.
    if SECRETS_BACKUP.exists():
        print(f"Recovering real {SECRETS_PATH.name} from {SECRETS_BACKUP.name}", flush=True)
        shutil.move(SECRETS_BACKUP, SECRETS_PATH)
    # A marker left by a crashed release build would otherwise leak production config
    # (real AdMob IDs) into the next test build. Always start from a clean slate.
    if BUILD_ENV_PATH.exists():
        print(f"Removing stale {BUILD_ENV_PATH.name} from a previous run", flush=True)
        BUILD_ENV_PATH.unlink()

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

    app_env, passthrough = _extract_env_flag(sys.argv[1:])
    extra_args = passthrough or ["-v"]
    cmd = ["fs-build", "aab", *extra_args]
    if app_env:
        print(f"Dynaconf env baked into bundle: '{app_env}' ({BUILD_ENV_PATH.name})", flush=True)
    else:
        print("No --env: bundle uses default/development env (Google TEST AdMob IDs)", flush=True)
    print(f"Running: {' '.join(cmd)}", flush=True)

    real_secrets = SECRETS_PATH.read_text(encoding="utf-8")
    shutil.copy2(SECRETS_PATH, SECRETS_BACKUP)
    try:
        # Expose only the sanitized copy to the packager.
        SECRETS_PATH.write_text(_sanitize_toml(real_secrets), encoding="utf-8")
        # Bake the runtime env into the bundle (release builds only). config.py imports
        # this module to pick the Dynaconf env on device.
        if app_env:
            BUILD_ENV_PATH.write_text(
                '"""Generated by scripts/build_aab.py — do not edit or commit."""\n'
                f'APP_ENV = "{app_env}"\n',
                encoding="utf-8",
            )
        result = subprocess.run(cmd, cwd=PROJECT_ROOT, env=env)
        return result.returncode
    finally:
        # Restore the real file (move overwrites the sanitized copy and drops the backup).
        shutil.move(SECRETS_BACKUP, SECRETS_PATH)
        # Never leave the marker behind: keeps the tree clean and stops the next test
        # build from accidentally shipping production config.
        if BUILD_ENV_PATH.exists():
            BUILD_ENV_PATH.unlink()


if __name__ == "__main__":
    sys.exit(main())
