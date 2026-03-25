# import os
from dynaconf import Dynaconf, Validator

# Lista de variáveis de ambiente obrigatórias
required_variables = [
    "GITHUB_TOKEN",
]

settings = Dynaconf(
    # Ativa múltiplos ambientes
    environments=True,
    # Indica se deve ou não carregar variáveis de ambiente de um arquivo '.env'
    load_dotenv=False,
    # Lista de arquivos de configuração a serem carregados, na ordem em que são especificados
    settings_files=["settings.toml", ".secrets.toml"],
    # Prefixo usado para adicionar variáveis de ambiente
    envvar_prefix="SET_VAR_DYNACONF",
    # Nome da variável de ambiente que controla a troca entre os diferentes ambientes configurados
    # env_switcher="DYNACONF_ENV_MODE", # Use ENV_FOR_DYNACONF do proprio dynaconf
    validators=[
        Validator(
            *required_variables,
            must_exist=True,
            messages={
                "must_exist_true": (
                    f"As variáveis {required_variables} são obrigatórias."
                    " Defina em settings.toml ou .secrets.toml"
                )
            },
        )
    ],
)

# os.environ['DYNACONF_ENV_MODE'] = 'production'
# `envvar_prefix` = export envvars with `export DYNACONF_FOO=bar`.
# `settings_files` = Load these files in the order.
