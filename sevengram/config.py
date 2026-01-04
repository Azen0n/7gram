from pydantic import PostgresDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BOT_TOKEN: str
    DB_HOST: str = 'postgres'
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_PORT_HOST: int
    DB_PORT_CONTAINER: int = 5432

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

    @property
    def database_url(self) -> str:
        return PostgresDsn.build(
            scheme='postgresql+asyncpg',
            username=self.DB_USER,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT_CONTAINER,
            path=self.DB_NAME,
        ).unicode_string()


settings = Settings()
