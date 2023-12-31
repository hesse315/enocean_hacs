"""Config flows for the ENOcean integration."""

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant import config_entries
from homeassistant.const import CONF_DEVICE, CONF_PATH

from .const import DOMAIN, ERROR_INVALID_DONGLE_PATH, LOGGER
from . import dongle


class VolEnoceanId():
    """"voluptuos check if eid is between 0x00000001 and 0xFFFFFFFF"""

    def __call__(self, enoid):
        try:
            enoid = f"{int(enoid,16):08x}"
            if not 0x0 < enoid <= 0xffffffff:
                raise vol.Invalid('enocean id has to be in range 0x00000001 and 0xFFFFFFFF')
        except ValueError as err:
            raise vol.Invalid('expected id as 4 byte hex') from err

        return enoid

    def __repr__(self):
        return 'EnocenId()'



DONGLE_SCHEMA = vol.Schema(
    {vol.Required(CONF_PATH): cv.string}
)

DEVICE_SCHEMA = vol.Schema(
    {
        vol.Required("enoid"): VolEnoceanId(),
        "manufacturer": cv.string,
        "model": cv.string,
        "eep":  cv.string,
        "eep_tx": [],
    }
)


class EnOceanHacsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the EnOcean HACS config flows."""

    VERSION = 1
    MANUAL_PATH_VALUE = "Custom path"

    async def async_step_user(self, user_input=None):
        """Handle an EnOcean config flow start."""
        LOGGER.debug('config flow: start step user')

        LOGGER.debug('config flow: start step user')
        LOGGER.debug(str(self._async_current_entries()))

        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        return await self.async_step_detect()

    async def async_step_detect(self, user_input=None):
        """Propose a list of detected dongles.
        first step in integration configuration
        """
        LOGGER.debug('config flow: detetc')
        errors = {}
        if user_input is not None:
            if user_input[CONF_DEVICE] == self.MANUAL_PATH_VALUE:
                return await self.async_step_manual(None)
            if await self.validate_enocean_conf(user_input):
                return self.create_enocean_entry(user_input)
            errors = {CONF_DEVICE: ERROR_INVALID_DONGLE_PATH}

        # fill list with serial devices
        bridges = await self.hass.async_add_executor_job(dongle.detect)
        if len(bridges) == 0:
            return await self.async_step_manual(user_input)
        bridges.append(self.MANUAL_PATH_VALUE)

        # ask user
        return self.async_show_form(
            step_id="detect",
            data_schema=vol.Schema({vol.Required(CONF_DEVICE): vol.In(bridges)}),
            errors=errors,
        )

    async def async_step_manual(self, user_input=None):
        """Request manual USB dongle path."""
        default_value = None
        errors = {}
        if user_input is not None:
            if await self.validate_enocean_conf(user_input):
                return self.create_enocean_entry(user_input)
            default_value = user_input[CONF_DEVICE]
            errors = {CONF_DEVICE: ERROR_INVALID_DONGLE_PATH}

        return self.async_show_form(
            step_id="manual",
            data_schema=vol.Schema(
                {vol.Required(CONF_DEVICE, default=default_value): str}
            ),
            errors=errors,
        )

    async def validate_enocean_conf(self, user_input) -> bool:
        """Return True if the user_input contains a valid dongle path."""
        dongle_path = user_input[CONF_DEVICE]
        path_is_valid = await self.hass.async_add_executor_job(
            dongle.validate_path, dongle_path
        )
        return path_is_valid

    def create_enocean_entry(self, user_input):
        """Create an entry for the provided configuration."""
        return self.async_create_entry(title="EnOcean HACS", data=user_input)
