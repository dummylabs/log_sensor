from math import ceil
import logging
from datetime import datetime, timedelta
from homeassistant.core import Config, HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class LogSensorDataUpdateCoordinator(DataUpdateCoordinator):
    """simple circular buffer to count errors and warnings"""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize."""
        self.platforms = []
        super().__init__(
            hass, _LOGGER, name=DOMAIN, update_interval=timedelta(seconds=30)
        )
        self.group_by = 1  # 15
        buf_size = range(ceil(60 / self.group_by))
        self.error_buffer = [0 for i in buf_size]
        self.warn_buffer = [0 for i in buf_size]
        self.deep = 4
        assert self.deep <= len(self.error_buffer)
        self.last_error_slot = None
        self.last_warn_slot = None

    def add_error(self, dt):
        print("added error")
        head = self._get_head(dt)
        if self.last_error_slot is not None:
            if head != self.last_error_slot:
                self.error_buffer[head] = 0
        self.last_error_slot = head
        self.error_buffer[head] += 1
        _LOGGER.debug(f"Head: {head}")
        _LOGGER.debug(f"Buffer: {self.error_buffer}")

    def add_warn(self, dt):
        print("added warning")
        head = self._get_head(dt)
        if self.last_warn_slot is not None:
            if head != self.last_warn_slot:
                self.warn_buffer[head] = 0
        self.last_warn_slot = head
        self.warn_buffer[head] += 1

    def get_error_count(self):
        dt = datetime.now()
        return self._get_count(self.error_buffer, dt)

    def get_warn_count(self):
        dt = datetime.now()
        return self._get_count(self.warn_buffer, dt)

    def _get_head(self, dt):
        return (ceil(dt.minute / self.group_by) or 1) - 1

    def _get_count(self, buffer, dt):
        head = self._get_head(dt)
        total = buffer[head]
        for _ in range(self.deep):
            head = head - 1 if head > 0 else len(buffer) - 1
            total += buffer[head]
        return total

    async def _async_update_data(self) -> None:
        print("async_update_data CALLED")
        return