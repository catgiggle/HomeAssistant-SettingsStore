import voluptuous as vol

from ..constants import FIELD_ID, FIELD_NAME, FIELD_SCOPE


class EntrySelectorValidator:
    @staticmethod
    def validate(data):
        if not ((FIELD_ID in data) ^ (FIELD_NAME in data)):
            raise vol.Invalid('Provide exactly one of id or name')

        if FIELD_ID in data and FIELD_SCOPE in data:
            raise vol.Invalid('Scope cannot be provided with id')

        return data
