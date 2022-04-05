from aiogram import Dispatcher, types
from db.models import PhraseImages, MemeImages
from filters.player_filter import IsAdmin, IsPrivate
import asyncio
from sqlalchemy import select


async def admin_cmd(message: types.Message):
    await message.answer('Команды админа:\n-  -  -\n/clear\n-  -  -\n/phrase\n-  -  -\n/memes')


async def upload_phrases(message: types.Message):
    db_session = message.bot.get("db")

    file = open('фразы.txt', encoding='UTF-8')
    phrase_index = 0
    for line in file:
        text = line.strip().capitalize()
        print(text)
        phrase_index += 1

        path_img = f'pics/phrs/{phrase_index}.jpg'
        input = types.InputFile(path_img)
        img = await message.bot.send_photo(message.from_user.id, input)
        await asyncio.sleep(0.1)

        async with db_session() as session:
            await session.merge(
                PhraseImages(
                    phrase_id=phrase_index,
                    link=img.photo[-1].file_id,
                    text=text
                )
            )
            await session.commit()
        await asyncio.sleep(0.1)
    file.close()

    sql = select(PhraseImages)
    async with db_session() as session:
        get_phrases = await session.execute(sql)
        phrases = get_phrases.scalars().all()

    for phrase in phrases:
        await message.bot.send_photo(message.from_user.id, phrase.link, caption=phrase.text)
        await asyncio.sleep(0.5)


async def upload_memes(message: types.Message):
    db_session = message.bot.get("db")

    for i in range(1, 101):
        path_img = f'pics/{i}.jpg'
        print(path_img)
        input = types.InputFile(path_img)
        img = await message.bot.send_photo(message.from_user.id, input)
        await asyncio.sleep(0.1)

        async with db_session() as session:
            await session.merge(
                MemeImages(
                    img_id=i,
                    link=img.photo[-1].file_id
                )
            )
            await session.commit()

async def check_errors(message: types.Message):
    db_session = message.bot.get("db")
    phrases = select(PhraseImages)

    async with db_session() as session:
        phrs = await session.execute(phrases)
        phr = phrs.scalars()

    for item in phr:
        await message.bot.send_photo(
            message.from_user.id,
            item.link,
            f'{item.phrase_id}\n{item.text}\n{item.link}'
        )
        await asyncio.sleep(0.2)

async def change_text(message: types.Message):
    db_session = message.bot.get("db")
    
    async with db_session() as session:
        phrase10: PhraseImages = await session.get(PhraseImages, 10)
        phrase11: PhraseImages = await session.get(PhraseImages, 11)
        phrase12: PhraseImages = await session.get(PhraseImages, 12)
        phrase13: PhraseImages = await session.get(PhraseImages, 13)
        phrase14: PhraseImages = await session.get(PhraseImages, 14)
        phrase15: PhraseImages = await session.get(PhraseImages, 15)
        phrase16: PhraseImages = await session.get(PhraseImages, 16)

        phrase10_text = phrase11.text
        phrase11_text = phrase12.text
        phrase12_text = phrase13.text
        phrase13_text = phrase14.text
        phrase14_text = phrase15.text
        phrase15_text = 'Когда увидел драку бомжей на улице'
        phrase16_text = 'Когда на первом свидании делаешь вид, что успешный бизнесмен'

        phrase10.text = phrase10_text
        phrase11.text = phrase11_text
        phrase12.text = phrase12_text
        phrase13.text = phrase13_text
        phrase14.text = phrase14_text
        phrase15.text = phrase15_text
        phrase16.text = phrase16_text

        await session.commit()
        
def register_upload(dp: Dispatcher):
    dp.register_message_handler(change_text, IsAdmin(), commands='txt')
    dp.register_message_handler(check_errors, IsAdmin(), commands='ch')
    dp.register_message_handler(
        admin_cmd, IsPrivate(), IsAdmin(), commands='admin')
    dp.register_message_handler(
        upload_phrases, IsPrivate(), IsAdmin(), commands='phrase')
    dp.register_message_handler(
        upload_memes, IsPrivate(), IsAdmin(), commands='memes')
