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

settings = Dynaconf(
    # Enable environment-based configuration ([default], [development], [production], etc.)
    environments=True,
    # Do not load from .env files — use settings.toml and .secrets.toml instead
    load_dotenv=False,
    # Configuration files loaded in order (later files override earlier ones)
    # .secrets.toml is optional — not present on mobile builds
    settings_files=["settings.toml", ".secrets.toml"],
    # Prefix for environment variable overrides (e.g. SET_VAR_DYNACONF_GITHUB_TOKEN=xxx)
    envvar_prefix="SET_VAR_DYNACONF",
    validators=[_validators],
)
