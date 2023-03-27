# -*- coding: utf-8 -*-

logger.info("Home Temperature has been started")

DAY_TIME = {"from": 6, "to": 20}
DAY_TEMP_INC = 3


sensors = {
    "living_room": "sensor.salon_temperatura",
    "albert_room": "sensor.albert_temperatura",
    "wiktor_room": "sensor.wiktor_temperatura",
    "bedroom": "sensor.sypialnia_temperatura",
    "bathroom": "sensor.dallas_sensor_28_ff64_1e0f_7ac5_2",
    "office_room": "sensor.gabinet_temperatura",
    "toilet": "sensor.toaleta_temperatura",
}

outputs = {
    "living_room": "input_select.salon_strefa_temperatury",
    "albert_room": "input_select.albert_strefa_temperatury",
    "wiktor_room": "input_select.wiktor_strefa_temperatury",
    "bedroom": "input_select.sypialnia_strefa_temperatury",
    "bathroom": "input_select.lazienka_strefa_temperatury",
    "office_room": "input_select.gabinet_strefa_temperatury",
    "toilet": "input_select.toaleta_strefa_temperatury",
}

desired_temps = {
    "living_room": [
      {"from": 7, "to": 19, "temp": 21.5},
      {"from": 20, "to": 22, "temp": 20.5},
      {"temp": 20},
    ],
    "albert_room": [
      {"from": 7, "to": 19, "temp": 21.5},
      {"temp": 20},
    ],
    "wiktor_room": [
      {"from": 7, "to": 19, "temp": 21.5},
      {"temp": 20},
    ],
    "bedroom": [
      {"temp": 16},
    ],
    "bathroom": [
      {"from": 7, "to": 9, "temp": 21.5},
      {"from": 19, "to": 23, "temp": 22.5},
      {"temp": 20},
    ],
    "office_room": [
      {"from": 10, "to": 18, "temp": 21.5},
      {"temp": 20},
    ],
    "toilet": [
      {"from": 21, "to": 23, "temp": 21.5},
      {"temp": 19.5},
    ],
}


def get_desired_temp(room_id):
  current_time = datetime.datetime.now()
  current_hour = current_time.hour

  default_temp = None
  for i in desired_temps[room_id]:
    if 'from' in i and 'to' in i:
      if current_hour >= i['from'] and current_hour <= i['to']:
        return i['temp']
    else:
      default_temp = i['temp']

  return default_temp


def get_zone(current_temp, desired_temp):
  # ... 23 - Zimno
  # 23 ... 24 - Chłodno
  # 24 ... 25 - OK
  # 25 ... 26 - Ciepło
  # 26 ... - Gorąco
  diff = current_temp - desired_temp
  if diff < -1:
    return 'Zimno'
  elif diff < 0:
    return 'Chłodno'
  elif diff < 1:
    return 'OK'
  elif diff < 2:
    return 'Ciepło'
  return 'Gorąco'


def get_temp(sensor_id, room_id):
  state = hass.states.get(sensor_id)

  if state.state == "unknown" or state.state == None:
    logger.warning("Can not get temperature of %s", room_id)
    return

  try:
    return float(state.state)
  except (ValueError, TypeError):
    logger.warning("Could not parse temperature of %s, raw value is %s", room_id, state.state)


def get_current_temps():
  return {
    room_id: get_temp(sensor_id, room_id)
    for room_id, sensor_id in sensors.items()
  }


def set_zones(current_temps):
  for room_id, current_temp in current_temps.items():
    if current_temp is None:
     continue

    desired_temp = get_desired_temp(room_id)
    if desired_temp is None:
      logger.warning("Can not find desired temperature for %s", room_id)
      continue

    temp_zone = get_zone(current_temp, desired_temp)
    logger.debug("Current temp. in %s is %s °C, desired temp. should be %s °C", room_id, current_temp, desired_temp)
    logger.warning("Setting %s temp. zone to %s", room_id, temp_zone)
    attrs = hass.states.get(outputs[room_id]).attributes
    hass.states.set(outputs[room_id], temp_zone, attrs)


def is_day():
  current_time = datetime.datetime.now()
  current_hour = current_time.hour

  return current_hour >= DAY_TIME["from"] and current_hour < DAY_TIME["to"]


def set_heating_temp():
  # see: https://www.buderus.com/ocsmedia/optimized/full/o228308v52_6720813494.pdf page 51
  outside_temp = get_temp("sensor.dom_temperature", "outside")

  if outside_temp < 0:
    heating_temp = round(45 - 1.5 * outside_temp)
  else:
    heating_temp = round(45 - outside_temp)

  if is_day():
    heating_temp = heating_temp + DAY_TEMP_INC

  if heating_temp < 35:
    heating_temp = 35
  elif heating_temp > 80:
    heating_temp = 80

  logger.warning("Setting heating temp. to %s", heating_temp)
  attrs = hass.states.get("input_number.heating_temperature").attributes
  hass.states.set("input_number.heating_temperature", heating_temp, attrs)


current_temps = get_current_temps()
set_zones(current_temps)
set_heating_temp()


logger.info("Home Temperature finished")

