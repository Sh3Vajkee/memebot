from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from sqlalchemy import delete
from db.models import Lobby, CurrentPlayers
from keyboars import host_kb


async def cmd_join(call: types.CallbackQuery):
    db_session = call.bot.get("db")

    async with db_session() as session:
        check_player = await session.get(CurrentPlayers, call.from_user.id)

    if check_player:

        await call.answer('Вы не можете находиться одновременно в нескольких лобби', show_alert=True)
        await call.message.delete()

    else:

        join_data = call.data.split('_')
        lobby_id = int(join_data[-1])

        try:
            user_name = f'@{call.from_user.username}'
        except:
            user_name = f'User_{call.from_user.id}'

        async with db_session() as session:
            lobby: Lobby = await session.get(Lobby, lobby_id)
            lobby.total_players += 1
            lobby.msg_text += f'\n{user_name}'

            await session.merge(
                CurrentPlayers(
                    player_id=call.from_user.id,
                    user_name=user_name,
                    lobby_id=lobby_id
                )
            )
            await session.commit()

        await call.bot.edit_message_text(lobby.msg_text, lobby.owner_id, lobby.msg_id, reply_markup=host_kb)

        await call.answer(f'Вы присоединились к лобби №{lobby.msg_id}')

        leave_kb = types.InlineKeyboardMarkup()
        leave_kb.add(types.InlineKeyboardButton(
            'Покинуть', callback_data=f'leave_{lobby.msg_id}'))

        await call.message.answer('Ожидание старта игры...', reply_markup=leave_kb)

        await call.message.delete()


async def leave_lobby(call: types.CallbackQuery):
    db_session = call.bot.get("db")

    get_call_data = call.data.split('_')
    lobby_id = int(get_call_data[-1])

    try:
        user_name = f'@{call.from_user.username}'
    except:
        user_name = f'User_{call.from_user.id}'

    try:
        delete_current_player = delete(CurrentPlayers).filter(
            CurrentPlayers.player_id == call.from_user.id)
        async with db_session() as session:
            await session.execute(delete_current_player)

            lobby: Lobby = await session.get(Lobby, lobby_id)
            lobby.total_players -= 1
            new_text: str = lobby.msg_text
            lobby.msg_text = new_text.replace(f'\n{user_name}', '')

            await session.commit()

        await call.bot.edit_message_text(lobby.msg_text, lobby.owner_id, lobby.msg_id, reply_markup=host_kb)
        await call.answer('Вы покинули лобби')
        await call.message.delete()

    except:
        await call.answer('Ошибка')
        await call.message.delete()


def join_register_handler(dp: Dispatcher):
    dp.register_callback_query_handler(cmd_join, Text(startswith='join_'))
    dp.register_callback_query_handler(leave_lobby, Text(startswith='leave_'))
