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

logger.info("process_iotcreators decoded data %s", decoded_paylod)


def load_json(text):
    result = {}
    for i in text.strip("{}").split(","):
        key, value = i.split(":")
        result[key.strip('"')] = float(value)
    return result

payload = load_json(decoded_paylod)

logger.info("process_iotcreators data %s", payload)

if("Temp" in payload):
  attrs = hass.states.get('sensor.garage_temperature').attributes
  hass.states.set('sensor.garage_temperature', payload["Temp"], attrs)

if("Humid" in payload):
  attrs = hass.states.get('sensor.garage_humidity').attributes
  hass.states.set('sensor.garage_humidity', payload["Humid"], attrs)

if("Press" in payload):
  attrs = hass.states.get('sensor.garage_pressure').attributes
  hass.states.set('sensor.garage_pressure', round(payload["Press"] * 1000, 2), attrs)

if("Gas" in payload):
  attrs = hass.states.get('sensor.garage_gas').attributes
  hass.states.set('sensor.garage_gas', payload["Gas"], attrs)

if("Vbat" in payload):
  battery = int((payload["Vbat"]/1000 - 3.6) * 10000/56)
  if battery > 100:
      battery = 100
  if battery < 0:
      battery = 0

  hass.states.set('sensor.thingy_battery', battery, {
      'unit_of_measurement': '%',
      'device_class': 'battery',
      'friendly_name': 'Garaż - Bateria',
      'icon': 'mdi:battery-50',
  })

if("Door" in payload):
  labels = {
    1: "opening",
    2: "open",
    3: "closing",
    4: "closed",
    5: None,
    -1: None,
  }
  label = labels.get(int(payload["Door"]), None)

  attrs = hass.states.get('cover.garage_door').attributes
  hass.states.set('cover.garage_door', label, attrs)

if("Car" in payload):
  attrs = hass.states.get('binary_sensor.garage_car_presence').attributes
  hass.states.set('binary_sensor.garage_car_presence', "on" if int(payload["Car"]) == 1 else "off", attrs)

logger.info("process_iotcreators data set")
