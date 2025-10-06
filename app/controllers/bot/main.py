from aiogram.types import BotCommand, Message
from aiogram.filters import Command
from aiogram import Router

COMMANDS = [BotCommand(command="start", description="Запускает бота")]
router = Router(name="main")


@router.message(Command("start"))
async def start_command_handler(message: Message):
    await message.answer("Hello! I'm your bot.")
