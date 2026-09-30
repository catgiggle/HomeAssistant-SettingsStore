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
                vol.Required(FIELD_ENTITY_ID): cv.entity_id,
            })
        )

    async def handle(self, request):
        sensor = self._hass.data[DOMAIN][SENSOR_ENTITIES][request.data[FIELD_ENTITY_ID]]

        await self._hass.async_add_executor_job(self._execute, sensor.path)
        sensor.refresh()

    def _execute(self, path):
        with Database.connect(path) as connection:
            connection.execute('''
                DELETE FROM settings_store
            ''')
