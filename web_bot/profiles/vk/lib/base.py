import time
from collections.abc import Callable

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from web_bot.profiles.vk.constants import WAIT_TIME
from web_bot.profiles.vk.context import context


class Base:
    def __init__(self):
        pass

    def _kebab_to_camel(self, value: str) -> str:

        _ = self

        parts = value.split('-')
        return parts[0] + ''.join(word.capitalize() for word in parts[1:])

    def _scroll(self, selector_part: str, func: Callable | None = None) -> str:

        _ = self

        last_element = None
        while True:

            if func is not None:
                func()

            selector: str = f'{selector_part}:last-child'
            elements = WebDriverWait(context.driver, WAIT_TIME).until(
                expected_conditions.visibility_of_all_elements_located((By.CSS_SELECTOR, selector)))

            if last_element == elements[len(elements) - 1]:
                break

            last_element = elements[len(elements) - 1]
            print('scrollIntoView')
            context.driver.execute_script('arguments[0].scrollIntoView({block: "center"});', last_element)

            time.sleep(2)

        return context.driver.execute_script('return document.documentElement.outerHTML;')
