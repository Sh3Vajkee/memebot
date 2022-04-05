from aiogram import Dispatcher, types
from random import randint, shuffle
from db.models import Lobby, CurrentPlayers, PhraseImages, MemeImages, MsgChoice
from keyboars import host_kb
from sqlalchemy import select, delete
import asyncio
from filters.player_filter import IsHost, IsPrivate


async def cmd_memegame(message: types.Message):
    db_session = message.bot.get('db')

    try:
        user_name = f'@{message.from_user.username}'
    except:
        user_name = f'User_{message.from_user.id}'

    msg = await message.answer(f'Создано лобби.Игроки в лобби:\n{user_name}', reply_markup=host_kb)

    async with db_session() as session:
        await session.merge(
            Lobby(
                msg_id=msg.message_id,
                msg_text=msg.text,
                owner_id=message.from_user.id,
                owner_username=user_name
            )
        )
        await session.merge(
            CurrentPlayers(
                player_id=message.from_user.id,
                user_name=user_name,
                lobby_id=msg.message_id
            )
        )
        await session.commit()

    await message.delete()


async def cmd_startgame(call: types.CallbackQuery):
    db_session = call.bot.get('db')

    lobby_query = select(CurrentPlayers).filter(
        CurrentPlayers.lobby_id == call.message.message_id)

    phrase_id = randint(1, 85)
    memes_query = select(MemeImages)
    async with db_session() as session:

        get_meme_imgs = await session.execute(memes_query)
        player_imgs = get_meme_imgs.scalars().all()

        phrase: PhraseImages = await session.get(PhraseImages, phrase_id)

        lobby: Lobby = await session.get(Lobby, call.message.message_id)
        lobby.status = 'Closed'
        lobby.round += 1
        lobby.phrase_link = phrase.link
        lobby.phrase_text = phrase.text

        get_lobby_players = await session.execute(lobby_query)
        lobby_players = get_lobby_players.scalars().all()

        await session.commit()

    await call.answer('Игра запущена')
    await call.message.delete()

    for player in lobby_players:
        await call.bot.send_message(player.player_id, 'Выберите наиболее подходящее изображение к фразе...')
        await asyncio.sleep(0.3)
        await call.bot.send_photo(player.player_id, phrase.link)

    await asyncio.sleep(2)

    for player in lobby_players:

        shuffle(player_imgs)

        for img in player_imgs[:5]:

            pic_kb = types.InlineKeyboardMarkup()
            pic_kb.add(types.InlineKeyboardButton(
                'Выбрать', callback_data=f'pic_{str(img.img_id)}'))

            msg = await call.bot.send_photo(
                player.player_id,
                img.link,
                caption=phrase.text,
                reply_markup=pic_kb
            )

            async with db_session() as session:
                await session.merge(
                    MsgChoice(
                        lobby_id=call.message.message_id,
                        msg_id=msg.message_id,
                        chat_id=player.player_id
                    )
                )
                await session.commit()


async def cmd_cancelgame(call: types.CallbackQuery):
    db_session = call.bot.get("db")

    try:

        sql = delete(Lobby).filter(Lobby.msg_id == call.message.message_id)
        players_sql = delete(CurrentPlayers).filter(
            CurrentPlayers.lobby_id == call.message.message_id)
        async with db_session() as session:
            await session.execute(sql)
            await session.execute(players_sql)
            await session.commit()

        await call.answer('Лобби удалено')
        await call.message.delete()

    except:
        await call.answer('Лобби не найдено')


def gamestart_register_handler(dp: Dispatcher):
    dp.register_message_handler(
        cmd_memegame, IsPrivate(), IsHost(), commands='memegame')
    dp.register_callback_query_handler(cmd_startgame, text='host_start')
    dp.register_callback_query_handler(cmd_cancelgame, text='host_cancel')
