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
                vol.Required(FIELD_ENTITY_ID): cv.entity_id,
                vol.Optional(FIELD_SCOPE, default=DEFAULT_SCOPE): cv.string,
            }),
            supports_response=True
        )

    async def handle(self, request):
        sensor = self._hass.data[DOMAIN][SENSOR_ENTITIES][request.data[FIELD_ENTITY_ID]]

        result = await self._hass.async_add_executor_job(
            self._execute,
            sensor.path,
            request.data[FIELD_SCOPE],
        )

        return {
            FIELD_LIST: [
                {
                    FIELD_NAME: row[0],
                    FIELD_VALUE: row[1],
                    FIELD_CREATED_AT: row[2],
                    FIELD_MODIFIED_AT: row[3],
                }
                for row in result
            ]
        }

    @staticmethod
    def _execute(path, scope):
        with Database.connect(path) as connection:
            return connection.execute('''
                SELECT name, value, createdAt, modifiedAt
                FROM settings_store
                WHERE scope = ?
                ORDER BY name ASC
            ''', (scope,)).fetchall()
