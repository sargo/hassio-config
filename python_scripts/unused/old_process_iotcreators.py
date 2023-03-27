# -*- coding: utf-8 -*-

logger.info("process_iotcreators started")

encoded_paylod = data.get("data")

logger.info("process_iotcreators encoded data %s", encoded_paylod)


def unhexlify(hexstr):
    """Return the binary data represented by hexstr.
    :param str|ReadableBuffer hexstr: Hexadecimal string.
    """

    if len(hexstr) % 2 != 0:
        raise Error("Odd-length string")

    return bytes([int(hexstr[i : i + 2], 16) for i in range(0, len(hexstr), 2)])


decoded_paylod = unhexlify(encoded_paylod).decode('ascii')

logger.warn("process_iotcreators decoded data %s", decoded_paylod)


def load_json(text):
    result = {}
    for i in text.strip("{}").split(","):
        key, value = i.split(":")
        result[key.strip('"')] = float(value)
    return result

payload = load_json(decoded_paylod)

logger.info("process_iotcreators data %s", payload)


hass.states.set('sensor.thingy_temperature', payload["Temp"], {
    'unit_of_measurement': '°C',
    'device_class': 'temperature',
    'friendly_name': 'Thingy 91 - Temperatura',
    'icon': 'mdi:thermometer',
})
hass.states.set('sensor.thingy_humidity', payload["Humid"], {
    'unit_of_measurement': '%',
    'device_class': 'humidity',
    'friendly_name': 'Thingy 91 - Wilgotność',
    'icon': 'mdi:water-percent',
})
hass.states.set('sensor.thingy_pressure', round(payload["Press"] * 1000, 2), {
    'unit_of_measurement': 'hPa',
    'device_class': 'preasure',
    'friendly_name': 'Thingy 91 - Ciśnienie',
    'icon': 'mdi:gauge',
})
hass.states.set('sensor.thingy_gas', payload["Gas"], {
    'unit_of_measurement': 'Ω',
    'device_class': 'gas',
    'friendly_name': 'Thingy 91 - Opór gazów VOC',
    'icon': 'mdi:gas-cylinder',
})


def get_gas_baseline():
    state = hass.states.get('sensor.thingy_gas_baseline')

    if state.state == "unknown":
        logger.warning("Can not get gas_baseline")
        return

    try:
        return float(state.state)
    except ValueError:
        logger.warning("Could not parse gas_baseline, raw value is %s", state.state)


gas_baseline = get_gas_baseline() or 30000

# Set the humidity baseline to 40%, an optimal indoor humidity.
hum_baseline = 40.0

# This sets the balance between humidity and gas reading in the
# calculation of air_quality_score (25:75, humidity:gas)
hum_weighting = 0.25

gas = payload["Gas"]
gas_offset = gas_baseline - gas

hum = payload["Humid"]
hum_offset = hum - hum_baseline

# Calculate hum_score as the distance from the hum_baseline.
if hum_offset > 0:
    hum_score = (100 - hum_baseline - hum_offset) / (100 - hum_baseline) * (hum_weighting * 100)
else:
    hum_score = (hum_baseline + hum_offset) / hum_baseline * (hum_weighting * 100)

# Calculate gas_score as the distance from the gas_baseline.
if gas_offset > 0:
    gas_score = (gas / gas_baseline) * (100 - (hum_weighting * 100))
else:
    gas_score = 100 - (hum_weighting * 100)

# Calculate air_quality_score.
air_quality_score = hum_score + gas_score

iaq = round((1 - (air_quality_score/100)) * 500, 1)





hass.states.set('sensor.thingy_iaq', iaq, {
    'unit_of_measurement': 'IAQ',
    'device_class': 'gas',
    'friendly_name': 'Thingy 91 - IAQ',
    'icon': 'mdi:air-filter',
})

battery = int((payload["Vbat"]/1000 - 3.6) * 10000/56)
if battery > 100:
    battery = 100
if battery < 0:
    battery = 0

hass.states.set('sensor.thingy_battery', battery, {
    'unit_of_measurement': '%',
    'device_class': 'battery',
    'friendly_name': 'Thingy 91 - Bateria',
    'icon': 'mdi:battery-50',
})

logger.info("process_iotcreators data set")
