"""https://github.com/dummylabs/thewatchman§"""
import asyncio
from datetime import datetime, timedelta
import logging

import queue

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Config, HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.typing import HomeAssistantType


from .const import DOMAIN, PLATFORMS, STARTUP_MESSAGE
from .coordinator import LogSensorDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: Config):
    """Set up this integration using YAML is not supported."""
    return True


async def async_setup_entry(hass: HomeAssistantType, entry: ConfigEntry):
    """Set up this integration using UI"""

    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN] = {"error_count": 0, "warning_count": 0}
        _LOGGER.info(STARTUP_MESSAGE)

    coordinator = LogSensorDataUpdateCoordinator(hass)
    coordinator.async_set_updated_data(data={"errors": "unknown"})

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    hass.data[DOMAIN][entry.entry_id] = coordinator
    hass.data[DOMAIN]["coordinator"] = coordinator

    for platform in PLATFORMS:
        if entry.options.get(platform, True):
            coordinator.platforms.append(platform)
            hass.async_add_job(
                hass.config_entries.async_forward_entry_setup(entry, platform)
            )

    entry.async_on_unload(entry.add_update_listener(update_listener))

    # error_handler = LogErrorHandler(hass)
    # error_handler.setLevel(logging.WARN)
    # logging.root.addHandler(error_handler)
    # hass.data[DOMAIN]["error_handler"] = error_handler

    simple_queue: queue.SimpleQueue = queue.SimpleQueue()
    queue_handler = LogErrorQueueHandler(simple_queue)
    queue_handler.setLevel(logging.WARN)
    logging.root.addHandler(queue_handler)

    handler = LogErrorHandler(hass)

    hass.data[DOMAIN]["error_handler"] = handler
    hass.data[DOMAIN]["queue_handler"] = queue_handler

    listener = logging.handlers.QueueListener(
        simple_queue, handler, respect_handler_level=True
    )

    listener.start()
    hass.data[DOMAIN]["listener"] = listener

    return True


class LogErrorQueueHandler(logging.handlers.QueueHandler):
    """Process the log in another thread."""

    def emit(self, record):
        """Emit a log record."""
        try:
            self.enqueue(record)
        except Exception:  # pylint: disable=broad-except
            self.handleError(record)


async def update_listener(hass: HomeAssistant, entry: ConfigEntry):
    """Reload integration when options changed"""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(
    hass: HomeAssistant, config_entry
):  # pylint: disable=unused-argument
    """Handle integration unload"""
    queue_handler = hass.data[DOMAIN].get("queue_handler", None)
    if queue_handler:
        logging.root.removeHandler(queue_handler)
        listener = hass.data[DOMAIN].get("listener", None)
        listener.stop()

    handler = hass.data[DOMAIN].get("error_handler", None)
    if handler:
        logging.getLogger().removeHandler(handler)

    del hass.data[DOMAIN]
    return True


class LogErrorHandler(logging.Handler):
    """Log handler for error messages."""

    def __init__(self, hass):
        """Initialize a new LogErrorHandler."""
        super().__init__()
        self.hass = hass

    async def update(self):
        coord = self.hass.data[DOMAIN]["coordinator"]
        return coord.async_set_updated_data(data={"errors": 66})

    def emit(self, record):
        """Save error and warning logs."""
        if record.levelname == "WARNING":
            # self.hass.data[DOMAIN]["warning_count"] += 1
            print("WARNING")
            dt = datetime.now()
            self.hass.data[DOMAIN]["coordinator"].add_warn(dt)

        elif record.levelname == "ERROR":
            print("ERROR")
            # self.hass.data[DOMAIN]["error_count"] += 1
            dt = datetime.now()
            self.hass.data[DOMAIN]["coordinator"].add_error(dt)

        if record.levelname in ["ERROR", "WARNING"]:
            coord = self.hass.data[DOMAIN]["coordinator"]
            # coord.async_set_updated_data(data={"errors": 66})

            asyncio.run_coroutine_threadsafe(
                async_update_state(self.hass),
                self.hass.loop,
            ).result()


async def async_update_state(hass):
    coord = hass.data[DOMAIN]["coordinator"]
    coord.async_set_updated_data(data={"errors": 66})
    return None
