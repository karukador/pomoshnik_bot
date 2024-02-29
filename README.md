# Бот помощник
бот помощник для telegram на python с нейросетью
# Как использовать
1) Клонируйте этот репозиторий:
```
git clone https://github.com/karukador/pomoshnik_bot.git
```
2) Установите requirements
3) Получите токен через [BotFather](https://telegram.me/BotFather) в Telegram 
4) Создайте файл config.py со следующим кодом:
```
my_TOKEN = "ВАШ ТОКЕН"
GPT_LOCAL_URL = 'http://localhost:1234/v1/chat/completions'
HEADERS = {"Content-Type": "application/json"}
MAX_TOKENS = 150
```
5) Установите LM Studio
6) Установите mistralai/Mistral-7B-Instruct-v0.2 (или другую нейросеть, которую вы используете)
7) Запустите вашу нейросеть
8) Запустите bot.py
