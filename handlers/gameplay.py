import asyncio
from contextlib import suppress
from random import shuffle, randint
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.utils.exceptions import MessageNotModified
from filters.player_filter import IsReady
from sqlalchemy import select, delete
from db.models import CurrentPlayers, Lobby, MemeRound, MemeImages, MsgLike, PhraseImages, MsgChoice


async def gameplay(call: types.CallbackQuery):
    db_session = call.bot.get('db')

    pic_data_list = call.data.split('_')
    pic_data = int(pic_data_list[-1])

    await call.answer('Выбор сделан')
    await call.message.answer('Ожидание других игроков...')

    query_msgs = select(MsgChoice).filter(
        MsgChoice.chat_id == call.from_user.id)
    delete_msgs = delete(MsgChoice).filter(
        MsgChoice.chat_id == call.from_user.id)
    async with db_session() as session:

        player_msgs = await session.execute(query_msgs)
        msgs = player_msgs.scalars()

        for msg in msgs:
            with suppress(MessageNotModified):
                await call.bot.edit_message_reply_markup(msg.chat_id, msg.msg_id)

        get_img: MemeImages = await session.get(MemeImages, pic_data)

        check_user: CurrentPlayers = await session.get(CurrentPlayers, call.from_user.id)
        check_user.ready = 'Yes'

        await session.merge(
            MemeRound(
                lobby_id=check_user.lobby_id,
                player_id=call.from_user.id,
                img_link=get_img.link
            )
        )

        lobby: Lobby = await session.get(Lobby, check_user.lobby_id)
        lobby.ready_players += 1

        await session.execute(delete_msgs)

        await session.commit()

    if lobby.total_players == lobby.ready_players:

        get_lobby_players_query = select(CurrentPlayers).filter(
            CurrentPlayers.lobby_id == check_user.lobby_id)
        get_meme_round_query = select(MemeRound).filter(
            MemeRound.lobby_id == check_user.lobby_id)

        async with db_session() as session:
            get_lobby_players = await session.execute(get_lobby_players_query)
            lobby_players = get_lobby_players.scalars().all()

            get_meme_round = await session.execute(get_meme_round_query)
            meme_round = get_meme_round.scalars().all()

        await asyncio.sleep(3)

        for player in lobby_players:

            await call.bot.send_message(player.player_id, f' \n\n\nРаунд {lobby.round}\n\n\n ')

            for meme_pic in meme_round:

                if meme_pic.player_id == player.player_id:
                    msg = await call.bot.send_photo(
                        player.player_id,
                        meme_pic.img_link,
                        caption=f'{lobby.phrase_text}\n(Ваш вариант)'
                    )
                else:
                    like_kb = types.InlineKeyboardMarkup()
                    like_kb.add(types.InlineKeyboardButton(
                        '👍 Like', callback_data=f'like_{str(meme_pic.player_id)}'))

                    msg = await call.bot.send_photo(
                        player.player_id,
                        meme_pic.img_link,
                        caption=lobby.phrase_text,
                        reply_markup=like_kb
                    )

                async with db_session() as session:
                    await session.merge(
                        MsgLike(
                            lobby_id=check_user.lobby_id,
                            msg_id=msg.message_id,
                            chat_id=msg.chat.id
                        )
                    )
                    await session.commit()

            await call.bot.send_message(player.player_id, 'Проголосуйте за понравившийся результат')

        await asyncio.sleep((4*(lobby.total_players)))

        lobby_msgs = select(MsgLike).filter(
            MsgLike.lobby_id == check_user.lobby_id)
        async with db_session() as session:
            get_msgs = await session.execute(lobby_msgs)
            msgs = get_msgs.scalars().all()

        for msg in msgs:
            with suppress(MessageNotModified):
                await call.bot.edit_message_reply_markup(msg.chat_id, msg.msg_id)

        delete_msgs = delete(MsgLike).filter(
            MsgLike.lobby_id == check_user.lobby_id)
        async with db_session() as session:
            await session.execute(delete_msgs)
            await session.commit()

        if lobby.round == 5:

            lobby_results_query = select(CurrentPlayers).filter(
                CurrentPlayers.lobby_id == check_user.lobby_id).order_by(CurrentPlayers.likes.desc())
            async with db_session() as session:
                lobby_results = await session.execute(lobby_results_query)
                results = lobby_results.scalars().all()

            result_text = '🏆Результаты игры'
            place = 0
            for item in results:

                place += 1
                user_name = item.user_name
                likes = item.likes

                if place == 1:
                    medal = '🥇'
                elif place == 2:
                    medal = '🥈'
                elif place == 3:
                    medal = '🥉'
                else:
                    medal = '💩'

                result_text += f'\n{medal}{place}.<b>{user_name}</b> - <b>{likes}pts</b>'

            for player in lobby_players:

                await call.bot.send_message(player.player_id, result_text, parse_mode='HTML')

            clear_lobby = delete(Lobby).filter(
                Lobby.msg_id == check_user.lobby_id)
            clear_players = delete(CurrentPlayers).filter(
                CurrentPlayers.lobby_id == check_user.lobby_id)
            clear_meme_round = delete(MemeRound).filter(
                MemeRound.lobby_id == check_user.lobby_id)
            delete_msgs = delete(MsgLike).filter(
                MsgLike.lobby_id == check_user.lobby_id)

            async with db_session() as session:
                await session.execute(clear_lobby)
                await session.execute(clear_players)
                await session.execute(clear_meme_round)
                await session.execute(delete_msgs)

                await session.commit()

        else:

            memes_query = select(MemeImages)
            change_ready_query = select(CurrentPlayers).filter(
                CurrentPlayers.lobby_id == check_user.lobby_id)
            phrase_id = randint(1, 85)
            async with db_session() as session:
                phrase: PhraseImages = await session.get(PhraseImages, phrase_id)

                get_ready_players = await session.execute(change_ready_query)
                ready_players = get_ready_players.scalars().all()

                for player in ready_players:
                    player.ready = 'No'
                    player.liked = 'No'

                get_meme_imgs = await session.execute(memes_query)
                player_imgs = get_meme_imgs.scalars().all()

                lobby: Lobby = await session.get(Lobby, check_user.lobby_id)
                lobby.ready_players = 0
                lobby.round += 1

                next_phrase_link = phrase.link
                next_phrase_text = phrase.text

                lobby.phrase_link = next_phrase_link
                lobby.phrase_text = next_phrase_text

                await session.commit()

            for player in lobby_players:

                await call.bot.send_message(player.player_id, 'Выберите наиболее подходящее изображение к фразе...')
                await asyncio.sleep(0.3)
                await call.bot.send_photo(player.player_id, next_phrase_link)

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
                        caption=next_phrase_text,
                        reply_markup=pic_kb
                    )

                    async with db_session() as session:
                        await session.merge(
                            MsgChoice(
                                lobby_id=lobby.msg_id,
                                msg_id=msg.message_id,
                                chat_id=player.player_id
                            )
                        )
                        await session.commit()


def gameplay_register_handler(dp: Dispatcher):
    dp.register_callback_query_handler(
        gameplay, IsReady(), Text(startswith='pic_'))
