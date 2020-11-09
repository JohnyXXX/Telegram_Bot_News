import configparser
from sys import stderr, stdout

import telebot
from telebot import types

from module import DataBase, Parser
from vk import VkGroupParser

TG_BOT_API_LIMIT_REQUESTS = 19
config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')
bot = telebot.TeleBot(config['telegram']['tg_bot_token'])


def markup_text_gen(text):
    if 'mediakub.net' in text['url']:
        return '🔗 МедиаКУБ'
    elif 'gubakhaokrug.ru' in text['url']:
        return '🔗 Губахинский городской округ'
    elif 'newgubakha.ru' in text['url']:
        return '🔗 Новая Губаха'
    elif 'nashagubaha.ru' in text['url']:
        return '🔗 Наша Губаха'


class Main:
    def __init__(self):
        self.db = DataBase('db')
        self.p = Parser()
        self.vk = VkGroupParser()

    def __prepare_message_for_send(self, text):
        self.rhash = None
        if 'mediakub.net' in text['url']:
            self.rhash = config['telegram_rhash']['RHASH_MEDIAKUB']
        elif 'gubakhaokrug.ru' in text['url']:
            self.rhash = config['telegram_rhash']['RHASH_GUBAKHAOKRUG']
        elif 'newgubakha.ru' in text['url']:
            self.rhash = config['telegram_rhash']['RHASH_NEWGUBAKHA']
        elif 'nashagubaha.ru' in text['url']:
            self.rhash = config['telegram_rhash']['RHASH_NASHAGUBAHA']
        return '<a href="https://t.me/iv?url={}&rhash={}">{}</a>'.format(text['url'], self.rhash, text['title'])

    def __send_message_to_tg_channel(self, chat_id, item, parse_mode='HTML'):
        markup = types.InlineKeyboardMarkup()
        btn_my_site = types.InlineKeyboardButton(text=markup_text_gen(item), url=item['url'])
        markup.add(btn_my_site)
        bot.send_message(chat_id=chat_id, text=self.__prepare_message_for_send(item), parse_mode=parse_mode,
                         reply_markup=markup)

    @staticmethod
    def __send_photo_to_tg_channel(chat_id, item):
        msg = bot.send_photo(chat_id=chat_id, photo=item['url'], caption=item['title'])
        bot.pin_chat_message(msg.chat.id, msg.message_id)

    def run(self):
        counter = 0
        try:
            for item in self.p.run():
                if item['url'] in self.db.urls_from_db():
                    continue
                else:
                    if counter <= TG_BOT_API_LIMIT_REQUESTS:
                        self.__send_message_to_tg_channel(config.get('telegram', 'tg_id_channel'), item)
                        self.db.add_to_db(item)
                        counter += 1
                        print('Send to Telegram', item, file=stdout)
            for item in self.vk.vk_wall_search():
                if item['title'] in self.db.titles_from_db():
                    continue
                else:
                    if counter <= TG_BOT_API_LIMIT_REQUESTS:
                        self.__send_photo_to_tg_channel(config.get('telegram', 'tg_id_channel'), item)
                        self.db.add_to_db(item)
                        counter += 1
                        print('Send to Telegram', item, file=stdout)
        except Exception as e:
            print(e, file=stderr)


if __name__ == '__main__':
    start = Main()
    start.run()
