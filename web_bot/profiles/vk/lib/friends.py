import time

from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.mouse_button import MouseButton
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from app_vk.models import VKProfile
from web_bot.profiles.vk.constants import WAIT_TIME
from web_bot.profiles.vk.context import context
from web_bot.profiles.vk.lib.base import Base


class Friends(Base):

    def __init__(self) -> None:
        super().__init__()

    def parse_friends(self, is_step2: bool = False) -> None:

        if context.vk_item.is_private_profile:
            return

        check_res = self.__check_fields()

        if check_res['all']:
            self.__handle_profiles()
            return

        if not is_step2:
            self.__open_friends_tab()

        if check_res['friends_moscow_all_links'] and not is_step2:
            self.parse_friends(True)
            return

        avatar_selector: str = '[data-testid=userrichcell-avatar] > a[href]'

        must_disappear_prop: str = 'must-disappear-item'
        must_disappear_camel: str = self._kebab_to_camel(must_disappear_prop)

        context.driver.execute_script(
            f'document.querySelectorAll("{avatar_selector}").forEach(el => el.dataset.{must_disappear_camel} = "true")')

        context.driver.execute_script('window.scrollTo(0, 0);')

        self.__set_search_params(is_step2)

        empty_selector: str = '[data-testid="friends_of_friend_all_search_empty_placeholder"]'

        selectors = [f'{avatar_selector}:not([data-{must_disappear_prop}="true"])', empty_selector]
        result = WebDriverWait(context.driver, WAIT_TIME).until(
            lambda d: next(
                (
                    (selector_str, found) for selector_str in selectors
                    if (found := [el for el in d.find_elements(By.CSS_SELECTOR, selector_str) if el.is_displayed()])
                ),
                False
            )
        )

        selector_found, elements = result

        links = 'EMPTY'
        if selector_found != empty_selector:
            links_arr = []

            def parse():
                link_elements = WebDriverWait(context.driver, WAIT_TIME).until(
                    expected_conditions.visibility_of_all_elements_located((By.CSS_SELECTOR, avatar_selector)))
                for element in link_elements:
                    href = element.get_attribute('href')
                    if href in links_arr:
                        continue
                    links_arr.append(href)

            self._scroll(selector_found, parse)
            if len(links_arr):
                links = '\n'.join(links_arr)

        setattr(context.vk_item, 'friends_moscow_girl_links' if is_step2 else 'friends_moscow_all_links', links)
        context.vk_item.save()

        if not is_step2:
            self.parse_friends(True)
            return

        check_res = self.__check_fields()

        if is_step2 and not check_res['all']:
            raise Exception('parse_friends is_step2 and not check_res all')

        if is_step2:
            self.__handle_profiles()

    def __handle_profiles(self) -> None:

        _ = self

        links: str = context.vk_item.friends_moscow_all_links

        if links == 'EMPTY':
            return

        links_all = links.split('\n')

        links: str = context.vk_item.friends_moscow_girl_links

        if links == 'EMPTY' and not len(links_all):
            return

        links_girl = links.split('\n')

        links_res = []
        for link in links_all:
            links_res.append(VKProfile(url=link, gender='G' if link in links_girl else 'M'))

        if len(links):
            VKProfile.objects.bulk_create(links_res, ignore_conflicts=True)

        context.vk_item.is_parsed = True
        context.vk_item.save()

    def __check_fields(self) -> dict[str, bool]:

        _ = self

        res = {
            'friends_moscow_all_links': isinstance(
                context.vk_item.friends_moscow_all_links, str) and context.vk_item.friends_moscow_all_links != '',
            'friends_moscow_girl_links': isinstance(
                context.vk_item.friends_moscow_girl_links, str) and context.vk_item.friends_moscow_girl_links != '',
        }

        res['all'] = res['friends_moscow_all_links'] and res['friends_moscow_girl_links']

        return res

    def __set_search_params(self, is_step2: bool) -> None:

        _ = self

        selector = '[data-testid="friends_of_friend_page"]'
        element = WebDriverWait(context.driver, WAIT_TIME).until(
            expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, selector)))
        context.cursor.show_cursor()
        context.cursor.move_to([element.rect['x'] + 514, element.rect['y'] + 120])

        time.sleep(1)

        context.driver.switch_to.active_element.clear()
        context.driver.switch_to.active_element.send_keys('Москва')
        ActionChains(context.driver).send_keys(Keys.ARROW_DOWN).perform()
        ActionChains(context.driver).send_keys(Keys.ARROW_DOWN).perform()
        ActionChains(context.driver).send_keys(Keys.ENTER).perform()
        time.sleep(1)

        if is_step2:
            ActionChains(context.driver).send_keys(Keys.TAB).perform()
            ActionChains(context.driver).send_keys(Keys.TAB).perform()
            ActionChains(context.driver).send_keys(Keys.TAB).perform()
            ActionChains(context.driver).send_keys(Keys.TAB).perform()
            ActionChains(context.driver).send_keys(Keys.ARROW_DOWN).perform()
            time.sleep(1)

        ActionChains(context.driver).send_keys(Keys.ESCAPE).perform()

    def __open_friends_tab(self) -> None:

        _ = self

        old_tab = context.driver.current_window_handle

        selector = 'a[href^="/friends?id="]'
        element = WebDriverWait(context.driver, WAIT_TIME).until(
            expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, selector))
        )
        context.cursor.show_cursor()
        context.cursor.move_to(element)
        actions = ActionBuilder(context.driver)
        actions.pointer_action.pointer_down(MouseButton.MIDDLE)
        actions.pointer_action.pointer_up(MouseButton.MIDDLE)
        actions.perform()

        WebDriverWait(context.driver, WAIT_TIME).until(
            lambda d: len(d.window_handles) > 1
        )
        new_tab = next(
            handle for handle in context.driver.window_handles
            if handle != old_tab
        )
        context.driver.switch_to.window(new_tab)


friends = Friends()
