import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from ..constants import *
from ..utils.Database import Database


class ClearService:
    def __init__(self, hass):
        self._hass = hass

    def register(self):
        self._hass.services.async_register(
            DOMAIN,
            'clear',
            self.handle,
            schema=vol.Schema({
                vol.Required(FIELD_STORE): cv.entity_id,
                vol.Optional(FIELD_SCOPE): cv.string,
            })
        )

    async def handle(self, request):
        sensor = self._hass.data[DOMAIN][SENSOR_ENTITIES][request.data[FIELD_STORE]]

        if request.data.get(FIELD_SCOPE) == '*':
            await self._hass.async_add_executor_job(
                self._execute_clear_all,
                sensor.path,
            )
        else:
            await self._hass.async_add_executor_job(
                self._execute_clear_scope,
                sensor.path,
                request.data.get(FIELD_SCOPE, DEFAULT_SCOPE),
            )

        sensor.refresh()

    @staticmethod
    def _execute_clear_all(path):
        with Database.connect(path) as connection:
            connection.execute('''
                DELETE FROM settings_store
            ''')

    @staticmethod
    def _execute_clear_scope(path, scope):
        with Database.connect(path) as connection:
            connection.execute('''
                DELETE FROM settings_store
                WHERE scope = ?
            ''', (scope,))
