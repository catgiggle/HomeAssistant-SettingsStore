import sqlite3

import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from ..constants import *


class DeleteService:
    def __init__(self, hass):
        self._hass = hass

    def register(self):
        self._hass.services.async_register(
            DOMAIN,
            'delete',
            self.handle,
            schema=vol.Schema({
                vol.Required(FIELD_ENTITY_ID): cv.entity_id,
                vol.Required(FIELD_SCOPE): cv.string,
                vol.Required(FIELD_NAME): cv.string,
            })
        )

    async def handle(self, request):
        sensor = self._hass.data[DOMAIN][SENSOR_ENTITIES][request.data[FIELD_ENTITY_ID]]

        with sqlite3.connect(sensor.path) as connection:
            connection.execute('''
                DELETE FROM settings_store
                WHERE scope = ? AND name = ?
            ''', (
                request.data[FIELD_SCOPE],
                request.data[FIELD_NAME],
            ))

        sensor.refresh()
