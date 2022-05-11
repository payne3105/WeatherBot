import telebot
import json
import requests
from telebot import types

import private
from location import set_location, Location, emptiness_location, reset_location


# Weather bot
# 1 - show weather in custom city - ✔
# 2 - show weather by location - ✔
# 3 - save location - ✔
# 4 - show weather for day or for next day - ✔
# 5 - reset location - ✔

bot = telebot.TeleBot(private.token)


# Welcome message
@bot.message_handler(commands=['start'])
def proper_performance(message):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    button_location = types.KeyboardButton(text='Location 📍', request_location=True)
    button_continue = types.KeyboardButton(text='Continue ▶')
    button_reset = types.KeyboardButton(text='Reset ♻')
    emptiness = emptiness_location()
    if emptiness:
        markup.add(button_reset, button_continue)
        bot.send_message(message.chat.id, 'Now you can clear your location history.',
                         reply_markup=markup)
    else:
        markup.add(button_location)
        bot.send_message(message.chat.id, 'To perform properly, this bot needs your location.\n',
                         reply_markup=markup)


# Getting location
@bot.message_handler(content_types=['location'])
def get_location(message):
    lat = message.location.latitude
    lon = message.location.longitude
    bot.send_message(message.chat.id, 'Thanks, now you can choose option.')
    set_location(lat, lon)
    start_message(message)


# Main controller
@bot.message_handler(func=lambda message: message.text == 'Continue ▶')
def start_message(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    button_help = types.InlineKeyboardButton(text='Help', callback_data='help')
    button_weather = types.InlineKeyboardButton(text='Find weather', callback_data='weather')
    button_forecast = types.InlineKeyboardButton(text='Forecast weather', callback_data='forecast')
    markup.add(button_weather, button_forecast, button_help)
    bot.send_message(message.chat.id, f'Welcome to my weather bot, {message.from_user.first_name}!\n'
                                      f'This bot allows you to find out the weather and forecast it.',
                     reply_markup=markup)


# Callback to Help Button
@bot.callback_query_handler(func=lambda callback: callback.data == 'help')
def callback_help(callback):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    back_button = types.KeyboardButton(text='Back')
    markup.add(back_button)

    bot.send_message(callback.message.chat.id,
                     f'To restart the bot - /start\n'
                     f'To find out the weather - click button "Weather"\n'
                     f'To forecast weather - click button "Forecast"\n'
                     f'You must type in your city in English, e.g. Moscow.\n'
                     f'Or allow getting your location by pressing button.\n'
                     f'To read help - click "Help"', reply_markup=markup)
    bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.id)  # Delete prev /start


# Callback to Weather Button
@bot.callback_query_handler(func=lambda callback: callback.data == 'weather')
def callback_weather(callback):
    markup = types.InlineKeyboardMarkup(row_width=1)
    button_location = types.InlineKeyboardButton(text='Location 📍', callback_data='location')
    button_type = types.InlineKeyboardButton(text='Type City ⌨', callback_data='type')
    markup.add(button_location, button_type)
    bot.send_message(callback.message.chat.id, 'Write your city.\n'
                                               'Or show weather by your location.',
                     reply_markup=markup)


# Find weather by sending location
@bot.callback_query_handler(func=lambda callback: callback.data == 'location')
def weather_by_location(callback):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    back_button = types.KeyboardButton(text='Back')
    markup.add(back_button)

    weather_request = requests.get(f'https://api.openweathermap.org/data/2.5/weather?lat={Location.latitude}'
                                   f'&lon={Location.longitude}&appid={private.weather_appid}')
    main_info = json.loads(weather_request.text)['weather'][0]['main']
    more_info = json.loads(weather_request.text)['weather'][0]['description']
    temperature = json.loads(weather_request.text)['main']['temp']  # Kelvin
    temperature = float(temperature) - 273.15  # Celsius
    temperature_feels = json.loads(weather_request.text)['main']['feels_like']  # Kelvin
    temperature_feels = float(temperature_feels) - 273.15  # Celsius
    city = json.loads(weather_request.text)['name']

    bot.send_message(callback.message.chat.id, f'Weather for today: \n\n'
                                               f'{main_info}, {more_info}.\n'
                                               f'Temperature: {int(temperature)} °C\n'
                                               f'Feels like: {int(temperature_feels)} °C\n'
                                               f'Location: {city}',
                     reply_markup=markup)


# Type in your city
@bot.callback_query_handler(func=lambda callback: callback.data == 'type')
def weather_typed(callback):
    sent_message = bot.send_message(callback.message.chat.id, 'What is your city?')
    bot.register_next_step_handler(sent_message, weather_by_city)


# Find weather by typing city
def weather_by_city(message):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    back_button = types.KeyboardButton(text='Back')
    markup.add(back_button)

    weather_request = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={message.text}&appid'
                                   f'={private.weather_appid}')
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


# Callback for forecast button
@bot.callback_query_handler(func=lambda callback: callback.data == 'forecast')
def callback_forecast(callback):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    back_button = types.KeyboardButton(text='Back')
    markup.add(back_button)
    forecast_request = requests.get(f'https://api.openweathermap.org/data/2.5/onecall?lat={Location.latitude}'
                                    f'&lon={Location.longitude}'
                                    f'&exclude=minutely,hourly,alerts,'
                                    f'current&appid={private.weather_appid}')

    day_1_temperature = json.loads(forecast_request.text)['daily'][1]['temp']['day']
    day_1_temperature = float(day_1_temperature) - 273.15
    day_1_feels = json.loads(forecast_request.text)['daily'][1]['feels_like']['day']
    day_1_feels = float(day_1_feels) - 273.15
    day_1_main_info = json.loads(forecast_request.text)['daily'][1]['weather'][0]['main']
    day_1_more_info = json.loads(forecast_request.text)['daily'][1]['weather'][0]['description']
    bot.send_message(callback.message.chat.id, f'Weather for tomorrow:\n\n'
                                               f'{day_1_main_info}, {day_1_more_info}.\n'
                                               f'Temperature: {int(day_1_temperature)} °C\n'
                                               f'Feels like: {int(day_1_feels)} °C',
                     reply_markup=markup)


# Back to start
@bot.message_handler(func=lambda message: message.text == 'Back')
def back_handler(message):
    proper_performance(message)


# Clear your history
@bot.message_handler(func=lambda message: message.text == 'Reset ♻')
def reset_handler(message):
    emptiness = emptiness_location()
    if emptiness:
        reset_location()
    proper_performance(message)


bot.infinity_polling()
