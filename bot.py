import telebot
import json
import requests
from telebot import types

bot = telebot.TeleBot('')

# Weather bot
# 1 - show weather in custom city - ✔
# 2 - show weather by geoposition - ✔
# 3 - save geoposition
# 4 - show weather for day or for next day️


# Welcome message
@bot.message_handler(commands=['start'])
def welcome_message(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    button_help = types.InlineKeyboardButton(text='Help', callback_data='help')
    button_weather = types.InlineKeyboardButton(text='Find Weather', callback_data='weather')
    markup.add(button_weather, button_help)
    bot.send_message(message.chat.id, f'Welcome to my weather bot, {message.from_user.first_name}!\n'
                                      f'This bot allows you to find out the weather'
                                      f' by typing your city.', reply_markup=markup)


# Callback to Help Button
@bot.callback_query_handler(func=lambda callback: callback.data == 'help')
def callback_help(callback):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    back_button = types.KeyboardButton(text='Back')
    markup.add(back_button)

    bot.send_message(callback.message.chat.id,
                     f'To restart the bot - /start\n'
                     f'To find out the weather - click button "Weather"\n'
                     f'You must type in your city in English, e.g. Moscow.\n'
                     f'Or allow getting your location by pressing button.\n'
                     f'To read help - click "Help"', reply_markup=markup)
    bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.id)  # Delete prev /start


# After pressed button, save input data
@bot.callback_query_handler(func=lambda callback: callback.data == 'weather')
def callback_weather(callback):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    button_location = types.KeyboardButton(text='Location 📍', request_location=True)
    button_type = types.KeyboardButton(text='Type City ⌨')
    markup.add(button_location, button_type)
    bot.send_message(callback.message.chat.id, 'Write your city.\n'
                                               'Or allow getting your location.',
                     reply_markup=markup)


# Find weather by sending location
@bot.message_handler(content_types=['location'])
def weather_by_location(message):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    back_button = types.KeyboardButton(text='Back')
    markup.add(back_button)

    weather_request = requests.get(f'https://api.openweathermap.org/data/2.5/weather?lat={message.location.latitude}'
                                   f'&lon={message.location.longitude}&appid=e03ae7f775d48388005fd29386ae4fd7')
    main_info = json.loads(weather_request.text)['weather'][0]['main']
    more_info = json.loads(weather_request.text)['weather'][0]['description']
    temperature = json.loads(weather_request.text)['main']['temp']  # Kelvin
    temperature = float(temperature) - 273.15  # Celsius
    temperature_feels = json.loads(weather_request.text)['main']['feels_like']  # Kelvin
    temperature_feels = float(temperature_feels) - 273.15  # Celsius
    city = json.loads(weather_request.text)['name']
    bot.send_message(message.chat.id, f'Weather for today: \n\n'
                                      f'{main_info}, {more_info}.\n'
                                      f'Temperature: {int(temperature)} °C\n'
                                      f'Feels like: {int(temperature_feels)} °C\n'
                                      f'Location: {city}')


# Type in your city
@bot.message_handler(func=lambda message: message.text == 'Type City ⌨')
def weather_typed(message):
    sent_message = bot.send_message(message.chat.id, 'What is your city?')
    bot.register_next_step_handler(sent_message, weather_by_city)


# Find weather by typing city
def weather_by_city(message):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    back_button = types.KeyboardButton(text='Back')
    markup.add(back_button)

    weather_request = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={message.text}&appid'
                                   f'=e03ae7f775d48388005fd29386ae4fd7')
    main_info = json.loads(weather_request.text)['weather'][0]['main']
    more_info = json.loads(weather_request.text)['weather'][0]['description']
    temperature = json.loads(weather_request.text)['main']['temp']  # Kelvin
    temperature = float(temperature) - 273.15  # Celsius
    temperature_feels = json.loads(weather_request.text)['main']['feels_like']  # Kelvin
    temperature_feels = float(temperature_feels) - 273.15  # Celsius
    city = json.loads(weather_request.text)['name']
    bot.send_message(message.chat.id, f'Weather for today: \n\n'
                                      f'{main_info}, {more_info}.\n'
                                      f'Temperature: {int(temperature)} °C\n'
                                      f'Feels like: {int(temperature_feels)} °C\n'
                                      f'Location: {city}',
                     reply_markup=markup)


# Back to start
@bot.message_handler(func=lambda message: message.text == 'Back')
def back_handler(message):
    welcome_message(message)


bot.infinity_polling()
