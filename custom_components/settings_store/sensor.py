from homeassistant.helpers.device_registry import DeviceInfo

from .Sensor.CountSensor import CountSensor
from .constants import *


async def async_setup_entry(hass, entry, async_add_entities):
    entryConfig = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([
        CountSensor(
            hass,
            entryConfig[CONFIG_NAME],
            entryConfig[STORAGE_PATH],
            DeviceInfo(
                identifiers={(DOMAIN, entry.entry_id)},
                model=NAME,
                serial_number=entryConfig[CONFIG_NAME],
                manufacturer=AUTHOR,
                sw_version=VERSION,
            )
        )
    ], True)
