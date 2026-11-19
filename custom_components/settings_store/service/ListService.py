import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from ..constants import *
from ..utils.Database import Database


class ListService:
    def __init__(self, hass):
        self._hass = hass

    def register(self):
        self._hass.services.async_register(
            DOMAIN,
            'list',
            self.handle,
            schema=vol.Schema({
                vol.Required(FIELD_STORE): cv.entity_id,
                vol.Optional(FIELD_SCOPE): cv.string,
            }),
            supports_response=True
        )

    async def handle(self, request):
        sensor = self._hass.data[DOMAIN][SENSOR_ENTITIES][request.data[FIELD_STORE]]

        if request.data.get(FIELD_SCOPE) == '*':
            result = await self._hass.async_add_executor_job(
                self._execute_list_all,
                sensor.path,
            )
        else:
            result = await self._hass.async_add_executor_job(
                self._execute_list_scope,
                sensor.path,
                request.data.get(FIELD_SCOPE, DEFAULT_SCOPE),
            )

        return {
            FIELD_LIST: [
                {
                    FIELD_ID: row[0],
                    FIELD_NAME: row[1],
                    FIELD_SCOPE: row[2],
                    FIELD_VALUE: row[3],
                    FIELD_CREATED_AT: row[4],
                    FIELD_MODIFIED_AT: row[5],
                }
                for row in result
            ]
        }

    @staticmethod
    def _execute_list_all(path):
        with Database.connect(path) as connection:
            return connection.execute('''
                SELECT id, name, scope, value, createdAt, modifiedAt
                FROM settings_store
                ORDER BY scope ASC, name ASC
            ''').fetchall()

    @staticmethod
    def _execute_list_scope(path, scope):
        with Database.connect(path) as connection:
            return connection.execute('''
                SELECT id, name, scope, value, createdAt, modifiedAt
                FROM settings_store
                WHERE scope = ?
                ORDER BY name ASC
            ''', (scope,)).fetchall()
