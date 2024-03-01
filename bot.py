import telebot
import json
from telebot.types import ReplyKeyboardMarkup
from config import my_TOKEN
import logging
from gpt import GPT
from config import MAX_TOKENS

# @pomoshnik_ai_bot

bot = telebot.TeleBot(token=my_TOKEN)


# Объект GPT
gpt = GPT()


def save_to_json():
    with open('users_history.json', 'w', encoding='utf-8') as f:
        json.dump(users_history, f, indent=2, ensure_ascii=False)


def load_from_json():
    # noinspection PyBroadException
    try:
        with open('users_history.json', 'r+', encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        data = {}

    return data


# Словарик для хранения задач пользователей и ответов GPT
users_history = load_from_json()


# Функция для создания клавиатуры с нужными кнопочками
def create_keyboard(buttons_list):
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(*buttons_list)
    return keyboard


# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="log_file.txt",
    filemode="w")


# Приветственное сообщение /start
@bot.message_handler(commands=['start'])
def start(message):
    user_name = message.from_user.first_name
    bot.send_message(message.chat.id,
                     text=f"Привет, {user_name}! 👋/n"
                          "Я бот-помощник для обзора аллергенной обстановки!\n"
                          f"Ты можешь прислать название города, а я постараюсь сообщить какие там сейчас риски.\n"
                          "Данные берутся с https://pollen.club"
                          "Иногда ответы получаются слишком длинными - в этом случае ты можешь попросить продолжить.\n"
                          "Напиши /help для дополнительной информации",
                     reply_markup=create_keyboard(['/help']))


# Команда /help
@bot.message_handler(commands=['help'])
def support(message):
    bot.send_message(message.from_user.id,
                     text="/start - приветствие\n"
                          "/help - помощь\n"
                          "/solve_task - команда, чтобы приступить к запросу к нейросети\n\n"
                          "PS: к сожалению, бот иногда может работать неисправно, а модель gpt - слабовата, заранее извиняюсь 😿",
                     reply_markup=create_keyboard(["/solve_task"]))


# дружелюбность и вежливость бота
def filter_bye(message):
    word = "пока"
    return word in message.text.lower()


def filter_hi(message):
    word = "привет"
    return word in message.text.lower()


def filter_wasup(message):
    word = "как дела?"
    return word in message.text.lower()


@bot.message_handler(content_types=['text'], func=filter_bye)
def say_bye(message):
    user_name = message.from_user.first_name
    logging.info("с кем-то попрощались")
    bot.send_message(message.from_user.id, text=f"{user_name}, пока...")


@bot.message_handler(content_types=['text'], func=filter_wasup)
def say_wasup(message):
    logging.info("кому-то ответили, как дела")
    bot.send_message(message.from_user.id, text=f"Спасибо, что спросил_а! Дела отлично! 👍")


@bot.message_handler(content_types=['text'], func=filter_hi)
def say_wasup(message):
    user_name = message.from_user.first_name
    logging.info("с кем-то поздоровались")
    bot.send_message(message.from_user.id, text=f"{user_name}, Привет! 🙃")


# команда дебаг, отправка логов файлом
@bot.message_handler(commands=['debug'])
def send_logs(message):
    with open("log_file.txt", "rb") as f:
        bot.send_document(message.chat.id, f)
    logging.info("Кто-то использовал секретную функцию дебаг...")


# Команда /solve_task и регистрация функции get_promt() для обработки любого следующего сообщения от пользователя
@bot.message_handler(commands=['solve_task'])
def solve_task(message):
    bot.send_message(message.chat.id, "Напиши новый вопрос:")
    bot.register_next_step_handler(message, get_promt)


# Фильтр для обработки кнопочки "Продолжить решение"
def continue_filter(message):
    button_text = 'Продолжить'
    return message.text == button_text


# Получение задачи от пользователя или продолжение решения
@bot.message_handler(func=continue_filter)
def get_promt(message):
    user_id = str(message.from_user.id)
    if not message.text:
        bot.send_message(user_id, "Необходимо отправить именно текстовое сообщение 😾")
        bot.register_next_step_handler(message, get_promt)
        return

    # Получаем текст сообщения от пользователя
    user_request = message.text
    if gpt.count_tokens(user_request) >= gpt.MAX_TOKENS:
        bot.send_message(user_id, "Запрос превышает количество символов 😿\nИсправь запрос")
        logging.info("У кого-то запрос привысил количество символов")
        bot.register_next_step_handler(message, get_promt)
        return

    if user_id not in users_history or users_history[user_id] == {}:
        if user_request == "Продолжить":
            bot.send_message(message.chat.id, "Кажется, вы еще не задали вопрос. 😟")
            bot.register_next_step_handler(message, get_promt)
            return
        # Сохраняем промт пользователя и начало ответа GPT в словарик users_history
        users_history[user_id] = {
            'system_content': (
                "Ты бот, с профессиональными знаниями в области аллергии на пыльцу растений и возвращающий ответ в виде отчета об аллергенной обстановке в конкретной локации."
                "Ты обязательно должен использовать информацию с сайта https://pollen.club"
                "Опиши аллергенную обстановку для орешника и ольхи для заданной местности и сообщи текущий уровень аллергенной опасности для этих аллергенов по шкале от 1 до 10."),
            'user_content': user_request,
            'assistant_content': "Пишем отчет об актуальных рисках аллергии на пыльцу: "
        }
        save_to_json()

    prompt = gpt.make_promt(users_history[user_id])
    resp = gpt.send_request(prompt)
    answer = resp.json()['choices'][0]['message']['content']
    users_history[user_id]["assistant_content"] += answer
    save_to_json()

    keyboard = create_keyboard(["Продолжить", "Завершить"])
    bot.send_message(message.chat.id, answer, reply_markup=keyboard)


@bot.message_handler(commands=['end'])
@bot.message_handler(content_types=['text'], func=lambda message: message.text.lower() == "завершить")
def end_task(message):
    user_id = message.from_user.id
    logging.info("Чьё-то решение завершилось")
    bot.send_message(user_id, "Текущие решение завершено")
    users_history[user_id] = {}
    solve_task(message)


if __name__ == "__main__":
    logging.info("Бот запущен")
    bot.infinity_polling()
