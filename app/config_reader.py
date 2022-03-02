import configparser
import os
from dataclasses import dataclass


@dataclass
class TgBot:
    token: str


@dataclass
class Config:
    tg_bot: TgBot


def load_config(path: str):
    config = configparser.ConfigParser()
    config.read(path)

    tg_bot_token = config.get("tg_bot", "token")

    return Config(tg_bot=TgBot(token=tg_bot_token))
