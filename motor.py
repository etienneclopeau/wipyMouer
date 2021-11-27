from machine import PWM, Pin
from utils import Smoother

class MOTOR():
    def __init__(self, timer, sensPinNumber, PWMpinNumber, minSpeed = 0, maxSpeed = 100, smoothingWindowLength = 20, sensInvertion = 1):
        self.sensPinNumber = sensPinNumber
        self.PWMpinNumber = PWMpinNumber
        self.timer = timer
        self.pwm = PWM(self.timer, frequency=5000)  
        self.pwm_c = self.pwm.channel(self.timer, pin=self.PWMpinNumber, duty_cycle=0.0)
        self.pinSens = Pin(sensPinNumber, mode = Pin.OUT)
        self.minSpeed = minSpeed 
        self.maxSpeed = maxSpeed 
        self.smoother = Smoother(smoothingWindowLength)
        self.smoothedSpeed = 0
        self.localSpeed = 0
        self.sensInvertion = sensInvertion
        self.definePWMCycle( 0)

    
    def definePWMCycle(self, cycle):
        if cycle * self.sensInvertion > 0: 
            self.pinSens.value(0)
        else:
            self.pinSens.value(1)
        self.pwm_c.duty_cycle(abs(cycle)) 
        # print(self.pinSens.value(), cycle, self.smoothedSpeed)
        

    def setSpeed(self, speed):
        """ 
        speed en %
            * for speed < 1% , motor is stoped
            * for speed = 1% , motor speed is set to self.minSpeed
            * for speed = 100%, motor speed is set to self.maxSpeed
        O% = minSpeed ; 100% = maxSpeed"""
        if speed > 100 : speed = 100
        elif speed < -100 : speed = -100


        if abs(speed) < 1:
            self.localSpeed = 0
        elif speed > 0 :
            self.localSpeed = self.minSpeed + speed / 100 * (self.maxSpeed - self.minSpeed)
        elif speed < 0:
            self.localSpeed = -self.minSpeed + speed / 100 * (self.maxSpeed - self.minSpeed)

        
        self.smoothedSpeed = self.smoother.smoothThis(self.localSpeed)

        self.definePWMCycle(self.smoothedSpeed / 100.)

