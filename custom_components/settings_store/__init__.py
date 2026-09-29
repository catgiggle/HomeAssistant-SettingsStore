from homeassistant.helpers import config_validation as cv

from .Model.StorageBuilder import StorageBuilder
from .Service.ClearService import ClearService
from .Service.DeleteService import DeleteService
from .Service.GetService import GetService
from .Service.SetService import SetService
from .constants import *

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass, _config):
    await _createRootConfig(hass)

    SetService(hass).register()
    GetService(hass).register()
    DeleteService(hass).register()
    ClearService(hass).register()

    return True


async def async_setup_entry(hass, entry):
    config = await _createEntryConfig(hass, entry)
    await StorageBuilder(hass, config[STORAGE_PATH]).async_build()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass, entry):
    if await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        await _removeEntryConfig(hass, entry)

        return True

    return False


async def async_remove_entry(hass, entry):
    storagePath = hass.config.path(f".storage/{DOMAIN}/{entry.data.get(CONFIG_INTERNAL_NAME)}.db")
    await StorageBuilder(hass, storagePath).async_remove()


async def _createRootConfig(hass):
    config = {
        SENSOR_ENTITIES: {},
    }
    hass.data.setdefault(DOMAIN, config)
    hass.data[DOMAIN].setdefault(SENSOR_ENTITIES, {})

    return config


async def _createEntryConfig(hass, entry):
    config = {
        CONFIG_DISPLAY_NAME: entry.data.get(CONFIG_DISPLAY_NAME),
        CONFIG_INTERNAL_NAME: entry.data.get(CONFIG_INTERNAL_NAME),
        STORAGE_PATH: hass.config.path(f".storage/{DOMAIN}/{entry.data.get(CONFIG_INTERNAL_NAME)}.db"),
    }
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].setdefault(SENSOR_ENTITIES, {})
    hass.data[DOMAIN][entry.entry_id] = config

    return config


async def _removeEntryConfig(hass, entry):
    hass.data[DOMAIN].pop(entry.entry_id, None)
