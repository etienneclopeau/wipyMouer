from parameters import *
import time

from mqttClient import startMqttClient
client = startMqttClient()

from pynput import keyboard

from streamTracer import startBokehApp #, plotpanel

current = dict(mode = "Manual",
               blade = False,
               up = False,
               left = False,
               right = False,
               down = False)

def on_press(key):
    print(str(key))
    updated = False
    if key == keyboard.Key.up:
        if not current['up'] :
            current['up'] = True
            updated = True
    elif key == keyboard.Key.left:
        if not current['left'] :
            current['left'] = True
            updated = True
    elif key == keyboard.Key.down:
        if not current['down'] :
            current['down'] = True
            updated = True
    elif key == keyboard.Key.right:
        if not current['right'] :
            current['right'] = True
            updated = True
    elif key == keyboard.Key.esc:
        if not current['mode'] == "Manual" :
            current['mode'] = "Manual"
            updated = True
    elif str(key) == "'a'":
        if not current['mode'] == "Auto" :
            current['mode'] = "Auto"
            updated = True
    elif key == keyboard.Key.space:
        if not current['blade'] :
            current['blade'] = True
            updated = True

    if updated :
        client.publish(topic_command,str(current))
        print("update command", str(current))

def on_release(key):
    updated = False
    if key == keyboard.Key.up:
        if current['up'] :
            current['up'] = False
            updated = True
    elif key == keyboard.Key.left:
        if current['left'] :
            current['left'] = False
            updated = True
    elif key == keyboard.Key.down:
        if current['down'] :
            current['down'] = False
            updated = True
    elif key == keyboard.Key.right:
        if current['right'] :
            current['right'] = False
            updated = True
    elif key == keyboard.Key.space:
        if current['blade'] :
            current['blade'] = False
            updated = True
    if updated :
        client.publish(topic_command,str(current))
        print("update command", str(current))


#  in a non-blocking fashion:
listener = keyboard.Listener(
    on_press = on_press,
    on_release = on_release)
listener.start()


startBokehApp()
# plotpanel()
