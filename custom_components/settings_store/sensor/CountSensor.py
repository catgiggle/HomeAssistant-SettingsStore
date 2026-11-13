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
        self._custom_attributes = {}

        self._update_data()

    @property
    def path(self):
        return self._storagePath

    @property
    def extra_state_attributes(self):
        return self._custom_attributes

    def refresh(self):
        self._update_data()
        self.async_write_ha_state()

    async def async_added_to_hass(self):
        self._hass.data[DOMAIN][SENSOR_ENTITIES][self.entity_id] = self

    async def async_will_remove_from_hass(self):
        self._hass.data[DOMAIN][SENSOR_ENTITIES].pop(self.entity_id, None)

    def _update_data(self):
        with Database.connect(self._storagePath) as connection:
            stateResult = connection.execute('''
                SELECT COUNT(*), MIN(createdAt), MAX(modifiedAt)
                FROM settings_store
            ''').fetchone()

            scopesResult = connection.execute('''
                SELECT scope, MIN(createdAt), MAX(modifiedAt)
                FROM settings_store
                GROUP BY scope
            ''').fetchall()

        self._attr_native_value = stateResult[0] if stateResult else None
        self._custom_attributes = {
            'store_created_at': stateResult[1] if stateResult else None,
            'store_modified_at': stateResult[2] if stateResult else None,
            **{
                f"{row[0].replace('.', '_').replace(' ', '_')}_created_at": row[1]
                for row in scopesResult
            },
            **{
                f"{row[0].replace('.', '_').replace(' ', '_')}_modified_at": row[2]
                for row in scopesResult
            }
        }
