import re

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.util import slugify

from .constants import *


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        formData = user_input or {}
        formErrors = {}

        fieldLabelValue = formData.get(CONFIG_LABEL, '').strip()
        fieldNameValue = formData.get(CONFIG_NAME, '').strip()

        normalizedName = None

        if user_input is not None:
            if not re.search(r'[a-zA-Z]', fieldLabelValue):
                formErrors[CONFIG_LABEL] = 'invalid_label'

            if fieldNameValue:
                if fieldNameValue == slugify(fieldNameValue):
                    normalizedName = fieldNameValue
                else:
                    formErrors[CONFIG_NAME] = 'invalid_name'
            else:
                normalizedName = slugify(fieldLabelValue)

            if not formErrors:
                await self.async_set_unique_id(normalizedName)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(title=fieldLabelValue, data={
                    CONFIG_LABEL: fieldLabelValue,
                    CONFIG_NAME: normalizedName,
                })

        return self.async_show_form(
            step_id='user',
            data_schema=vol.Schema({
                vol.Required(CONFIG_LABEL, default=fieldLabelValue): cv.string,
                vol.Optional(CONFIG_NAME, default=fieldNameValue): cv.string,
            }),
            errors=formErrors
        )
