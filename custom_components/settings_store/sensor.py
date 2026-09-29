from homeassistant.helpers.device_registry import DeviceInfo

from .Sensor.CountSensor import CountSensor
from .constants import *


async def async_setup_entry(hass, entry, async_add_entities):
    config = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([
        CountSensor(
            hass,
            config[CONFIG_INTERNAL_NAME],
            config[STORAGE_PATH],
            DeviceInfo(
                identifiers={(DOMAIN, entry.entry_id)},
                name=config[CONFIG_DISPLAY_NAME],
                model=NAME,
                serial_number=config[CONFIG_INTERNAL_NAME],
                manufacturer=AUTHOR,
                sw_version=VERSION,
            )
        )
    ], True)
