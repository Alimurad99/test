from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message
import logging
import sqlite3

API_TOKEN = '5483072162:AAGYdhMZPEPjlTO90O-nXmnpod2U9MkLLXk'
ADMIN = 5530513447

kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
kb.add(types.InlineKeyboardButton(text="Рассылать всем"))
kb.add(types.InlineKeyboardButton(text="Добавить в Банановыетрова"))
kb.add(types.InlineKeyboardButton(text="Убрать из Банановые острова"))
kb.add(types.InlineKeyboardButton(text="Стата"))

logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)

conn = sqlite3.connect('db.db')
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS users(user_id INTEGER, block INTEGER);""")
conn.commit()

class dialog(StatesGroup):
	spam = State()
  blacklist = State()
  whitelist = State()
  
  @dp.message_handler(commands=['start'])
async def start(message: Message):
  cur = conn.cursor()
  cur.execute(f"SELECT block FROM users WHERE user_id = {message.chat.id}")
  result = cur.fetchone()
  if message.from_user.id == ADMIN:
    await message.answer('Добро пожаловать в PhonkBot Выберите действие на клавиатуре', reply_markup=kb)
  else:
      if result is None:
        cur = conn.cursor()
        cur.execute(f'''SELECT * FROM users WHERE (user_id="{message.from_user.id}")''')
        entry = cur.fetchone()
        if entry is None:
          cur.execute(f'''INSERT INTO users VALUES ('{message.from_user.id}', '0')''')
          conn.commit()
          await message.answer('Приве!!т')
      else:
        await message.answer('Ты был отправлен банановые острова!')
        
        @dp.message_handler(content_types=['text'], text='Рассылка')
async def spam(message: Message):
  await dialog.spam.set()
  await message.answer('Напиши текст рассылки')
  
  @dp.message_handler(state=dialog.spam)
async def start_spam(message: Message, state: FSMContext):
  if message.text == 'Назад':
    await message.answer('Главное меню', reply_markup=kb)
    await state.finish()
  else:
    cur = conn.cursor()
    cur.execute(f'''SELECT user_id FROM users''')
    spam_base = cur.fetchall()
      for z in range(len(spam_base)):
        await bot.send_message(spam_base[z][0], message.text)
        await message.answer('Рассылка завершена', reply_markup=kb)
        await state.finish()
        
        @dp.message_handler(content_types=['text'], text='Добавить в ЧС')
async def hanadler(message: types.Message, state: FSMContext):
  if message.chat.id == ADMIN:
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.InlineKeyboardButton(text="Назад"))
    await message.answer('Введите id пользователя, которого нужно отправить банановые острова!.\nДля отмены нажмите кнопку ниже', reply_markup=keyboard)
    await dialog.blacklist.set()
    
    @dp.message_handler(state=dialog.blacklist)
async def proce(message: types.Message, state: FSMContext):
  if message.text == 'Назад':
    await message.answer('Отмена! Возвращаю назад.', reply_markup=kb)
    await state.finish()
  else:
    if message.text.isdigit():
      cur = conn.cursor()
      cur.execute(f"SELECT block FROM users WHERE user_id = {message.text}")
      result = cur.fetchall()
      if len(result) == 0:
        await message.answer('Такой пользователь не найден в базе данных.', reply_markup=kb)
        await state.finish()
      else:
        a = result[0]
        id = a[0]
        if id == 0:
          cur.execute(f"UPDATE users SET block = 1 WHERE user_id = {message.text}")
          conn.commit()
          await message.answer('Пользователь успешно отправлен банановые острова!', reply_markup=kb)
          await state.finish()
          await bot.send_message(message.text, 'Ты был забанен Администрацией')
        else:
          await message.answer('Данный пользователь уже пв банановых островах', reply_markup=kb)
          await state.finish()
    else:
      await message.answer('Ты вводишь буквы...\n\nВведи ID')
      
      @dp.message_handler(content_types=['text'], text='Убрать из ЧС')
async def hfandler(message: types.Message, state: FSMContext):
  cur = conn.cursor()
  cur.execute(f"SELECT block FROM users WHERE user_id = {message.chat.id}")
  result = cur.fetchone()
  if result is None:
    if message.chat.id == ADMIN:
      keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
      keyboard.add(types.InlineKeyboardButton(text="Назад"))
      await message.answer('Введите id пользователя, которого нужно разблокировать.\nДля отмены нажмите кнопку ниже', reply_markup=keyboard)
      await dialog.whitelist.set()
      
      @dp.message_handler(state=dialog.whitelist)
async def proc(message: types.Message, state: FSMContext):
  if message.text == 'Отмена':
    await message.answer('Отмена! Возвращаю назад.', reply_markup=kb)
    await state.finish()
  else:
    if message.text.isdigit():
      cur = conn.cursor()
      cur.execute(f"SELECT block FROM users WHERE user_id = {message.text}")
      result = cur.fetchall()
      conn.commit()
      if len(result) == 0:
        await message.answer('Такой пользователь не найден в базе данных.', reply_markup=kb)
        await state.finish()
      else:
        a = result[0]
        id = a[0]
        if id == 1:
          cur = conn.cursor()
          cur.execute(f"UPDATE users SET block = 0 WHERE user_id = {message.text}")
          conn.commit()
          await message.answer('Пользователь успешно вернулся из банановые острова!щ.', reply_markup=kb)
          await state.finish()
          await bot.send_message(message.text, 'Вы были разблокированы администрацией.')
        else:
          await message.answer('Данный пользователь не был в банановых островах.', reply_markup=kb)
          await state.finish()
    else:
      await message.answer('Ты вводишь буквы...\n\nВведи ID')
      
      @dp.message_handler(content_types=['text'], text='Статистика')
async def hfandler(message: types.Message, state: FSMContext):
	cur = conn.cursor()
	cur.execute('''select * from users''')
  results = cur.fetchall()
  await message.answer(f'Людей которые когда либо заходили в бота: {len(results)}')
  
  if __name__ == '__main__':
  executor.start_polling(dp, skip_updates=True)
