# Shizocells
## Сайт  и аналог дейтинга "Леонардо Дайвинчик" для нишевого телеграм сообщества
Данный pet-проект был создан для ознакомления с созданием и деплоем сайтов на Flask'е и оптимизированных aiogram ботов.
## 🛠 Установка и запуск
### 1. Клонирование проекта и установка зависимостей
```
git clone https://github.com/FedorLukin/shizobot.git
```
Создайте виртаульное окружение, активируйте его и установите зависимости из requirements.txt:
```
   sudo apt update
   sudo apt install python3-venv
   python3 -m venv venv
   source venv/bin/activate
   pip instal -r requirements.txt
```
### 2. Настройка домена, SSL и Nginx
Для запуска сайта необходимо зарегестрировать домен и настроить nginx реверс-проксирование, а также gunicorn-WSGI. После регистрации домена необходимо создать А-запись для домена с ip-адрессом вашего сервера. Затем необходимо выпустить SSL-сертификат для домена, чтобы обеспечить поддержку протокола HTTPS.
Для выпуска сертификата установите certbot:
```
sudo apt install certbot
```
Убедитесь, что на сервере не используется 80 порт, завершите процесс использующий его, указав его PID:
```
sudo netstat -tuln | grep :80
sudo kill <PID>
```
Выпустите сертификат для вашего домена.
```
sudo certbot certonly --standalone -d your_domain.ru
```
Установите nginx и добавьте его в автозагрузку.
```
sudo apt install nginx
sudo systemctl enable nginx
```
Создайте файл конфигурации виртуальных хостов /etc/nginx/sites-available/your_domain, для настройки реверс-проксирования домена сайта и вебхука телеграм-бота со следующим содержанием:
```
server {
    listen 80;
    server_name your_domain.ru www.your_domain.ru;

    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name your_domain.ru your_domain.ru;

    ssl_certificate /etc/letsencrypt/live/your_domain.ru/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your_domain.ru/privkey.pem;

    # Webhook для aiogram
    location /webhook {
        proxy_set_header Host $http_host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_buffering off;
        proxy_pass http://127.0.0.1:<port>; # Укажите порт вашего веб-сервера бота
    }

    # Основной сайт
    location / {
        proxy_set_header Host $http_host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_buffering off;
        proxy_pass http://127.0.0.1:<port>; # Укажите порт на котором запущен gunicorn
    }
}
```
### 3. Создание скрипта запуска (start.sh)

Создайте shell скрипт в директории проекта:

```
#!/bin/bash
source /shizobot/venv/bin/activate
python3.12 -m bot &
cd /shizobot/website
gunicorn --workers 4 -b 127.0.0.1:<port> app:app # Укажите порт на котором запускаете gunicorn
```
Сделайте его исполняемым:
```
chmod +x start.sh
```
### 4. Создание Systemd Unit-файла
Создайте /etc/systemd/system/shizobot.service файл, выполняющий данный скрипт, он обеспечит бесперебойную работу проекта даже в случае перезагрузки сервера:
```
[Unit]
Description=Shizocells Telegram Bot and Website Service
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/shizobot
ExecStart=/shizobot/start.sh
StandardOutput=journal
StandardError=journal
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```
### 5. Настройка базы данных и применение миграций
Для функционирования бота необходима postgresql база данных. Устанавливаем postgresql и драйверы, если psql не установлен:
```
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql.service
```
Создаём пользователя и базу данных:
```
psql postgres
CREATE USER <username> WITH PASSWORD '<password>';
CREATE DATABASE <database name>;
GRANT ALL PRIVILEGES ON DATABASE <database name> to <username>;
ALTER USER <username> WITH SUPERUSER;
GRANT postgres TO <username>;
```
 После этого необходимо создать .env файл в директории проекта и внести в него все данные касающиеся базы данных и затем провести миграцию, используя alembic:
```
alembic upgrade head
```
Для доступа к админ-панели бота необходимо внести tg id аккаунта админа в таблицу admins базы данных:

```
INSERT INTO admins VALUES (<admin_id>)
```
### 6. Настройка переменных окружения и запуск проекта
Для запуска проекта необходимо внести все переменные окружения в .env по образцу .env.example. Для корректного определения города, указанного пользователем бота, потребуется получить бесплатный api-ключ разработчика для доступа к api yandex maps, сделать это можно [здесь](https://developer.tech.yandex.ru).

После заполнения переменных окружения можно запускать проект:
```
sudo systemctl start shizobot.service
```
