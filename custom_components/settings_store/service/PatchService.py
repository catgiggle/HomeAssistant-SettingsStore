from datetime import datetime

import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from ..constants import *
from ..utils.Database import Database
from ..validator.EntrySelectorValidator import EntrySelectorValidator


class PatchService:
    def __init__(self, hass):
        self._hass = hass

    def register(self):
        self._hass.services.async_register(
            DOMAIN,
            'patch',
            self.handle,
            schema=vol.All(vol.Schema({
                vol.Required(FIELD_STORE): cv.entity_id,
                vol.Optional(FIELD_ID): cv.positive_int,
                vol.Optional(FIELD_NAME): cv.string,
                vol.Optional(FIELD_SCOPE): cv.string,
                vol.Required(FIELD_VALUE): cv.string,
            }), EntrySelectorValidator.validate)
        )

    async def handle(self, request):
        sensor = self._hass.data[DOMAIN][SENSOR_ENTITIES][request.data[FIELD_STORE]]

        if FIELD_ID in request.data:
            await self._hass.async_add_executor_job(
                self._execute_by_id,
                sensor.path,
                request.data.get(FIELD_ID),
                request.data.get(FIELD_VALUE),
            )

        if FIELD_NAME in request.data:
            await self._hass.async_add_executor_job(
                self._execute_by_name,
                sensor.path,
                request.data.get(FIELD_NAME),
                request.data.get(FIELD_SCOPE, DEFAULT_SCOPE),
                request.data.get(FIELD_VALUE),
            )

        sensor.refresh()

    @staticmethod
    def _execute_by_id(path, entry_id, value):
        now = datetime.now().strftime(DATETIME_FORMAT)
        with Database.connect(path) as connection:
            connection.execute('''
                UPDATE settings_store
                SET
                    value = CASE
                        WHEN json_valid(settings_store.value) AND json_valid(?)
                        THEN json_patch(settings_store.value, ?) ELSE ?
                    END,
                    modifiedAt = ?
                WHERE id = ?
            ''', (value, value, value, now, entry_id))

    @staticmethod
    def _execute_by_name(path, name, scope, value):
        now = datetime.now().strftime(DATETIME_FORMAT)
        with Database.connect(path) as connection:
            connection.execute('''
                INSERT INTO settings_store (name, scope, value, createdAt, modifiedAt)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT (name, scope)
                DO UPDATE SET
                    value = CASE
                        WHEN json_valid(settings_store.value) AND json_valid(excluded.value)
                        THEN json_patch(settings_store.value, excluded.value)
                        ELSE excluded.value
                    END,
                    modifiedAt = excluded.modifiedAt
            ''', (name, scope, value, now, now))
