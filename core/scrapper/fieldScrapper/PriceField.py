from core.scrapper.absrtract.AbstractParseField import AbstractParseField


class PriceField(AbstractParseField):
    def __init__(self):
        super(PriceField, self).__init__("price")

    def _find_field_in_html(self, html: dict) -> dict:
        pass