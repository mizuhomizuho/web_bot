# web_bot

```shell
python -m venv .venv && source .venv/bin/activate && python --version
#Python 3.12.13
poetry install
python django_5/manage.py migrate
mysql -h localhost -u parser -pparser parser < dump.sql
python django_5/manage.py runserver 8008
#Login: admin
#Password: admin

python -m web_bot vk
```

```shell
python django_5/manage.py makemigrations
python django_5/manage.py migrate
```