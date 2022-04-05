from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from db.models import CurrentPlayers
from filters.player_filter import IsLiked


async def like_msg(call: types.CallbackQuery):
    db_session = call.bot.get("db")

    data_like = call.data.split('_')
    like_id = int(data_like[-1])

    async with db_session() as session:

        msg_owner: CurrentPlayers = await session.get(CurrentPlayers, like_id)
        msg_owner.likes += 1

        who_liked: CurrentPlayers = await session.get(CurrentPlayers, call.from_user.id)
        who_liked.liked = 'Yes'

        await session.commit()

    await call.answer('Выбор сделан')


def like_register_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(
        like_msg, IsLiked(), Text(startswith='like_'))
