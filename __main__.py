import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.types.bot_command_scope import BotCommandScopeDefault
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from config_loader import Config, load_config
from db.base import Base
from handlers.commands import register_commands
from handlers.gamestart import gamestart_register_handler
from handlers.join import join_register_handler
from handlers.gameplay import gameplay_register_handler
from handlers.like import like_register_handlers
from filters.player_filter import IsHost, IsReady, IsLiked, IsAdmin, IsJoined, IsPrivate
from handlers.upload_img import register_upload
from updatesworker import get_handled_updates_list


async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(
            command="memegame", description="Создать лобби"),
        BotCommand(
            command="lobbies", description="Найти лобби"),
    ]
    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        filename="test.log"
    )

    config: Config = load_config()

    engine = create_async_engine(
        f"postgresql+asyncpg://{config.db.user}:{config.db.password}@{config.db.host}/{config.db.db_name}",
        future=True
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_sessionmaker = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )

    bot = Bot(config.bot.token, parse_mode="HTML")
    bot["db"] = async_sessionmaker
    dp = Dispatcher(bot)

    dp.filters_factory.bind(IsHost)
    dp.filters_factory.bind(IsReady)
    dp.filters_factory.bind(IsLiked)
    dp.filters_factory.bind(IsAdmin)
    dp.filters_factory.bind(IsJoined)
    dp.filters_factory.bind(IsPrivate)

    register_commands(dp)
    gamestart_register_handler(dp)
    join_register_handler(dp)
    gameplay_register_handler(dp)
    like_register_handlers(dp)
    register_upload(dp)

    await set_bot_commands(bot)

    try:
        await dp.start_polling(allowed_updates=get_handled_updates_list(dp))
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


try:
    asyncio.run(main())
except (KeyboardInterrupt, SystemExit):
    logging.error("Bot stopped!")
