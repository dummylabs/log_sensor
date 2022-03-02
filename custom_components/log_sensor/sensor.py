from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.core import callback
from homeassistant.components.sensor import ATTR_STATE_CLASS as STATE_CLASS
from .const import DEFAULT_NAME, DOMAIN, ICON, SENSOR
from .entity import LogSensorEntity


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices(
        [
            ErrorsLogSensor(
                coordinator=coordinator,
                entity_description=SensorEntityDescription(
                    key="log_errors",
                    name="log_errors",
                    icon="mdi:alert",
                    state_class=SensorStateClass.MEASUREMENT,
                ),
            ),
            WarningsLogSensor(
                coordinator=coordinator,
                entity_description=SensorEntityDescription(
                    key="log_warnings",
                    name="log_warnings",
                    icon="mdi:alert-outline",
                    state_class=SensorStateClass.MEASUREMENT,
                ),
            ),
        ]
    )


class ErrorsLogSensor(LogSensorEntity, SensorEntity):
    """Timestamp sensor for last watchman update time"""

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        print("native_value called")
        return self.coordinator.get_error_count()

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {"hello": "world"}

    # @callback
    # def _handle_coordinator_update(self) -> None:
    #     super()._handle_coordinator_update()

    # @property
    # def should_poll(self) -> bool:
    #     return False


class WarningsLogSensor(LogSensorEntity, SensorEntity):
    """Timestamp sensor for last watchman update time"""

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        return self.coordinator.get_warn_count()

    # @property
    # def should_poll(self) -> bool:
    #     return False