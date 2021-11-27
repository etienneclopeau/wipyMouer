from parameters import *
import time


import paho.mqtt.client as mqtt

time0 = time.time()

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(topic_batteryVoltage)
    client.subscribe(topic_wheelMotorsIntensity)
    client.subscribe(topic_bladeMotorIntensity)
    client.subscribe(topic_debug)

# The callback for when a PUBLISH message is received from the server.
global new_data
new_data = getEmptyData()
print('test', len(new_data['time']))

def on_message(client, userdata, msg):
    # print(msg.topic+" "+str(msg.payload))
    # print(msg.topic, topic_debug)
    if msg.topic == topic_debug:
        # print(msg.topic+" "+str(msg.payload))
        # print(str(msg.payload)[2:-1].split(';')[:-1])
        data = [eval(a) for a in str(msg.payload)[2:-1].split(';')[:-1]]
        print(msg.topic+" "+str(data))
        # print('test', len(new_data['time']))

        new_data['time'].append(time.time() - time0)
        for var,val in zip(debugData,data):
            # print(val)
            new_data[var].append(val)




def reset_new_data():
    for key in new_data.keys():
        new_data[key] = list()

def startMqttClient():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.loop_start()

    client.connect(mqtt_server, 1883, 60) # port 1883, keepalive 60s
    return client
