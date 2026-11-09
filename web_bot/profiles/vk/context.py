from app_vk.models import VKItem
from web_bot.context import Context as MainContext
from web_bot.context import context as main_context


class Context(MainContext):
    vk_item: VKItem | None = None

    def init_vk_context(self) -> None:
        _ = self
        for field_name in list(MainContext.model_fields.keys()):
            setattr(context, field_name, getattr(main_context, field_name))


context = Context()
