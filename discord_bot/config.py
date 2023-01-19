from dataclasses import dataclass

from environs import Env


@dataclass
class DiscordBot:
    token: str
    tenor: str


@dataclass
class DbConfig:
    hostname: str
    username: str
    password: str
    database: str


@dataclass
class Guild:
    guild_id: int


@dataclass
class Role:
    admin: int
    closemod: int
    streamer: int
    twitch_announcement: int


@dataclass
class Channel:
    close_channel: int


@dataclass
class Config:
    bot: DiscordBot
    guild: Guild
    db: DbConfig
    roles: Role
    channels: Channel


def load_config(path: str = None):
    env = Env()
    env.read_env(path)

    return Config(
        DiscordBot(
            token=env.str("BOT_TOKEN"),
            tenor=env.str("TENOR_TOKEN")
        ),
        Guild(
            guild_id=env.int("GUILD_ID")
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
            twitch_announcement=env.int("STREAM_ANNOUNCEMENT_ROLE"),  # ID роли для получения уведомлений о стримах
            streamer=env.int("STREAMER_ROLE"),  # ID роли стримера
        ),
        Channel(
            close_channel=env.int("CLOSE_CHANNEL"),  # канал, в котором будут проводиться клозы 5х5
        )
    )
