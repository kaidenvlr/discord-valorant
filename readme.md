# Discord bot for checking valorant store
Данный бот написан на Python, c использованием [discord.py](https://github.com/Rapptz/discord.py)

## Команды бота

### создание события
>`/create_event <month> <day> <hour> <minute> [channel_id] [name]` - создает ивент в 
> этом году, в установленную дату и время в канале с ID `channel_id` и названием `name`

### гифки

>`/hug <member>`- обнимающиеся челы с указанием, что вы обнимаете упомянутого пользователя

>`/pat <member>` - чел гладит другого чела с указанием, что вы гладите упомянутого пользователя

>`/punch <member>` - чел бьет другого чела с указанием, что вы бьете упомянутого пользователя

### валорант

>`/login <username> <password>` - вносите свои логин и пароль в базу данных

>`/logout` - убираете свои данные из базы данных

>`/stats <nickname> <tag>` - отображает статистику игрока с RiotId `nickname#tag` 

>`/shop` - отображает текущий магазин в валоранте (работает через раз я хз как починить)


## Запуск бота
Получите токены Tenor API и Discord API по указанным ссылкам:
>[Tenor](https://tenor.com/gifapi/documentation#quickstart)\
>[Discord](https://discord.com/developers/applications)

После получения токенов, переименуйте файл `.env.dist` и внесите свои значения 
токенов, региона трекинга магазина, конфигурации базы данных (в боте была 
использована `mysql`), ID сервера, ID ролей администратора и клоз-модератора, 
ID канала, в котором по умолчанию будут проводиться клозы.  

В cmd/bash: 

```
pip3 install -r requirements.txt
python3 bot.py
```

## Добавление  функций бота
Для добавления своей функции в директории`discord_bot/cogs` создайте пакет со своей 
категорией функции и используйте шаблон, расположенный в `discord_bot/cogs/test`. 
Затем добавьте в файле `bot.py`, расположенный в корневом каталоге, в список, 
показанный ниже, свою функцию в формате 
`"discord_bot.cogs.<название категории>.<название файла>"`
```
cogs: list = [
    "discord_bot.cogs.tracker.login",
    "discord_bot.cogs.tracker.logout",
    "discord_bot.cogs.tracker.shop",
    "discord_bot.cogs.tracker.stats",

    "discord_bot.cogs.actions.actions",

    "discord_bot.cogs.events.close.create",
    "discord_bot.cogs.events.new_member.new_member"
]
```



## Удаление функций бота
Для удаления функции бота удалите каталог, если функция вам больше не понадобится, 
и в файле `bot.py`, расположенный в корневом каталоге, из списка, показанный ниже, 
удалите ненужную функцию.
```
cogs: list = [
    "discord_bot.cogs.tracker.login",
    "discord_bot.cogs.tracker.logout",
    "discord_bot.cogs.tracker.shop",
    "discord_bot.cogs.tracker.stats",

    "discord_bot.cogs.actions.actions",

    "discord_bot.cogs.events.close.create",
    "discord_bot.cogs.events.new_member.new_member"
]
```

