from dataclasses import dataclass
from typing import List

from environs import Env


@dataclass
class DiscordBot:
    token: str
    admins: List[int]
    tenor: str


@dataclass
class DbConfig:
    hostname: str
    username: str
    password: str
    database: str


@dataclass
class Role:
    admin: int
    closemod: int


@dataclass
class Channel:
    close_channel: int


@dataclass
class Config:
    bot: DiscordBot
    db: DbConfig
    roles: Role
    channels: Channel


def load_config(path: str = None):
    env = Env()
    env.read_env(path)

    return Config(
        DiscordBot(
            token=env.str("BOT_TOKEN"),
            admins=list(map(int, env.list("ADMINS"))),
            tenor=env.str("TENOR_TOKEN")
        ),
        DbConfig(
            hostname=env.str("DB_HOST"),
            username=env.str("DB_USER"),
            password=env.str("DB_PASS"),
            database=env.str("DB_NAME"),
        ),
        Role(
            admin=env.int("ADMINISTRATOR_ROLE"),  # ID роли администратора
            closemod=env.int("CLOSE_MODERATOR_ROLE"),  # ID роли для проведения ивентов
        ),
        Channel(
            close_channel=env.int("CLOSE_CHANNEL"),  # канал, в котором будут проводиться клозы 5х5
        )
    )
