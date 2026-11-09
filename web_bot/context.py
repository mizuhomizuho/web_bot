from humancursor import WebCursor
from pydantic import BaseModel, ConfigDict
from selenium import webdriver


class Context(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    driver: webdriver.Chrome | None = None
    cursor: WebCursor | None = None


context = Context()
