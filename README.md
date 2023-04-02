# Бот "Фотоконкурс"

#### _# photo-contest-bot_

### Технологии
<p>
<img src="https://habrastorage.org/webt/46/r2/ba/46r2baf00uhoixq-saia7wegqfu.jpeg" title="VK API" height="50"/>
<img src="https://docs.aiohttp.org/en/stable/_static/aiohttp-plain.svg" title="Aiohttp" height="50"/>
<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/2/29/Postgresql_elephant.svg/1200px-Postgresql_elephant.svg.png" title="PostgreSQL" height="50"/>
<img src="https://assets.zabbix.com/img/brands/rabbitmq.svg" title="RabbitMQ" height="50"/>
<img src="https://files.virgool.io/upload/users/30711/posts/mivbx6r9geed/nwqgenmrbrfc.jpeg" title="Asyncio" height="50"/>
<img src="https://www.blender.org/wp-content/uploads/2021/11/alembic_logo_symbol.png" title="Alembc" height="50"/>
<img src="https://quintagroup.com/cms/python/images/sqlalchemy-logo.png/@@images/eca35254-a2db-47a8-850b-2678f7f8bc09.png" title="SQLAlchemy" height="50"/>
<img src="https://res.cloudinary.com/postman/image/upload/t_team_logo/v1629869194/team/2893aede23f01bfcbd2319326bc96a6ed0524eba759745ed6d73405a3a8b67a8" title="Postman" height="50"/><br>
</p>

### Poller    
Получает обновления с внешнего сервера (vk) и передает их на дальнейшую обработку.

### Worker
Получает сообщения, которые приходят от Poller'а, 
и обрабатывает их, реализуя логику игры. Возвращает в очередь конечный результат - сообщение для отправки.

### Sender
Отправляет полученные от Worker'а сообщения пользователям в беседу (vk).

### Web -> App
Веб-интерфейс для получения администратором дополнительной информации и управления ботом. <br>

**Запуск бота**    
```python main.py```

**Запуск веб-интерфейса**    
```python main_app.py ```    

**Запуск тестов**   
```pytest -v```

### Доступные команды/кнопки
Команды пишутся в чат без знаков препинания, кавычек и других символов.    
_Общее управление_     
:pushpin: _starting/Запустить конкурс_ - запускает конкурс, если достаточно участников;    
:pushpin: _help/Доступные команды_ - выводит подробную инструкцию о возможностях бота, которую Вы сейчас читаете;    
:pushpin: _rules/Правила конкурса_ - выводит правила проведения конкурса;    
:pushpin: _score/Победитель прошлой игры_ - показывает список активных участников - тех, кто еще не выбыл;    
:pushpin: _stop/Закончить конкурс_ - досрочно заканчивает конкурс и выбирает победителя из активных участников на момент остановки;    
:pushpin: Кнопка _'Долго не отвечаю? Тык сюда!'_ перезапускает игру с того места, на которой она зависла,
  например, из-за сбоя сервера или каких-то других причин.    

_Кнопки голосования_    
:pushpin: Две верхние кнопки подписаны именами участников раунда и соответствуют по порядку левому и правому участнику;    
:pushpin: Кнопка _'Пусть решит случай'_ случайно отдает голос за одного из участников раунда.    

#### Архитектура
![](https://sun9-14.userapi.com/impg/FX2W-sQjrw6SdMqHtuyf35r9q_QoMB3gIYgAbQ/Amj4o0wFWto.jpg?size=716x441&quality=95&sign=4d52a5ee4b4831cec6b34677f0335ce3&type=album)

