import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from ..constants import *
from ..utils.Database import Database


class GetService:
    def __init__(self, hass):
        self._hass = hass

    def register(self):
        self._hass.services.async_register(
            DOMAIN,
            'get',
            self.handle,
            schema=vol.Schema({
                vol.Required(FIELD_ENTITY_ID): cv.entity_id,
                vol.Optional(FIELD_SCOPE, default=DEFAULT_SCOPE): cv.string,
                vol.Required(FIELD_NAME): cv.string,
            }),
            supports_response=True
        )

    async def handle(self, request):
        sensor = self._hass.data[DOMAIN][SENSOR_ENTITIES][request.data[FIELD_ENTITY_ID]]

        result = await self._hass.async_add_executor_job(
            self._execute,
            sensor.path,
            request.data[FIELD_SCOPE],
            request.data[FIELD_NAME],
        )

        return {
            "value": result[0] if result else None
        }

    def _execute(self, path, scope, name):
        with Database.connect(path) as connection:
            return connection.execute('''
                SELECT value
                FROM settings_store
                WHERE scope = ? AND name = ?
            ''', (scope, name)).fetchone()
