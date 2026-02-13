"""Climate Controller.

Monitors outdoor temperature and HVAC current temperature to manage an
AC switch. Uses glob patterns to watch all temperature sensors and
attribute-change listeners on the HVAC entity.

Demo entities:
    - sensor.outside_temperature
    - climate.hvac
    - switch.ac
"""

import logging
from typing import Annotated

from pydantic_settings import SettingsConfigDict

from hassette import A, App, AppConfig, C, D, RawStateChangeEvent, states

logger = logging.getLogger(__name__)


class ClimateControllerConfig(AppConfig):
    model_config = SettingsConfigDict(env_prefix="climate_")

    temp_threshold: float = 24.0
    ac_switch: str = "switch.ac"
    climate_entity: str = "climate.hvac"
    check_interval: float = 300.0  # seconds


class ClimateController(App[ClimateControllerConfig]):
    """React to temperature changes and control an AC switch."""

    async def on_initialize(self) -> None:
        cfg = self.app_config
        self.logger.info(
            "Climate controller started — threshold=%.1f°, ac=%s",
            cfg.temp_threshold,
            cfg.ac_switch,
        )

        # Watch all temperature sensors via glob pattern
        self.bus.on_state_change(
            "sensor.*temperature*",
            changed=C.Increased(),
            handler=self.on_temp_increased,
        )

        self.bus.on_state_change(
            "sensor.*temperature*",
            changed=C.Decreased(),
            handler=self.on_temp_decreased,
        )

        # Watch HVAC current_temperature attribute
        self.bus.on_attribute_change(
            cfg.climate_entity,
            "current_temperature",
            handler=self.on_hvac_temp_change,
        )

        # Periodic climate summary
        self.scheduler.run_every(self.log_climate_summary, cfg.check_interval, name="climate_summary")

    async def on_temp_increased(
        self,
        event: RawStateChangeEvent,
        new_state: D.StateNew[states.SensorState],
        old_state: D.MaybeStateOld[states.SensorState],
        entity_id: D.EntityId,
    ) -> None:
        """An outdoor temperature sensor increased."""
        old_val = old_state.value if old_state else None
        self.logger.info("%s temperature increased: %s -> %s", entity_id, old_val, new_state.value)

        try:
            temp = float(new_state.value) if new_state.value is not None else None
        except (ValueError, TypeError):
            temp = None

        if temp is not None and temp > self.app_config.temp_threshold:
            self.logger.info("Temperature %.1f° exceeds threshold, turning on AC", temp)
            await self.api.turn_on(self.app_config.ac_switch)

    async def on_temp_decreased(
        self,
        event: RawStateChangeEvent,
        new_state: D.StateNew[states.SensorState],
        old_state: D.MaybeStateOld[states.SensorState],
        entity_id: D.EntityId,
    ) -> None:
        """An outdoor temperature sensor decreased."""
        old_val = old_state.value if old_state else None
        self.logger.info("%s temperature decreased: %s -> %s", entity_id, old_val, new_state.value)

        try:
            temp = float(new_state.value) if new_state.value is not None else None
        except (ValueError, TypeError):
            temp = None

        if temp is not None and temp <= self.app_config.temp_threshold:
            self.logger.info("Temperature %.1f° below threshold, turning off AC", temp)
            await self.api.turn_off(self.app_config.ac_switch)

    async def on_hvac_temp_change(
        self,
        event: RawStateChangeEvent,
        current_temp: Annotated[float | None, A.get_attr_new("current_temperature")],
    ) -> None:
        """HVAC current_temperature attribute changed."""
        self.logger.info("HVAC current temperature is now: %s", current_temp)

        if current_temp is not None and current_temp > self.app_config.temp_threshold:
            self.logger.info("HVAC reports %.1f° — ensuring AC is on", current_temp)
            await self.api.turn_on(self.app_config.ac_switch)

    async def log_climate_summary(self) -> None:
        """Periodic summary of climate-related entities."""
        outside = self.states.sensor.get("sensor.outside_temperature")
        hvac = self.states.climate.get(self.app_config.climate_entity)
        ac = self.states.switch.get(self.app_config.ac_switch)

        self.logger.info(
            "Climate summary — outside=%s, hvac=%s (current=%s), ac=%s",
            outside.value if outside else "unknown",
            hvac.value if hvac else "unknown",
            hvac.attributes.current_temperature if hvac else "unknown",
            ac.value if ac else "unknown",
        )
