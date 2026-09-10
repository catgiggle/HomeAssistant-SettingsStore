import sqlite3

import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from ..constants import *


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
                vol.Required(FIELD_SCOPE): cv.string,
                vol.Required(FIELD_NAME): cv.string,
            }),
            supports_response=True
        )

    async def handle(self, request):
        sensor = self._hass.data[DOMAIN][SENSOR_ENTITIES][request.data[FIELD_ENTITY_ID]]

        with sqlite3.connect(sensor.path) as connection:
            result = connection.execute('''
                SELECT value
                FROM settings_store
                WHERE scope = ? AND name = ?
            ''', (
                request.data[FIELD_SCOPE],
                request.data[FIELD_NAME],
            )).fetchone()

            return {
                "value": result[0] if result else None
            }
