


mqtt_server = "192.168.1.57"
topic_batteryVoltage = "robotMower_batteryVoltage"
topic_wheelMotorsIntensity = "robotMower_wheelMotorsIntensity"
topic_bladeMotorIntensity = "robotMower_bladeMotorIntensity"
topic_command = "robotMower_command"
topic_debug = "robotMower_debug"


debugData = ['dt',
            'wheelCurrent', 'bladeCurrent', 'batteryVoltage',
            # 'distance', 'obstacle detected',
            'speed filtered command', 'rotation filtered command',
            'leftMotor speed', 'leftMotor filtered Speed',
            'rightMotor speed', 'rightMotor filtered Speed',
            # 'batteryVoltage','wheelMotorsIntensity','bladeMotorIntensity', 
            ]
# plotingData = [[['speed filtered command', 'rotation filtered command'],['dt',]],
#                [['leftMotor speed', 'leftMotor filtered Speed',
#             'rightMotor speed', 'rightMotor filtered Speed'],['wheelCurrent', 'bladeCurrent',]],
#                 ['batteryVoltage']]


def getEmptyData ():
    emptyData= {
        'time' : list(),
    }
    for var in debugData:
        emptyData[var] = list()
    return emptyData
plotPeriod = 100 # ms


leftWheelMotorPWMPin = 'P22'
leftWheelMotorSensPin = 'P20'
leftWheelMototSens = -1
rightWheelMotorPWMPin = 'P21'
rightWheelMotorSensPin = 'P19'
rightWheelMototSens = 1
bladeMotorPWMPin = 'P11'
bladeMotorSensPin = 'P12'

distanceSensorPin = "P6"
distanceSensorTimeout = 30 # ms  #en us ; soit 30 *29.1*2   # pour détecter à 30cm max

# wheelCurrentSensorPin = "P17"
wheelCurrentSensorPin = 1
# wheelCurrentSensorADCid = 1#3
wheelCurrentLimit = 2000
wheelCurrentSmoothingWindow = 3
# bladeCurrentSensorPin = "P15"
bladeCurrentSensorPin = 0
# bladeCurrentSensorADCid = 1#2
bladeCurrentLimit = 2500
bladeCurrentSmoothingWindow = 3
batteryVoltageSensorPin = "P13"
# batteryVoltageSensorADCid = 1#0
batteryVoltageSensorSmoothingWindow = 100


wheelMotors_maxSpeed = 80
wheelMotors_minSpeed = 0
wheelMotors_smoothingWindow = 5


motion_maxSpeed = 100
motion_maxRotation = 60
speedSmoothingWindow = 10
rotationSmoothingWindow = 10

bladeMotor_maxSpeed = 100
bladeMotor_minSpeed = 20
bladeMotor_smoothingWindow = 10



#Pilot

durationOfPause = 1000

rotationDurationMin = 1000 + durationOfPause
rotationDurationMax = 3000 + durationOfPause

reverseDurationMin = 1000 + durationOfPause
reverseDurationMax = 3000 + durationOfPause

forwardMaxDuration = 30000 + durationOfPause
