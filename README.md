# hassette-examples

Example apps for the [Hassette](https://github.com/NodeJSmith/hassette) Home Assistant automation framework. These apps run against the built-in [Home Assistant demo integration](https://www.home-assistant.io/integrations/demo/) so you can try them without any real hardware.

This repository doubles as a **project template** — fork it and replace the example apps with your own.

## Quick Start

### 1. Clone and configure

```bash
git clone https://github.com/NodeJSmith/hassette-examples.git
cd hassette-examples
cp .env.example .env
```

### 2. Start Home Assistant

Hassette cannot run without a long lived access token to authenticate with Home Assistant, so we need to start just the Home Assistant container first:

```bash
docker compose up homeassistant -d
```

### 3. Complete Home Assistant onboarding

Open [http://localhost:8123](http://localhost:8123) and follow the [onboarding steps](https://www.home-assistant.io/getting-started/onboarding/) to create your user account. The demo integration is already enabled via `config/ha/configuration.yaml`, so demo entities will appear automatically after setup.

### 4. Create an access token

Once onboarding is complete, go to your profile page at [http://localhost:8123/profile/security](http://localhost:8123/profile/security) and create a **Long-Lived Access Token**. Copy the token and add it to your `.env` file:

```bash
HASSETTE__TOKEN=your_long_lived_access_token
```

### 5. Start Hassette

Now bring up the full stack:

```bash
docker compose up -d
```

Hassette will connect to Home Assistant and load all 5 example apps (7 instances). You can view the Hassette dashboard at [http://localhost:8126](http://localhost:8126) and check the logs with `docker compose logs hassette -f`.

## Apps

### 1. Motion Lights (`motion_lights.py`)

Turns lights on when motion is detected and off after motion clears.

**Patterns:** AppConfig, multi-instance, `on_state_change` with `changed_to`, dependency injection (`D.StateNew`), entity objects (`LightEntity`), `debounce`

**Entities:** `binary_sensor.movement_backyard`, `light.kitchen_lights`, `light.ceiling_lights`

**Multi-instance:** Two instances configured in `hassette.toml` — `backyard_kitchen` and `backyard_ceiling` — same motion sensor controlling different lights with different brightness levels.

### 2. Climate Controller (`climate_controller.py`)

Monitors outdoor and HVAC temperatures to manage an AC switch.

**Patterns:** Glob patterns (`sensor.*temperature*`), conditions (`C.Increased()`, `C.Decreased()`), `on_attribute_change`, accessors (`A.get_attr_new`), `run_every` scheduler, dependency injection

**Entities:** `sensor.outside_temperature`, `climate.hvac`, `switch.ac`

### 3. Cover Scheduler (`cover_scheduler.py`)

Automates covers/blinds on a daily schedule — opens on weekday mornings, closes at night.

**Patterns:** `run_cron`, `run_daily`, `run_hourly`, `run_in`, `once=True`, cache persistence, state iteration (`for entity_id, cover in self.states.cover`), lifecycle hooks (`on_shutdown`)

**Entities:** `cover.kitchen_window`, `cover.hall_window`, `cover.living_room_window`, `sun.sun`

### 4. Presence Tracker (`presence_tracker.py`)

Tracks a person's location and dynamically subscribes to zone changes when they leave home.

**Patterns:** Multi-instance, dynamic subscription management (`.cancel()`), conditions (`C.Increased()`), `set_state` to create custom sensors, `run_every` scheduler

**Entities:** `device_tracker.demo_paulus`, `device_tracker.demo_home_boy`, `zone.home`

### 5. Security Monitor (`security_monitor.py`)

Monitors lock service calls and moisture sensor alerts using synchronous patterns.

**Patterns:** `AppSync` with `on_initialize_sync`, `on_call_service`, `throttle`, sync state iteration

**Entities:** `lock.front_door`, `lock.kitchen_door`, `binary_sensor.basement_floor_wet`

## Pattern Coverage

| Pattern                  | App 1 | App 2 | App 3 | App 4 | App 5 |
| ------------------------ | :---: | :---: | :---: | :---: | :---: |
| AppConfig                |   x   |   x   |   x   |   x   |   x   |
| Multi-instance           |   x   |       |       |   x   |       |
| on_state_change          |   x   |   x   |   x   |   x   |   x   |
| on_attribute_change      |       |   x   |       |       |       |
| on_call_service          |       |       |       |       |   x   |
| Glob patterns            |       |   x   |       |       |       |
| changed_to/from          |   x   |       |       |       |   x   |
| Conditions (C)           |       |   x   |       |   x   |       |
| Dependency injection (D) |   x   |   x   |       |   x   |       |
| Accessors (A)            |       |   x   |       |       |       |
| Scheduler (various)      |       |   x   |   x   |   x   |       |
| State domain access      |   x   |       |   x   |   x   |   x   |
| API calls                |   x   |   x   |   x   |   x   |       |
| debounce/throttle        |   x   |       |       |       |   x   |
| once=True                |       |       |   x   |       |       |
| AppSync                  |       |       |       |       |   x   |
| Cache                    |       |       |   x   |       |       |
| Entity objects           |   x   |       |       |       |       |
| Dynamic subscriptions    |       |       |       |   x   |       |

## Project Structure

```
hassette-examples/
├── .env.example
├── README.md
├── pyproject.toml
├── docker-compose.yml
├── config/
│   ├── hassette.toml                # App configuration
│   └── ha/
│       └── configuration.yaml       # HA config with demo: enabled
└── src/
    └── hassette_examples/
        ├── __init__.py
        ├── motion_lights.py         # App 1: Motion-Activated Lights
        ├── climate_controller.py    # App 2: Climate Controller
        ├── cover_scheduler.py       # App 3: Cover/Blind Scheduler
        ├── presence_tracker.py      # App 4: Presence Tracker
        └── security_monitor.py      # App 5: Security Monitor (AppSync)
```

## Configuration

All app configuration lives in `config/hassette.toml`. See the [Hassette documentation](https://hassette.readthedocs.io/) for the full configuration reference.

Environment variables in `.env` override TOML values:

```bash
HA_TOKEN=your_long_lived_access_token
```

## License

MIT
