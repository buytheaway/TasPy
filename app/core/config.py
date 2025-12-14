from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field


class AppConfig(BaseSettings):
    app_name: str = "TaskTree"
    db_path: Path = Field(default=Path("tasks.db"))
    theme_qss: Path = Field(default=Path("app/themes/qss/future_neon.qss"))
    lang: str = "ru"

    class Config:
        env_prefix = "TT_"
        extra = "ignore"


# Backwards-compatible instance used elsewhere in the codebase
settings = AppConfig()
