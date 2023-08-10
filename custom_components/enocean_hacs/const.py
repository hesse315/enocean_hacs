"""Constants for the ENOcean integration."""
import logging

from homeassistant.const import Platform

DOMAIN = "enocean_hacs"
DATA_ENOCEAN = "enocean"
ENOCEAN_DONGLE = "dongle"

ERROR_INVALID_DONGLE_PATH = "invalid_dongle_path"

SIGNAL_RECEIVE_MESSAGE = "enocean_hacs.receive_message"
SIGNAL_SEND_MESSAGE = "enocean_hacs.send_message"

CONF_EEP = 'eep'
CONF_MANUFACTURER = 'manufacturer'
CONF_DEVICE_TYPE = 'type'
DEFAULT_MANUFACTURER = 'enocean'


LOGGER = logging.getLogger(__package__)

PLATFORMS = [
    Platform.SENSOR,
]
