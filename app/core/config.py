from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path


class Settings(BaseSettings):
    app_name: str = "TaskTree"
    db_path: Path = Field(default=Path("tasks.db"))
    theme_qss: Path = Field(default=Path("app/themes/qss/dark_green.qss"))
    lang: str = "ru"

    class Config:
        env_prefix = "TT_"
        extra = "ignore"


settings = Settings()