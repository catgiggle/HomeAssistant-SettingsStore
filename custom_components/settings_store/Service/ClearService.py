import sqlite3

import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from ..constants import *


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

        with sqlite3.connect(sensor.path) as connection:
            connection.execute('''
                DELETE FROM settings_store
            ''')

        sensor.refresh()
