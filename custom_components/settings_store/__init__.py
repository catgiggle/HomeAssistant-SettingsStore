from homeassistant.helpers import config_validation as cv

from .Service.ClearService import ClearService
from .Service.DeleteService import DeleteService
from .Service.GetService import GetService
from .Service.SetService import SetService
from .Setup.StorageBuilder import StorageBuilder
from .constants import *

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass, _config):
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].setdefault(SENSOR_ENTITIES, {})

    SetService(hass).register()
    GetService(hass).register()
    DeleteService(hass).register()
    ClearService(hass).register()

    return True


async def async_setup_entry(hass, entry):
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].setdefault(SENSOR_ENTITIES, {})
    hass.data[DOMAIN][entry.entry_id] = {
        CONFIG_NAME: entry.data.get(CONFIG_NAME),
        CONFIG_LABEL: entry.data.get(CONFIG_LABEL),
        STORAGE_PATH: hass.config.path(f".storage/{DOMAIN}/{entry.data.get(CONFIG_NAME)}.db"),
    }

    StorageBuilder(hass.data[DOMAIN][entry.entry_id][STORAGE_PATH]).build()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass, entry):
    await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    hass.data[DOMAIN].pop(entry.entry_id, None)

    return True


async def async_remove_entry(hass, entry):
    await hass.async_add_executor_job(
        StorageBuilder(hass.config.path(f".storage/{DOMAIN}/{entry.data[CONFIG_NAME]}.db")).remove)
