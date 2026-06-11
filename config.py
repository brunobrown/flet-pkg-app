from dynaconf import Dynaconf, Validator

# Required configuration variables that must be defined before the app starts.
# See: https://www.dynaconf.com/validation/
_required_variables = [
    "GITHUB_TOKEN",
]

_validators = Validator(
    *_required_variables,
    must_exist=True,
    messages={
        "must_exist_true": (
            f"Missing required configuration: {_required_variables}.\n"
            "\n"
            "Create a .secrets.toml file in the project root:\n"
            "\n"
            "  [default]\n"
            '  MOBILE_GITHUB_TOKEN = "ghp_your_personal_access_token_here"\n'
            "  [development]\n"
            '  GITHUB_TOKEN = "ghp_your_personal_access_token_here"\n'
            "  [homologation]\n"
            '  GITHUB_TOKEN = "ghp_your_personal_access_token_here"\n'
            "  [production]\n"
            '  GITHUB_TOKEN = "ghp_your_personal_access_token_here"\n'
            "\n"
            "Docs: https://dynaconf.com"
        )
    },
)

# Build-time environment marker.
#
# A packaged mobile app launches with NO OS environment variables, so Dynaconf's normal
# env switcher (ENV_FOR_DYNACONF) can't pick the environment at runtime on device — it
# always falls back to the `default` env (Google TEST AdMob IDs). To ship a production
# build that resolves the `production` env (real AdMob IDs), scripts/build_aab.py writes
# `_build_env.py` into the bundle (via `--env production`). We read it here.
#
# When the marker is ABSENT — every dev run, the web/server deploy, and every non-release
# AAB — `env` stays unset and Dynaconf keeps its normal behavior: ENV_FOR_DYNACONF on
# desktop/server, or the `default`/`development` env (TEST ad IDs) on a test-track build.
try:
    # Generated only by `build_aab.py --env <name>`; absent in the repo and in
    # dev/web runs, so the static import is expected to be unresolved here.
    from _build_env import APP_ENV  # ty: ignore[unresolved-import]
except ImportError:
    APP_ENV = None

_env_kwarg = {"env": APP_ENV} if APP_ENV else {}

settings = Dynaconf(
    # Enable environment-based configuration ([default], [development], [production], etc.)
    environments=True,
    # Force the env baked into the release bundle; otherwise let Dynaconf decide (env var
    # on desktop/server, or the default/development env on a test build).
    **_env_kwarg,
    # Do not load from .env files — use settings.toml and .secrets.toml instead
    load_dotenv=False,
    # Configuration files loaded in order (later files override earlier ones)
    # .secrets.toml is optional — not present on mobile builds
    settings_files=["settings.toml", ".secrets.toml"],
    # Prefix for environment variable overrides (e.g. SET_VAR_DYNACONF_GITHUB_TOKEN=xxx)
    envvar_prefix="SET_VAR_DYNACONF",
    validators=[_validators],
)
