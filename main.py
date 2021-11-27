

# boot.py -- run on boot-up
def connect():
    import machine
    from network import WLAN
    import network


    wifiSSID = 'TP-LINK_DA3B'
    wifiKey = '59507840'
    ipAdress = '192.168.1.107'


    # Disable telnet and FTP server before connecting to the network
    # server = network.Server()
    # server.deinit()

    wlan = WLAN() # get current object, without changing the mode


    if machine.reset_cause() != machine.SOFT_RESET:
        wlan.init(mode = WLAN.STA)
        wlan.ifconfig(config=(ipAdress, '255.255.255.0', '192.168.1.1', '8.8.8.8'))


    for i in range(3):
        if not wlan.isconnected():
            # change the line below to match your network ssid, security and password
            print("Trying to connect to wifi %i/3: "%(i+1) , wifiSSID)  
            try:
                wlan.connect(wifiSSID, auth=(WLAN.WPA2, wifiKey), timeout=8000)
                while not wlan.isconnected():
                    machine.idle() # save power while waiting
            except Exception:
                print("Timeout")
        

    if wlan.isconnected():
        print(wlan.ifconfig())
        print("Wifi connexion : ", wlan.isconnected())
    else:
        print("#####    No Wifi connexion    ####")





#################################################################################################""""
# main.py -- put your code here!
import pycom
import time
import math
from sensors import *
from parameters import *
import pilot
pycom.heartbeat(False)

# import gc
# gc.enable()



for cycles in range(10): # Arreter apres 10 cycles
    pycom.rgbled(0x007f00) # vert
    time.sleep(0.1)
    pycom.rgbled(0x7f7f00) # jaune
    time.sleep(0.1)
    pycom.rgbled(0x7f0000) # rouge
    time.sleep(0.1)

connect()
from mowMqtt import *


from motor import MOTOR
leftMotor = MOTOR(1, sensPinNumber = leftWheelMotorSensPin, PWMpinNumber = leftWheelMotorPWMPin , minSpeed = wheelMotors_minSpeed, maxSpeed = wheelMotors_maxSpeed, smoothingWindowLength = wheelMotors_smoothingWindow, sensInvertion=leftWheelMototSens)
rightMotor = MOTOR(2, sensPinNumber = rightWheelMotorSensPin, PWMpinNumber = rightWheelMotorPWMPin , minSpeed = wheelMotors_minSpeed, maxSpeed = wheelMotors_maxSpeed, smoothingWindowLength = wheelMotors_smoothingWindow, sensInvertion=rightWheelMototSens)
bladeMotor = MOTOR(3, sensPinNumber = bladeMotorSensPin, PWMpinNumber = bladeMotorPWMPin , minSpeed = bladeMotor_minSpeed, maxSpeed = bladeMotor_maxSpeed, smoothingWindowLength = bladeMotor_smoothingWindow)


# wheelCurrentSensor = ItensitySensor(wheelCurrentSensorPin, wheelCurrentSensorADCid , wheelCurrentSmoothingWindow, currentLimitMonitor= wheelCurrentLimit)
wheelCurrentSensor = ItensitySensor(wheelCurrentSensorPin , wheelCurrentSmoothingWindow, currentLimitMonitor= wheelCurrentLimit)
wheelCurrentSensor.qualibrate()
# bladeCurrentSensor = ItensitySensor(bladeCurrentSensorPin, bladeCurrentSensorADCid, bladeCurrentSmoothingWindow, currentLimitMonitor= 50)
bladeCurrentSensor = ItensitySensor(bladeCurrentSensorPin, bladeCurrentSmoothingWindow, currentLimitMonitor= bladeCurrentLimit)
bladeCurrentSensor.qualibrate()
# batteryVoltageSensor = VoltageSensor(batteryVoltageSensorPin, batteryVoltageSensorADCid, batteryVoltageSensorSmoothingWindow)
batteryVoltageSensor = VoltageSensor(batteryVoltageSensorPin, batteryVoltageSensorSmoothingWindow)

distanceSensor = UltrasonicPing(distanceSensorPin, timeout = distanceSensorTimeout)
obstacleDetector = ObstacleDetector(distanceSensor)



mowPilot = pilot.Pilot(durationOfPause, rotationDurationMin, rotationDurationMax, reverseDurationMin, reverseDurationMax,forwardMaxDuration)
dispatcher = pilot.Dispatcher(rightMotor, leftMotor)

oldTime = time.ticks_ms() # initialisation



while True:
    dt = time.ticks_diff(time.ticks_ms(), oldTime)
    oldTime = time.ticks_ms()

    # print("waiting for command")
    # time.sleep(0.1)


    wheelCurrent =wheelCurrentSensor.getIntensity()
    bladeCurrent = bladeCurrentSensor.getIntensity()
    batteryVoltage = batteryVoltageSensor.getVoltage()

    obstacleDetected = obstacleDetector.isObstacleDetected()
    # print(obstacleDetected)
    print(wheelCurrentSensor.nbOfCurrentLimitOverPassing)
    mowPilot.update(pilot.currentCommand,  obstacleDetected, wheelCurrentSensor.nbOfCurrentLimitOverPassing)
    dispatcher.dispatch(mowPilot.currentSpeed, mowPilot.currentTurn)

    if pilot.currentCommand["blade"]:
        bladeMotor.setSpeed(100)
    else :
        bladeMotor.setSpeed(0)

    debugData = [ dt,
                 wheelCurrent, bladeCurrent, batteryVoltage,
                # obstacleDetector.distance, obstacleDetected,
                mowPilot.currentSpeed, mowPilot.currentTurn,
                 leftMotor.localSpeed, leftMotor.smoothedSpeed,
                 rightMotor.localSpeed, rightMotor.smoothedSpeed,
                 ]
    debugDataFormated = str()
    for data in debugData:  
        if data is None:
            debugDataFormated += "{};".format(str(None))
        else:
            debugDataFormated += "{:.2f};".format(data)
    # print(debugDataFormated)
    
    # à commenter quand on est en autonome pur
    mqttClient.publish(topic_debug, debugDataFormated)
    mqttClient.check_msg()

    # print(bladeMotor.pwm_c.duty_cycle())
    # gc.collect()



