import sqlite3

import homeassistant.helpers.config_validation as cv
import voluptuous as vol

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
                vol.Required(FIELD_SCOPE): cv.string,
                vol.Required(FIELD_NAME): cv.string,
                vol.Required(FIELD_VALUE): cv.string,
            })
        )

    async def handle(self, request):
        sensor = self._hass.data[DOMAIN][SENSOR_ENTITIES][request.data[FIELD_ENTITY_ID]]

        with sqlite3.connect(sensor.path) as connection:
            connection.execute('''
                INSERT INTO settings_store (scope, name, value)
                VALUES (?, ?, ?)
                ON CONFLICT (scope, name)
                DO UPDATE SET value = excluded.value
            ''', (
                request.data[FIELD_SCOPE],
                request.data[FIELD_NAME],
                request.data[FIELD_VALUE],
            ))

        sensor.refresh()
