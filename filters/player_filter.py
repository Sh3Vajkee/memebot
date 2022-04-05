from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
from db.models import Lobby, CurrentPlayers
from sqlalchemy import select


class IsPrivate(BoundFilter):
    key = 'is_private'

    async def check(self, message: types.Message):
        return message.chat.type == types.ChatType.PRIVATE


class IsHost(BoundFilter):
    key = 'is_host'

    async def check(self, message: types.Message):
        db_session = message.bot.get("db")

        is_free = True
        sql = select(Lobby).filter(Lobby.owner_id == message.from_user.id)
        async with db_session() as session:
            player: CurrentPlayers = await session.get(CurrentPlayers, message.from_user.id)

            check = await session.execute(sql)
            result = check.scalars().all()

        if player and (len(result) > 0):
            is_free = False
        elif player or (len(result) > 0):
            is_free = False
        else:
            is_free = True

        return is_free


class IsReady(BoundFilter):
    key = 'is_ready'

    async def check(self, call: types.CallbackQuery):
        db_session = call.bot.get("db")

        async with db_session() as session:
            check: CurrentPlayers = await session.get(CurrentPlayers, call.from_user.id)

        return check.ready == 'No'


class IsLiked(BoundFilter):
    key = 'is_liked'

    async def check(self, call: types.CallbackQuery):
        db_session = call.bot.get("db")

        async with db_session() as session:
            check: CurrentPlayers = await session.get(CurrentPlayers, call.from_user.id)

        return check.liked == 'No'


class IsJoined(BoundFilter):
    key = 'is_joined'

    async def check(self, message: types.Message):
        db_session = message.bot.get("db")

        is_free: bool = True
        async with db_session() as session:
            check: CurrentPlayers = await session.get(CurrentPlayers, message.from_user.id)

        if check:
            is_free = False
        else:
            is_free = True

        return is_free


class IsAdmin(BoundFilter):
    key = 'is_admin'

    async def check(self, message: types.Message):
        admins = [746461090, 5131674802]
        return message.from_user.id in admins
