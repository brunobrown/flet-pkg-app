from dynaconf import Dynaconf, Validator

# Required configuration variables that must be defined before the app starts.
# See: https://www.dynaconf.com/validation/
required_variables = [
    "GITHUB_TOKEN",
]

settings = Dynaconf(
    # Enable environment-based configuration ([default], [development], [production], etc.)
    environments=True,
    # Do not load from .env files — use settings.toml and .secrets.toml instead
    load_dotenv=False,
    # Configuration files loaded in order (later files override earlier ones)
    settings_files=["settings.toml", ".secrets.toml"],
    # Prefix for environment variable overrides (e.g. SET_VAR_DYNACONF_GITHUB_TOKEN=xxx)
    envvar_prefix="SET_VAR_DYNACONF",
    validators=[
        Validator(
            *required_variables,
            must_exist=True,
            messages={
                "must_exist_true": (
                    f"Missing required configuration: {required_variables}. "
                    "Define them in settings.toml (public config) or .secrets.toml "
                    "(sensitive values like API tokens). "
                    "See https://dynaconf.com for configuration details."
                )
            },
        )
    ],
)
