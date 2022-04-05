from aiogram import types, Dispatcher
from sqlalchemy import select, delete
from db.models import Lobby, PhraseRound, CurrentPlayers, MemeRound, MsgLike, MsgChoice
from filters.player_filter import IsJoined, IsAdmin, IsPrivate


async def cmd_start(message: types.Message):
    await message.answer("Для того что бы создать лобби нажмите /memegame\nДля поиска лобби - /lobbies")


async def clear_tables(message: types.Message):
    db_session = message.bot.get("db")

    clear_lobby = delete(Lobby)
    clear_players = delete(CurrentPlayers)
    clear_round_phrases = delete(PhraseRound)
    clear_meme_round = delete(MemeRound)
    delete_msgs = delete(MsgLike)
    delete_pl_msgs = delete(MsgChoice)

    async with db_session() as session:
        await session.execute(clear_lobby)
        await session.execute(clear_players)
        await session.execute(clear_round_phrases)
        await session.execute(clear_meme_round)
        await session.execute(delete_msgs)
        await session.execute(delete_pl_msgs)

        await session.commit()


async def cmd_refresh(message: types.Message):
    db_session = message.bot.get("db")

    lobbies_query = select(Lobby).filter(Lobby.status == 'Open')
    async with db_session() as session:
        lobbyes_query = await session.execute(lobbies_query)
        lobbies = lobbyes_query.scalars().all()

    if len(lobbies) > 0:
        await message.delete()

        for lobby in lobbies:

            join_kb = types.InlineKeyboardMarkup()
            join_kb.add(types.InlineKeyboardButton(
                'Присоединиться', callback_data=f'join_{str(lobby.msg_id)}'))

            await message.answer(f'Лобби №{lobby.msg_id}\nХост: {lobby.owner_username}', reply_markup=join_kb)
    else:
        await message.answer('Нет активных лобби')
        await message.delete()


def register_commands(dp: Dispatcher):
    dp.register_message_handler(cmd_start, IsPrivate(), commands='start')
    dp.register_message_handler(
        cmd_refresh, IsPrivate(), IsJoined(), commands='lobbies')
    dp.register_message_handler(
        clear_tables, IsPrivate(), IsAdmin(), commands='clear')
