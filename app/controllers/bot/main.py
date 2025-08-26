from aiogram.types import BotCommand
from aiogram import Router

COMMANDS = [BotCommand(command="start", description="Запускает бота")]
router = Router(name="main")
