from abc import ABC, abstractmethod


class AbstractParseField(ABC):
    def __init__(self, field_name: str):
        self.field_name = field_name

    def __repr__(self):
        return f"FieldScrapper_{self.field_name}"

    @abstractmethod
    def _find_field_in_html(self, html: dict) -> dict:
        pass

    def collect_field(self, html: dict) -> dict:
        _result = self._find_field_in_html(html=html)
        return {self.field_name: _result}
