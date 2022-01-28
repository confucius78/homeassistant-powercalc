[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)
![hacs installs](https://img.shields.io/endpoint.svg?url=https%3A%2F%2Flauwbier.nl%2Fhacs%2Fpowercalc)
![Version](https://img.shields.io/github/v/release/bramstroker/homeassistant-powercalc)
![Downloads](https://img.shields.io/github/downloads/bramstroker/homeassistant-powercalc/total)

# Home Assistant Virtual Power Sensors
Custom component to calculate estimated power consumption of lights and other appliances.
Provides easy configuration to get virtual power consumption sensors in Home Assistant for all your devices which don't have a build in power meter.
This component estimates power usage by looking at brightness, hue/saturation and color temperature etc using different strategies. They are explained below.

![Preview](https://raw.githubusercontent.com/bramstroker/homeassistant-powercalc/master/assets/preview.gif)

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/bramski)

## TOC
- [Installation](#installation)
    - [HACS](#hacs)
    - [Manual](#manual)
- [Setup power sensors](#setup-power-sensors)
- [Configuration](#configuration)
    - [Sensor](#sensor-configuration)
    - [Global](#global-configuration)
- [Calculation modes](#calculation-modes)
    - [LUT](#lut-mode)
    - [Linear](#linear-mode)
    - [Fixed](#fixed-mode)
    - [WLED](#wled-mode)
- [Light model library](#light-model-library)
    - [LUT data files](#lut-data-files)
      - [Measuring lights](#creating-lut-files)
    - [Supported models](#supported-models)
- [Sensor naming](#sensor-naming)
- [Daily fixed energy](#faily-fixed-energy)
- [Setting up for energy dashboard](#setting-up-for-energy-dashboard)
- [Advanced features](#advanced-features)
    - [Multiple entities and grouping](#multiple-entities-and-grouping)
    - [Multiply Factor](#multiply-factor)
    - [Utility Meters](#utility-meters)
    - [Use real power sensor](#use-real-power-sensor)
- [Debug logging](#debug-logging)

## Installation

### HACS
This integration is part of the default HACS repository. Just click "Explore and add repository" to install

### Manual
Copy `custom_components/powercalc` into your Home Assistant `config` directory.

### Post installation steps
- Restart HA
- Add the following entry to `configuration.yaml`:
```yaml
powercalc:
```
- Restart HA final time

### Setup power sensors

Powercalc has a build-in library of more than 70 light models ([LUT](#lut-mode)), which have been measured and provided by users. See [supported models](docs/supported_models.md).

Starting from 0.12.0 Powercalc can automatically discover entities in your HA instance which are supported for automatic configuration.
After intallation and restarting HA power and energy sensors should appear. When this is not the case please check the logs for any errors.

When your appliance is not supported you have extensive options for manual configuration. These are explained below.

> Note: Manually configuring a entity will override an auto discovered entity

## Configuration

To manually add virtual sensors for your devices you have to add some configuration to `configuration.yaml`.
Additionally some settings can be applied on global level and will apply to all your virtual power sensors.
After changing the configuration you need to restart HA to get your power sensors to appear.

### Sensor configuration

For each entity you want to create a virtual power sensor for you'll need to add an entry in `configuration.yaml`.
Each virtual power sensor have it's own configuration possibilities.
They are as follows:

| Name                      | Type    | Requirement  | Description                                                                |
| ------------------------- | ------- | ------------ | -------------------------------------------------------------------------- |
| entity_id                 | string  | **Required** | HA entity ID. The id of the device you want your power sensor for          |
| manufacturer              | string  | **Optional** | Manufacturer, most of the time this can be automatically discovered        |
| model                     | string  | **Optional** | Model id, most of the time this can be automatically discovered            |
| standby_power             | float   | **Optional** | Supply the wattage when the device is off                                  |
| disable_standby_power     | boolean | **Optional** | Set to `true` to not show any power consumption when the device is standby |
| name                      | string  | **Optional** | Override the name                                                          |
| create_energy_sensor      | boolean | **Optional** | Set to disable/enable energy sensor creation. When set this will override global setting `create_energy_sensors` |
| create_utility_meters     | boolean | **Optional** | Set to disable/enable utility meter creation. When set this will override global setting `create_utility_meters` |
| utility_meter_types       | list    | **Optional** | Define which cycles you want to create utility meters for. See [cycle](https://www.home-assistant.io/integrations/utility_meter/#cycle). This will override global setting `utility_meter_types` |
| utility_meter_offset      | string  | **Optional** | Define the offset for utility meters. See [offset](https://www.home-assistant.io/integrations/utility_meter/#offset). |
| custom_model_directory    | string  | **Optional** | Directory for a custom light model. Relative from the `config` directory   |
| power_sensor_naming       | string  | **Optional** | Change the name (and id) of the sensors. Use the `{}` placeholder for the entity name of your appliance. When set this will override global setting `power_sensor_naming` |
| energy_sensor_naming      | string  | **Optional** | Change the name (and id) of the sensors. Use the `{}` placeholder for the entity name of your appliance. When set this will override global setting `energy_sensor_naming` |
| energy_integration_method | string  | **Optional** | Integration method for the energy sensor. See [HA docs](https://www.home-assistant.io/integrations/integration/#method) |
| mode                      | string  | **Optional** | Calculation mode, one of `lut`, `linear`, `fixed`. The default mode is `lut` |
| multiply_factor           | float   | **Optional** | Multiplies the calculated power by this number. See [multiply factor](#multiply-factor) |
| multiply_factor_standby   | boolean | **Optional** | When set to `true` the `multiply_factor` will also be applied to the standby power |
| fixed                     | object  | **Optional** | [Fixed mode options](#fixed-mode)                                          |
| linear                    | object  | **Optional** | [Linear mode options](#linear-mode)                                        |
| wled                      | object  | **Optional** | [WLED mode options](#wled-mode)                                            |
| entities                  | list    | **Optional** | Makes it possible to add multiple entities at once in one powercalc entry. Also enable possibility to create group sensors automatically. See [multiple entities and grouping](#multiple-entities-and-grouping)  |
| create_group              | string  | **Optional** | This setting is only applicable when you also use `entities` setting or `include`. Define a group name here. See [multiple entities and grouping](#multiple-entities-and-grouping) |
| include                   | object  | **Optional** | Use this in combination with `create_group` to automatically include entities from a certain area, group or template. See [Include entities](#dynamically-including-entities)
| power_sensor_id           | string  | **Optional** | Entity id of an existing power sensor. This can be used to let powercalc create energy sensors and utility meters. This will create no virtual power sensor.
| ignore_unavailable_state  | boolean | **Optional** | Set this to `true` when you want the power sensor to display a value (0 or `standby_power`) regardless of whether the source entity is available. The can be useful for example on a TV which state can become unavailable when it is set to off.

**Minimalistic example creating two power sensors:**

```yaml
sensor:
  - platform: powercalc
    entity_id: light.hallway
  - platform: powercalc
    entity_id: light.living_room
```

This will add a power sensors with the entity ids `sensor.hallway_power` and `sensor.living_room_power` to your installation.
See [Calculation modes](#calculation-modes) for all possible sensor configurations.

### Global configuration

All these settings are completely optional. You can skip this section if you don't need any advanced configuration.

| Name                      | Type    | Requirement  | Default                | Description                                                                                                                                        |
| ------------------------- | ------- | ------------ | ---------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| enable_autodiscovery      | boolean | **Optional** | true                   | Whether you want powercalc to automatically setup power sensors for supported models in your HA instance.
| scan_interval             | string  | **Optional** | 00:10:00               | Interval at which the sensor state is updated, even when the power value stays the same. Format HH:MM:SS                                           |
| create_energy_sensors     | boolean | **Optional** | true                   | Let the component automatically create energy sensors (kWh) for every power sensor                                                                 |
| power_sensor_naming       | string  | **Optional** | {} power               | Change the name of the sensors. Use the `{}` placeholder for the entity name of your appliance. This will also change the entity_id of your sensor |
| energy_sensor_naming      | string  | **Optional** | {} energy              | Change the name of the sensors. Use the `{}` placeholder for the entity name of your appliance. This will also change the entity_id of your sensor |
| create_utility_meters     | boolean | **Optional** | false                  | Set to `true` to automatically create utility meters of your energy sensors. See [utility_meters](#utility-meters) |
| utility_meter_types       | list    | **Optional** | daily, weekly, monthly | Define which cycles you want to create utility meters for. See [cycle](https://www.home-assistant.io/integrations/utility_meter/#cycle) |
| energy_integration_method | string  | **Optional** | Integration method for the energy sensor. See [HA docs](https://www.home-assistant.io/integrations/integration/#method) |

**Example:**

```yaml
powercalc:
  scan_interval: 00:01:00 #Each minute
  power_sensor_naming: "{} Powersensor"
  create_energy_sensors: false
```

## Calculation modes

To calculate estimated power consumption different modes are supported, they are as follows:
- [LUT (lookup table)](#lut-mode)
- [Linear](#linear-mode)
- [Fixed](#fixed-mode)
- [WLED](#wled-mode)

### LUT mode
Supported domain: `light`

This is the most accurate mode.
For a lot of light models measurements are taken using smart plugs. All this data is saved into CSV files. When you have the LUT mode activated the current brightness/hue/saturation of the light will be checked and closest matching line will be looked up in the CSV.
- [Supported models](#supported-models) for LUT mode
- [LUT file structure](#lut-data-files)

#### Configuration

```yaml
sensor:
  - platform: powercalc
    entity_id: light.livingroom_floorlamp
    manufacturer: signify
    model: LCT010
```

For most lights the device information in HA will supply the device and model correctly, so you can omit these.

```yaml
sensor:
  - platform: powercalc
    entity_id: light.livingroom_floorlamp
```

### Linear mode
Supported domains: `light`, `fan`

The linear mode can be used for dimmable devices which don't have a lookup table available.
You need to supply the min and max power draw yourself, by either looking at the datasheet or measuring yourself with a smart plug / power meter.
Power consumpion is calculated by ratio. So when you have your fan running at 50% speed and define watt range 2 - 6, than the estimated consumption will be 4 watt.

#### Configuration options
| Name              | Type    | Requirement  | Description                                 |
| ----------------- | ------- | ------------ | ------------------------------------------- |
| min_power         | float   | **Optional** | Power usage for lowest brightness level     |
| max_power         | float   | **Optional** | Power usage for highest brightness level    |
| calibrate         | string  | **Optional** | Calibration values                          |
| gamma_curve       | float   | **Optional** | Apply a gamma correction, for example 2.8   |

#### Example configuration

```yaml
sensor:
  - platform: powercalc
    entity_id: light.livingroom_floorlamp
    linear:
      min_power: 0.5
      max_power: 8
```

> Note: defining only `min_power` and `max_power` is only allowed for light and fan entities, when you are using another entity (for example a `sensor` or `input_number`) you must use the calibrate mode.

#### Advanced precision calibration

With the `calibrate` setting you can supply more than one power value for multiple brightness/percentage levels.
This allows for a more accurate estimation because not all lights are straight linear.

Also you can use this calibration table for other entities than lights and fans, to supply the state values and matching power values.

```yaml
sensor:
  - platform: powercalc
    entity_id: light.livingroom_floorlamp
    linear:
      calibrate:
        - 1 -> 0.3
        - 10 -> 1.25
        - 50 -> 3.50
        - 100 -> 6.8
        - 255 -> 15.3
```

> Note: For lights the supplied values must be in brightness range 1-255, when you select 1 in lovelace UI slider this is actually brightness level 3.
> For fan speeds the range is 1-100 (percentage)

Configuration with an sensor (`sensor.heater_modulation`) which supplies a percentage value (1-100):

```yaml
sensor:
  - platform: powercalc
    entity_id: sensor.heater_modulation
    name: Heater
    linear:
      calibrate:
        - 1 -> 200
        - 100 -> 1650
```

### Fixed mode
Supported domains: `light`, `fan`, `humidifier`, `switch`, `binary_sensor`, `device_tracker`, `remote`, `media_player`, `input_boolean`, `input_number`, `input_select`, `sensor`, `climate`, `vacuum`, `water_heater`

When you have an appliance which only can be set on and off you can use this mode.
You need to supply a single watt value in the configuration which will be used when the device is ON

#### Configuration options
| Name              | Type    | Requirement  | Description                                           |
| ----------------- | ------- | ------------ | ----------------------------------------------------- |
| power             | float   | **Optional** | Power usage when the appliance is turned on (in watt). Can also be a [template](https://www.home-assistant.io/docs/configuration/templating/) |
| states_power      | dict    | **Optional** | Power usage per entity state. Values can also be a [template](https://www.home-assistant.io/docs/configuration/templating/) |

#### Simple example
```yaml
sensor:
  - platform: powercalc
    entity_id: light.nondimmabled_bulb
    fixed:
      power: 20
```

#### Using a template for the power value
```yaml
sensor:
  - platform: powercalc
    entity_id: light.bathroom
    fixed:
      power: "{{states('input_number.bathroom_watts')}}"
```

#### Power per state
The `states_power` setting allows you to specify a power per entity state. This can be useful for example on Sonos devices which have a different power consumption in different states.

```yaml
sensor:
  - platform: powercalc
    entity_id: media_player.sonos_living
    fixed:
      states_power:
        playing: 8.3
        paused: 2.25
        idle: 1.5
```

You can also use state attributes. Use the `|` delimiter to seperate the attribute and value. Here is en example:

```yaml
sensor:
  - platform: powercalc
    entity_id: media_player.sonos_living
    fixed:
      power: 12
      states_power:
        media_content_id|Spotify: 5
        media_content_id|Youtube: 10
```

When no match is found in `states_power` lookup than the configured `power` will be considered.

### WLED mode
Supported domains: `light`

You can use WLED strategy for light strips which are controlled by [WLED](https://github.com/Aircoookie/WLED).
WLED calculates estimated current based on brightness levels and the microcontroller (ESP) used.
Powercalc asks to input the voltage on which the lightstrip is running and optionally a power factor. Based on these factors the wattage is calculated.

#### Configuration options
| Name              | Type    | Requirement  | Default | Description                                 |
| ----------------- | ------- | ------------ | ------- | ------------------------------------------- |
| voltage           | float   | **Required** |         | Voltage for the lightstrip                  |
| power_factor      | float   | **Optional** | 0.9     | Power factor, between 0.1 and 1.0           |

#### Example configuration

```yaml
sensor:
  - platform: powercalc
    entity_id: light.wled_lightstrip
    wled:
      voltage: 5
```

## More configuration examples

### Linear mode with additional standby power

```yaml
sensor:
  - platform: powercalc
    entity_id: light.livingroom_floorlamp
    linear:
      min_power: 0.5
      max_power: 8
    standby_power: 0.2
    name: My amazing power meter
```

<hr>

## Light model library

The component ships with predefined light measurements for some light models.
This library will keep extending by the effort of community users.

These models are located in `config/custom_components/powercalc/data` directory. 
You can also define your own models in `config/powercalc-custom-models` directory, when a manufacturer/model exists in this directory this will take precedence over the default data directory.

Each light model has it's own subdirectory `{manufacturer}/{modelid}`. i.e. signify/LCT010

### model.json

Every model MUST contain a `model.json` file which defines the supported calculation modes and other configuration.
See the [json schema](custom_components/powercalc/data/model_schema.json) how the file must be structured or the examples below.

When [LUT mode](#lut-mode) is supported also [CSV lookup files](#lut-data-files) must be provided.

Example lut mode:

```json
{
    "name": "Hue White and Color Ambiance A19 E26 (Gen 5)",
    "standby_power": 0.4,
    "supported_modes": [
        "lut"
    ],
    "measure_method": "script",
    "measure_device": "Shelly Plug S"
}
```

Example linear mode

```json
{
    "name": "Hue Go",
    "supported_modes": [
        "linear"
    ],
    "standby_power": 0.2,
    "linear_config": {
        "min_power": 0,
        "max_power": 6
    },
    "measure_method": "manual",
    "measure_device": "From manufacturer specifications"
}
```

### LUT data files

To calculate power consumption a lookup is done into CSV data files.

Depending on the supported color modes of the light the integration expects one or more CSV files here:
 - hs.csv.gz (hue/saturation, colored lamps)
 - color_temp.csv.gz (color temperature)
 - brightness.csv.gz (brightness only lights)

Some lights support two color modes (both hs and color_temp), so there must be two CSV files.

The files are gzipped to keep the repository footprint small, and installation fast but gzipping files is not mandatory.

Example:

```
- signify
  - LCT010
    - model.json
    - hs.csv.gz
    - color_temp.csv.gz
```

#### Expected file structure

- The file **MUST** contain a header row.
- The data rows in the CSV files **MUST** have the following column order:

**hs.csv**
```csv
bri,hue,sat,watt
```

**color_temp.csv**
```csv
bri,mired,watt
```

**brightness.csv**
```csv
bri,watt
```

***Ranges***:
- brightness (0-255)
- hue (0-65535)
- saturation (0-255)
- mired (0-500)  min value depending on min mired value of the light model

#### Creating LUT files

New files are created by taking measurements using a smartplug (i.e. Shelly plug) and changing the light to all kind of different variations using the Hue API or Home Assistant API.
The tooling is available at `utils/measure`.

The script supports several smartplugs with power monitoring.

See the [README](utils/measure/README.md) for more information.

### Supported models

See the [list](docs/supported_models.md) of supported lights which don't need any manual configuration

## Sensor naming

Let's assume you have a source sensor `light.patio` with name "Patio".
Powercalc will create the following sensors by default.
- sensor.patio_power (Patio power)
- sensor.patio_energy (Patio energy)

> Utility meters will use the energy name as a base and suffix with `_daily`, `_weekly`, `_monthly`

### Change suffixes
To change the default suffixes `_power` and `_energy` you can use the `power_sensor_naming` and `energy_sensor_naming` options.
The following configuration:

```yaml
powercalc:
  energy_sensor_naming: "{} kWh consumed"
```

will create:
- sensor.patio_power (Patio power)
- sensor.patio_kwh_consumed (Patio kWh consumed)

### Change name
You can also change the sensor name with the `name` option

```yaml
sensor:
  - platform: powercalc
    entity_id: light.patio
    name: Patio Light
```

will create:
- sensor.patio_light_power (Patio light power)
- sensor.patio_light_energy (Patio light energy)

## Daily fixed energy

> Available from v0.13 an higher

Sometimes you want to keep track of energy usage of individual devices which are not managed by Home Assistant.
When you know the energy consumption in kWh or W powercalc can make it possible to create an energy sensor (which can also be used in the energy dashboard). 
This can be helpful for devices which are always on and have a relatively fixed power draw. For example an IP camera, intercom, Google nest, Alexa, network switches etc.

### Configuration options

| Name                | Type    | Requirement  | Default  | Description                                           |
| ------------------- | ------- | ------------ | -------- | ------------------------------------------- |
| value               | float   | **Required** |          | Value either in watts or kWh. Can also be a [template](https://www.home-assistant.io/docs/configuration/templating/) |
| unit_of_measurement | string  | **Optional** | kWh      | `kWh` or `W` |
| on_time             | period  | **Optional** | 24:00:00 | How long the device is on per day. Only applies when unit_of_measurement is set to `W`. Format HH:MM:SS |
| update_frequency    | integer | **Optional** | 1800     | Seconds between each increase in kWh |

### Configuration examples

This will add 0.05 kWh per day to the energy sensor called "IP camera upstairs"

```yaml
sensor:
  - platform: powercalc
    name: IP camera upstairs
    daily_fixed_energy:
      value: 0.05
```

Or define in watts, with an optional on time (which is 24 hour a day by default).

```yaml
sensor:
  - platform: powercalc
    name: Intercom
    daily_fixed_energy:
      value: 21
      unit_of_measurement: W
      on_time: 12:00:00
```

This will simulate the devices using 21 watts for 12 hours a day. The energy sensor will increase by 0.252 kWh a day.

## Setting up for energy dashboard
If you want to use the virtual power sensors with the new [energy integration](https://www.home-assistant.io/blog/2021/08/04/home-energy-management/), you have to create an energy sensor which utilizes the power of the powercalc sensor. Starting from v0.4 of powercalc it will automatically create energy sensors for you by default. No need for any custom configuration. These energy sensors then can be selected in the energy dashboard. 

If you'd like to create your energy sensors by your own with e.g. [Riemann integration integration](https://www.home-assistant.io/integrations/integration/), then you can disable the automatic creation of energy sensors with the option `create_energy_sensors` in your configuration (see [global configuration](#global-configuration)).

## Advanced features

### Multiple entities and grouping

> Available from v0.8 and higher

Two new configuration parameters have been introduced `entities` and `create_group`.
`entities` will allow you to multiple power sensors in one `powercalc` sensor entry.
`create_group` will also create a group summing all the underlying entities. Which can directly be used in energy dashboard.
Each entry under `entities` can use the same configuration as when defined directly under `sensor`

```yaml
sensor:
  - platform: powercalc
    create_group: All hallway lights
    entities:
      -  entity_id: light.hallway
      -  entity_id: light.living_room
         linear:
           min_power: 0.5
           max_power: 8
```

This will create the following entities:
- sensor.hallway_power
- sensor.hallway_energy
- sensor.living_room_power
- sensor.living_room_energy
- sensor.all_hallway_lights_power (group sensor)
- sensor.all_hallway_lights_energy (group sensor)

**Nesting groups**
> Available from v0.15 and higher

You can also nest groups, this makes it possible to add an entity to multiple groups.

```yaml
sensor:
  - platform: powercalc
    create_group: All lights
    entities:
      - entity_id: light.a
      - entity_id: light.b
      - create_group: Upstairs lights
        entities:
          - entity_id: light.c
          - create_group: Bedroom Bob lights
            entities:
              - entity_id: light.d
```

Each group will have power sensors created for the following lights:
- All lights: `light.a`, `light.b`, `light.c`, `light.d`
- Upstairs lights: `light.c`, `light.d`
- Bedroom Bob lights: `light.d`

#### Dynamically including entities

Powercalc provides several methods to automatically include a bunch of entities in a group with the `include` option.
> Note: only entities will be included which are in the supported models list (these can be auto configured). You can combine `include` and `entities` to extend the group with custom configured entities.

**Include area**

> Available from v0.12 and higher

```yaml
sensor:
  - platform: powercalc
    create_group: Outdoor
    include:
      area: outdoor
```

This can also be mixed with the `entities` option, to add or override entities to the group. i.e.

```yaml
sensor:
  - platform: powercalc
    create_group: Outdoor
    include:
      area: outdoor
    entities:
      - entity_id: light.frontdoor
        fixed:
          power: 100
```

**Include group**

> Available from v0.14 and higher

Includes entities from a Home Assistant [group](https://www.home-assistant.io/integrations/group/) or [light group](https://www.home-assistant.io/integrations/light.group/)

```yaml
sensor:
  - platform: powercalc
    create_group: Livingroom lights
    include:
      group: group.livingroom_lights
```

**Include template**

> Available from v0.14 and higher

```yaml
sensor:
  - platform: powercalc
    create_group: All indoor lightd
    include:
      template: {{expand('group.all_indoor_lights')|map(attribute='entity_id')|list}}
```

### Multiply Factor

This feature allows you to multiply the calculated power.

This can be useful in the following use cases:
- You have a bunch of similar lights which you control as a group and want a single power sensor.
- You are using a LED strip from the LUT models, but you have extended or shortened it.

Let's assume you have a combination of 4 GU10 spots in your ceiling in a light group `light.livingroom_spots`

```yaml
- platform: powercalc
  entity_id: light.livingroom_spots
  multiply_factor: 4
```

This will add the power sensor `sensor.livingroom_spots_power` and the measured power will be multiplied by 4, as the original measurements are for 1 spot.

By default the multiply factor will **NOT** be applied to the standby power, you can set the `multiply_factor_standby` to do this.

```yaml
- platform: powercalc
  entity_id: light.livingroom_spots
  multiply_factor: 4
  multiply_factor_standby: true
```

> Note: a multiply_factor lower than 1 will decrease the power. For example 0.5 will half the power.

### Utility meters

The energy sensors created by the component will keep increasing the total kWh, and never reset.
When you want to know the energy consumed the last 24 hours, or last month you can use the [utility_meter](https://www.home-assistant.io/integrations/utility_meter/) component of Home Assistant. Powercalc allows you to automatically create utility meters for all your powercalc sensors with a single line of configuration.

```yaml
powercalc:
  create_utility_meters: true
```

By default utility meters are created for `daily`, `weekly`, `monthly` cycles.
You can change this behaviour with the `utility_meter_types` configuration option.

```yaml
powercalc:
  create_utility_meters: true
  utility_meter_types:
    - daily
    - yearly
```

The utility meters have the same name as your energy sensor, but are extended by the meter cycle.
Assume you have a light `light.floorlamp_livingroom`, than you should have the following sensors created:
- `sensor.floorlamp_livingroom_power`
- `sensor.floorlamp_livingroom_energy`
- `sensor.floorlamp_livingroom_energy_daily`
- `sensor.floorlamp_livingroom_energy_weekly`
- `sensor.floorlamp_livingroom_energy_monthly`

### Use real power sensor

> Available from v0.14 and higher

Use the following configuration to use an existing power sensor and let powercalc create the energy sensors and utility meters for it:

```yaml
- platform: powercalc
  entity_id: light.toilet
  power_sensor_id: sensor.toilet_light_power
```

## Debug logging

Add the following to configuration.yaml:

```yaml
logger:
  default: warning
  logs:
    custom_components.powercalc: debug
```
