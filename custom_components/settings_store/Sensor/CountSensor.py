import sqlite3

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import EntityCategory

from ..constants import *


class CountSensor(SensorEntity):
    def __init__(self, hass, configName, storagePath, deviceInfo):
        self._hass = hass
        self._storagePath = storagePath

        self._attr_name = 'Entries'
        self._attr_unique_id = f"{DOMAIN}_{configName}_entries"
        self._attr_suggested_object_id = self._attr_unique_id
        self._attr_device_info = deviceInfo
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def path(self):
        return self._storagePath

    @property
    def native_value(self):
        with sqlite3.connect(self._storagePath) as connection:
            result = connection.execute('''
                SELECT COUNT(*)
                FROM settings_store
            ''').fetchone()

            return result[0]

    def refresh(self):
        self.async_write_ha_state()

    async def async_added_to_hass(self):
        self._hass.data[DOMAIN][SENSOR_ENTITIES][self.entity_id] = self

    async def async_will_remove_from_hass(self):
        self._hass.data[DOMAIN][SENSOR_ENTITIES].pop(self.entity_id, None)
