from core.scrapper.absrtract.AbstractParseField import AbstractParseField


class IdCianField(AbstractParseField):
    def __init__(self):
        super().__init__(field_name="id_cian")

    def _find_field_in_html(self, html: dict) -> dict:
        pass

