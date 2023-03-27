# -*- coding: utf-8 -*-

logger.info("process_nrfcloud started")
logger.warn("process_nrfcloud data %s", data)

payload = data.get("data")

logger.warn("process_nrfcloud payload %s", payload)

if payload["appId"] == "TEMP":
    logger.warn("process_nrfcloud sensor.thingy_temperature=%s", payload["data"])
    hass.states.set('sensor.thingy_temperature', payload["data"], {
        'unit_of_measurement': '°C',
        'device_class': 'temperature',
        'friendly_name': 'Thingy 91 - Temperatura',
        'icon': 'mdi:thermometer',
    })

if payload["appId"] == "HUMID":
    logger.warn("process_nrfcloud sensor.thingy_humidity=%s", payload["data"])
    hass.states.set('sensor.thingy_humidity', payload["data"], {
        'unit_of_measurement': '%',
        'device_class': 'humidity',
        'friendly_name': 'Thingy 91 - Wilgotność',
        'icon': 'mdi:water-percent',
    })

if payload["appId"] == "AIR_PRESS":
    logger.warn("process_nrfcloud sensor.thingy_pressure=%s", payload["data"])
    hass.states.set('sensor.thingy_pressure', round(float(payload["data"]) * 10, 2), {
        'unit_of_measurement': 'hPa',
        'device_class': 'preasure',
        'friendly_name': 'Thingy 91 - Ciśnienie',
        'icon': 'mdi:gauge',
    })

if payload["appId"] == "AIR_QUAL":
    logger.warn("process_nrfcloud sensor.thingy_iaq=%s", payload["data"])
    hass.states.set('sensor.thingy_iaq', payload["data"], {
        'unit_of_measurement': 'IAQ',
        'device_class': 'gas',
        'friendly_name': 'Thingy 91 - IAQ',
        'icon': 'mdi:air-filter',
    })

if payload["appId"] == "VOLTAGE":
    battery = int((float(payload["data"])/1000 - 3.6) * 10000/56)
    if battery > 100:
        battery = 100
    if battery < 0:
        battery = 0

    logger.warn("process_nrfcloud sensor.thingy_battery=%d", battery)
    hass.states.set('sensor.thingy_battery', battery, {
        'unit_of_measurement': '%',
        'device_class': 'battery',
        'friendly_name': 'Thingy 91 - Bateria',
        'icon': 'mdi:battery-50',
    })

logger.info("process_nrfcloud data set")
