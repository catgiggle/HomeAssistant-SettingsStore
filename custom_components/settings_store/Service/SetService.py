import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from ..Utils.Database import Database
from ..constants import *


class SetService:
    def __init__(self, hass):
        self._hass = hass

    def register(self):
        self._hass.services.async_register(
            DOMAIN,
            'set',
            self.handle,
            schema=vol.Schema({
                vol.Required(FIELD_ENTITY_ID): cv.entity_id,
                vol.Optional(FIELD_SCOPE, default=DEFAULT_SCOPE): cv.string,
                vol.Required(FIELD_NAME): cv.string,
                vol.Required(FIELD_VALUE): cv.string,
            })
        )

    async def handle(self, request):
        sensor = self._hass.data[DOMAIN][SENSOR_ENTITIES][request.data[FIELD_ENTITY_ID]]

        await self._hass.async_add_executor_job(
            self._execute,
            sensor.path,
            request.data[FIELD_SCOPE],
            request.data[FIELD_NAME],
            request.data[FIELD_VALUE],
        )
        sensor.refresh()

    def _execute(self, path, scope, name, value):
        with Database.connect(path) as connection:
            connection.execute('''
                INSERT INTO settings_store (scope, name, value)
                VALUES (?, ?, ?)
                ON CONFLICT (scope, name)
                DO UPDATE SET value = excluded.value
            ''', (scope, name, value))
