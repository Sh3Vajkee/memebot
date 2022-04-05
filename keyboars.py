from aiogram import types


host_btn = [types.InlineKeyboardButton('Старт', callback_data='host_start'), types.InlineKeyboardButton('Отмена', callback_data='host_cancel')]
host_kb = types.InlineKeyboardMarkup(row_width=2)
host_kb.add(*host_btn)
