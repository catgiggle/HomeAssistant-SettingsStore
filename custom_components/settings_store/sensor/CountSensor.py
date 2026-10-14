from datetime import datetime

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import EntityCategory

from ..constants import *
from ..utils.Database import Database


class CountSensor(SensorEntity):
    _attr_has_entity_name = True
    _attr_name = 'Entries'

    def __init__(self, hass, configName, storagePath, deviceInfo):
        self._hass = hass
        self._storagePath = storagePath

        self._attr_unique_id = f"{DOMAIN}_{configName}_entries"
        self._attr_suggested_object_id = self._attr_unique_id
        self._attr_device_info = deviceInfo
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

        self._attr_native_value = 0
        self._latest_store_changed_at = None
        self._latest_entry_created_at = None
        self._latest_entry_modified_at = None

        self._update_data()

    @property
    def path(self):
        return self._storagePath

    @property
    def extra_state_attributes(self):
        return {
            'latest_store_changed_at': self._latest_store_changed_at,
            'latest_entry_created_at': self._latest_entry_created_at,
            'latest_entry_modified_at': self._latest_entry_modified_at,
        }

    def refresh(self):
        self._update_data()
        self.async_write_ha_state()

    async def async_added_to_hass(self):
        self._hass.data[DOMAIN][SENSOR_ENTITIES][self.entity_id] = self

    async def async_will_remove_from_hass(self):
        self._hass.data[DOMAIN][SENSOR_ENTITIES].pop(self.entity_id, None)

    def _update_data(self):
        with Database.connect(self._storagePath) as connection:
            result = connection.execute('''
                SELECT COUNT(*), MAX(createdAt), MAX(modifiedAt)
                FROM settings_store
            ''').fetchone()

        if result:
            self._attr_native_value = result[0]
            self._latest_store_changed_at = datetime.now().strftime(DATETIME_FORMAT)
            self._latest_entry_created_at = result[1]
            self._latest_entry_modified_at = result[2]
