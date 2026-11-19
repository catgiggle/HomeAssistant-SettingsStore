import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from ..constants import *
from ..utils.Database import Database


class RemoveService:
    def __init__(self, hass):
        self._hass = hass

    def register(self):
        self._hass.services.async_register(
            DOMAIN,
            'remove',
            self.handle,
            schema=vol.Schema({
                vol.Required(FIELD_ENTITY_ID): cv.entity_id,
                vol.Required(FIELD_ID): vol.All(vol.Coerce(int), vol.Range(min=1)),
            })
        )

    async def handle(self, request):
        sensor = self._hass.data[DOMAIN][SENSOR_ENTITIES][request.data[FIELD_ENTITY_ID]]

        await self._hass.async_add_executor_job(
            self._execute,
            sensor.path,
            request.data[FIELD_ID],
        )
        sensor.refresh()

    @staticmethod
    def _execute(path, id):
        with Database.connect(path) as connection:
            connection.execute('''
                DELETE FROM settings_store
                WHERE id = ?
            ''', (id,))
