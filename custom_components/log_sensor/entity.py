"""Log_sensor entity"""
from ensurepip import version
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo, EntityDescription

from custom_components.log_sensor import coordinator
from .coordinator import LogSensorDataUpdateCoordinator

from .const import DOMAIN, NAME, VERSION, ATTRIBUTION

HOME_ASSISTANT = "Home Assistant"


class LogSensorEntity(CoordinatorEntity):
    """a base class for log_sensor """

    @property
    def device_info(self):
        """group sensors under one device(service)"""
        return {
            "identifiers": {(DOMAIN, "log_sensor_unique_id")},
            "name": NAME,
            "model": VERSION,
            "manufacturer": NAME,
            "entry_type": DeviceEntryType.SERVICE,
        }

    def __init__(
        self,
        coordinator: LogSensorDataUpdateCoordinator,
        entity_description: EntityDescription,
    ) -> None:
        """Initialize version entities."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        # per sensor unique_id
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_{entity_description.key}"
        )
        self._attr_unit_of_measurement = "entries"
