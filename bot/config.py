from dotenv import dotenv_values
from dataclasses import dataclass


env_vars = dotenv_values(".env")

@dataclass
class WebServerConfig:
    web_server_host: str
    web_server_port: int
    webhook_path: str
    webhook_secret: str
    base_webhook_url: str
    webhook_ssl_cert: str
    webhook_ssl_priv: str

def load_server_config():
    env_vars = dotenv_values(".env")
    return WebServerConfig(
        web_server_host=env_vars['WEB_SERVER_HOST'],
        web_server_port=int(env_vars['WEB_SERVER_PORT']),
        webhook_path=env_vars['WEBHOOK_PATH'],
        webhook_secret=env_vars['WEBHOOK_SECRET'],
        base_webhook_url=env_vars['BASE_WEBHOOK_URL'],
        webhook_ssl_cert=env_vars['WEBHOOK_SSL_CERT'],
        webhook_ssl_priv=env_vars['WEBHOOK_SSL_PRIV']
    )


def load_db_URL() -> str:
    database = env_vars['DATABASE']
    db_user = env_vars['DB_USER']
    db_password = env_vars['DB_PASSWORD']
    db_host = env_vars['DB_HOST']
    db_port = env_vars['DB_PORT']
    return (f"://{db_user}:{db_password}@"
            f"{db_host}:{db_port}/{database}")