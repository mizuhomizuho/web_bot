
from web_bot.profiles.vk.context import context
from web_bot.profiles.vk.lib.profile import profile


def start() -> None:
    context.init_vk_context()
    # context.vk_profile.parse_profile(driver, 'https://vk.ru/id61435926')
    # profile.parse_profile('https://vk.ru/m.d.belozerova0206')
    # profile.parse_profile('https://vk.ru/volkonskaya1995')

    profile.start()
