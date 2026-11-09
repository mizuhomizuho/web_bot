import time

from selenium.common import TimeoutException
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from app_vk.models import VKItem, VKProfile
from web_bot.profiles.vk.constants import WAIT_TIME
from web_bot.profiles.vk.context import context
from web_bot.profiles.vk.lib.base import Base
from web_bot.profiles.vk.lib.friends import friends


class Profile(Base):

    def __init__(self):
        super().__init__()

    def start(self) -> None:
        item = VKItem.objects.exclude(is_parsed=True).first()

        if not item:
            item = VKProfile.objects.filter(gender='G').exclude(url__in=VKItem.objects.values('url')).first()

        if not item:
            item = VKProfile.objects.filter(gender='M').exclude(url__in=VKItem.objects.values('url')).first()

        if not item:
            # self.__parse_profile('https://vk.ru/id22626168')
            # return
            raise Exception('start not item')

        self.__parse_profile(item.url)

        time.sleep(1)

        self.start()

    def __parse_profile(self, page_url: str) -> None:
        context.vk_item = VKItem.objects.filter(url=page_url).first()
        if not context.vk_item:
            context.vk_item = VKItem.objects.create(url=page_url)

        attempts = 3
        for attempt in range(attempts):
            try:

                self.__close_all_tabs()

                # open_url(driver, 'https://vk.ru/id168910811')
                self.__go_to_url(page_url)

                context.vk_item.is_private_profile = self.__is_private_profile()
                context.vk_item.profile_id = context.vk_item.profile_id \
                    if context.vk_item.profile_id else self.__get_profile_id()
                context.vk_item.save()

                check_res = self.__check_fields()

                item_props: list[str] = [
                    'detailed_information_html',
                    'profile_more_html',
                    'photo_page_html',
                ]
                for prop_name in item_props:
                    if not check_res[prop_name]:
                        field_res = getattr(self, f'_Profile__get_field_{prop_name}')()
                        setattr(context.vk_item, prop_name, field_res)
                        context.vk_item.save()

                friends.parse_friends()

                check_res = self.__check_fields()

                if check_res['all']:
                    if context.vk_item.is_private_profile:
                        context.vk_item.is_parsed = True
                        context.vk_item.save()
                    return

            except TimeoutException as e:
                if attempt < attempts - 1:
                    time.sleep(1)
                else:
                    raise e

    def __get_field_profile_more_html(self) -> str:

        _ = self

        element = WebDriverWait(context.driver, WAIT_TIME).until(
            expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, '[data-testid="profile_more_button"]')))

        context.cursor.show_cursor()
        context.cursor.move_to(element)
        context.cursor.click_on(element)

        selector: str = '[data-testid="dropdownactionsheet-content"] [data-testid="profile_more_guest_report"]'
        WebDriverWait(context.driver, WAIT_TIME).until(
            expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, selector)))

        profile_more_html: str = context.driver.execute_script('return document.documentElement.outerHTML;')

        ActionChains(context.driver).send_keys(Keys.ESCAPE).perform()

        return profile_more_html

    def __is_private_profile(self) -> bool:

        _ = self

        element = WebDriverWait(context.driver, WAIT_TIME).until(
            expected_conditions.visibility_of_element_located(
                (By.CSS_SELECTOR, '#spa_layout_content .Profile__column')))

        return 'Это закрытый профиль' in element.get_attribute('textContent')

    def __get_field_detailed_information_html(self) -> str:

        _ = self

        selector = '[data-testid="profile-info"] [data-testid="profile-full-info-link"]'
        element = WebDriverWait(context.driver, WAIT_TIME).until(
            expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, selector)))

        context.cursor.show_cursor()
        context.cursor.move_to(element)
        context.cursor.click_on(element)

        selector = '[data-testid="profile-details-info-modal"] [data-testid="modalheader"]'
        element = WebDriverWait(context.driver, WAIT_TIME).until(
            expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, selector)))
        if element.get_attribute('textContent') != 'Подробная информацияЗакрыть':
            raise Exception(f'Не удалось открыть окно "Подробная информация" {element.get_attribute('textContent')}')

        detailed_information_html: str = context.driver.execute_script('return document.documentElement.outerHTML;')

        ActionChains(context.driver).send_keys(Keys.ESCAPE).perform()

        return detailed_information_html

    def __get_field_photo_page_html(self) -> str:

        selector: str = '#oct-tab-photos-control'
        # noinspection DuplicatedCode
        elements = WebDriverWait(context.driver, WAIT_TIME).until(
            expected_conditions.visibility_of_all_elements_located((By.CSS_SELECTOR, selector)))
        if len(elements) != 1:
            raise Exception(f'__get_field_photo_page_html len(elements) != 1 {len(elements)}')

        context.cursor.show_cursor()
        context.cursor.move_to(elements[0])
        context.cursor.click_on(elements[0])

        photo_page_html = self._scroll('a[href^="/photo"][data-id]')

        context.driver.back()

        return photo_page_html

    def __go_to_url(self, url) -> None:

        _ = self

        try:
            print(f"Открытие страницы. Попытка {url}")

            context.driver.set_page_load_timeout(5)
            context.driver.get(url)

            WebDriverWait(context.driver, 5).until(
                lambda d: d.execute_script('return document.readyState') in ('interactive', 'complete'))

            print("Страница загружена:", context.driver.current_url)

        except TimeoutException:
            print("Превышено время загрузки. Перезагружаем...")
            context.driver.execute_script("window.stop();")
            ActionChains(context.driver) \
                .key_down(Keys.CONTROL) \
                .send_keys("r") \
                .key_up(Keys.CONTROL) \
                .perform()

    def __check_fields(self) -> dict[str, bool]:

        _ = self

        res = {
            'detailed_information_html': isinstance(
                context.vk_item.detailed_information_html, str) and context.vk_item.detailed_information_html != '',
            'profile_more_html': isinstance(
                context.vk_item.profile_more_html, str) and context.vk_item.profile_more_html != '',
            'photo_page_html': True if context.vk_item.is_private_profile else isinstance(
                context.vk_item.photo_page_html, str) and context.vk_item.photo_page_html != '',
        }

        res['all'] = res['detailed_information_html'] and res['profile_more_html'] and res['photo_page_html']

        return res

    def __get_profile_id(self) -> int:

        _ = self

        elements = WebDriverWait(context.driver, WAIT_TIME).until(
            expected_conditions.visibility_of_all_elements_located((By.CSS_SELECTOR, '[id^="profile_avatar_"]')))

        if len(elements) != 1:
            raise Exception(f'get_profile_id len(elements) != 1 {len(elements)}')

        profile_id: str = elements[0].get_attribute('id').split('_')[2]

        if not profile_id.isdigit():
            raise Exception(f'get_profile_id not profile_id.isdigit() {profile_id}')

        return int(profile_id)

    def __close_all_tabs(self) -> None:

        _ = self

        window_handles = context.driver.window_handles
        window_handles_len = len(context.driver.window_handles)
        window_handles_i = 0
        for handle in window_handles:
            context.driver.switch_to.window(handle)
            if window_handles_i == window_handles_len - 1:
                break
            context.driver.close()
            window_handles_i = window_handles_i + 1


profile = Profile()
