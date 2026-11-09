import importlib
import os
import sys
import time

import django
from dotenv import load_dotenv
from humancursor import WebCursor
from selenium import webdriver

from web_bot.context import context

load_dotenv(dotenv_path=f'{os.path.dirname(os.path.abspath(__file__))}/../.env')

if len(sys.argv) < 2:
    print("Ошибка: не передан каталог профиля")
    sys.exit(1)

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../django_5'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_5.settings')
# os.environ['DJANGO_ALLOW_ASYNC_UNSAFE'] = 'true'
django.setup()

options = webdriver.ChromeOptions()
options.binary_location = os.environ.get('CHROME_APP_PATH')
# options.add_argument('--headless')
options.add_argument('--disable-extensions')
# https://github.com/ultrafunkamsterdam/undetected-chromedriver
# https://intoli.com/blog/not-possible-to-block-chrome-headless/chrome-headless-test.html
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument(f'--user-data-dir={os.environ.get('CHROME_USER_DATA_PATH')}')
options.add_argument(f'--profile-directory=Default')

context.driver = webdriver.Chrome(options=options)
context.cursor = WebCursor(context.driver)

try:
    context.driver.maximize_window()
    getattr(importlib.import_module(f'web_bot.profiles.{sys.argv[1]}.main'), 'start')()
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print('\nОстановка...')

except Exception as e:
    raise e

finally:
    context.driver.quit()
