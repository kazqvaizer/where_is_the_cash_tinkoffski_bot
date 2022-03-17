_registry = {
    "general_help": {
        "ru": (
            "Бот собирает данные по банкоматам Тинькофф банка из открытых API.\n"
            "Сообщает в реальном времени изменения остатков.\n"
            "Набери /where для отображения актуальных остатков.\n\n"
            "Работает пока что в г. Хабаровск.\n"
        ),
    },
}


class CommonMessages:
    """Simple registry with all common replies."""

    def __init__(self, language_code: str = "ru"):
        self.language_code = language_code

    def get_message(self, slug: str) -> str:
        messages = _registry[slug]
        return messages.get(self.language_code)
