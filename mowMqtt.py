
from umqttsimple import MQTTClient
import pycom


import ubinascii
import machine
from parameters import *
import pilot

client_id = ubinascii.hexlify(machine.unique_id())

import json
def sub_cb(topic, msg):
  # print((topic, msg))
  pycom.rgbled(0x007f00) # vert
  # print(str(topic)[2:-1])
  if str(topic)[2:-1] == topic_command:
    # print(str(msg)[2:-1].replace("'",'"'))
    # currentCommand = json.loads(str(msg)[2:-1].replace("'",'"')) 
    currentCommand = eval(str(msg)[2:-1].replace("'",'"'))
    print("new command received",currentCommand)
    for key in currentCommand.keys():
      pilot.currentCommand[key] = currentCommand[key]


mqttClient = MQTTClient(client_id, mqtt_server)
mqttClient.set_callback(sub_cb)
mqttClient.connect()
mqttClient.subscribe(topic_command)

