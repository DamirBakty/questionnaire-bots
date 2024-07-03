# БОТЫ на VK и Telegram для викторины

Боты умеют задавать вопросы и проверить на правильность ответов

## Как запустить

* Скачайте код
* Перейдите в корневую папку проекта
* Создайте виртуальное окружение
* Установите зависимости

```bash
$ pip install -r requirements.txt
```


## Установка Redis
[Установите и запустите Redis](https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/), если этого ещё не сделали.


* Создайте .env файл и скопируйте содержимое из .env.example
* Поменяйте данные под свой проект
* * TG_BOT_TOKEN - Токен телеграм бота
* * VK_BOT_TOKEN - API Ключ от бота сообщества в VK.


* Запустите бота для Telegram
```bash
$ python tg_bot.py
```

* Запустите бота для VK
```bash
$ python vk_bot.py
```
