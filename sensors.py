import machine,time
from machine import Pin, I2C
import pycom
import utime
import utils
import ads1x15

i2c = I2C(0)
i2c.init()
ads1115 = ads1x15.ADS1115(i2c)

class ItensitySensor():
    def __init__(self,pin, CurrentSmoothingWindow, currentLimitMonitor):
        self.pin = pin
        self.adc = machine.ADC() 
        # self.apin = self.adc.channel(pin=pin, attn=machine.ADC.ATTN_11DB)
        self.value = 0
        self.currentLimitMonitor = currentLimitMonitor
        self.nbOfCurrentLimitOverPassing = 0
        self.zero = 0
        self.smoother = utils.Smoother(CurrentSmoothingWindow)
    def getIntensity(self):
        # self.value = self.smoother.smoothThis(abs(self.apin() - self.zero))
        # self.value = self.smoother.smoothThis((self.apin() - self.zero))
        self.value = self.smoother.smoothThis(ads1115.read(channel1 = self.pin) - self.zero)
        # print(self.value, self.currentLimitMonitor)
        if self.value > self.currentLimitMonitor:
            self.nbOfCurrentLimitOverPassing += 1
        else:
            self.nbOfCurrentLimitOverPassing = 0
        return self.value
    
    def qualibrate(self):
        print("start qualibration")
        total = 0
        nb = 500
        i = 0
        while i < nb:
            # total += self.apin()
            print(i)
            #print(ads1115.read(channel1 = self.pin))
            total += ads1115.read(channel1 = self.pin)
            i+=1
            time.sleep_ms(20)
        self.zero = total / nb
        print("qualibration", self.zero)

    def sequence(self,nb):
        print("start sequence")
        total = 0
        i = 0
        while i < nb:
            # val = self.apin()
            val = ads1115.read(channel1 = self.pin)
            total += val
            i+=1
            print(utime.ticks_ms(), val, (val-self.zero), total/i)
        self.zero = total / nb
        print("end sequence", self.zero)


class VoltageSensor():
    def __init__(self,pin, smoothingWindow = 1):
        self.pin = pin
        self.adc = machine.ADC() 
        self.apin = self.adc.channel(pin=pin)#, attn=machine.ADC.ATTN_11DB)
        self.smoother = utils.Smoother(windowLength = smoothingWindow)
    def getVoltage(self):
        return self.smoother.smoothThis(self.apin() / 4095 * 1.1 /0.0435 /0.93 )   # indeed, read = 4095*(Vin/Vref) ; Vref = 1.1 ; 0.0435 is the pont diviseur ; 0.93 for qualibration


# def callbackHigh(ultrasonicPing):
#     # print('start callbackHigh ')
#     # ultrasonicPing.callback(Pin.IRQ_RISING | Pin.IRQ_HIGH_LEVEL, None)
#     ultrasonicPing.callback(Pin.IRQ_FALLING | Pin.IRQ_LOW_LEVEL, callbackLow, arg = ultrasonicPing)
#     # ultrasonicPing.echoStartTime = utime.ticks_us()
#     print('High ',utime.ticks_us())
#     # print('callbackHigh ',time.ticks_ms())


# def callbackLow(ultrasonicPing):
#     # print('start callbackLow ')
#     # ultrasonicPing.callback(Pin.IRQ_RISING | Pin.IRQ_HIGH_LEVEL | Pin.IRQ_FALLING | Pin.IRQ_LOW_LEVEL, None)
#     ultrasonicPing.echoDuration = utime.ticks_us()-ultrasonicPing.echoStartTime
    
#     ultrasonicPing.distance = int((ultrasonicPing.echoDuration / 2.) / 29.1)
#     # print('callbackLow ', utime.ticks_ms(), ultrasonicPing.echoDuration, ultrasonicPing.distance)
#     print('Low ', utime.ticks_us(), ultrasonicPing.echoDuration, ultrasonicPing.distance)


class UltrasonicPing(Pin):
    def __init__(self, *args, **kwargs):
        if "timeout" in kwargs.keys():
            self.timeout = kwargs["timeout"] # ms
            kwargs.pop("timeout")
        else:
            self.timeout = 100 #ms
        super().__init__( *args, **kwargs)
        # self.pin = Pin(self.pin, mode=Pin.OUT, pull=None)
        self.distance = 0
        self.measureRuning = False
        self.measureStartTime = 0
        self.echoStartTime = 0
    
    def sendPulse(self):
        self.mode(Pin.OUT)
        self.value(0) # Stabilize the sensor
        time.sleep_us(5)
        self.value(1)
        # Send a 10us pulse.
        time.sleep_us(10)
        self.value(0)

    def receivePulse(self):
        self.mode(Pin.IN)
        try:
            # pulse_time = machine.time_pulse_us(echo, 1, self.echo_timeout_us)
            pulse_time = pycom.pulses_get(self.id(), self.timeout)
            # print(pulse_time)
            return pulse_time
        except OSError as ex:
            if ex.args[0] == 110: # 110 = ETIMEDOUT
                raise OSError('Out of range')
            raise ex
    
     
    # def updateMeasure(self):
    #     if not self.measureRuning:
    #         self.measureRuning = True
    #         self.measureStartTime = utime.ticks_ms()
    #         self.sendPulse()
    #         self.mode(Pin.IN)
    #         # print("define callback")
    #         # self.callback(Pin.IRQ_RISING | Pin.IRQ_HIGH_LEVEL, callbackHigh, arg = self)
    #         self.callback(Pin.IRQ_RISING | Pin.IRQ_HIGH_LEVEL, None)
    #         start = time.ticks_us()
    #         while time.ticks_us()-start < 100000:
    #             utime.sleep_us(5)
    #             print(time.ticks_us(),self.value())
    #         raise()
    #         time.sleep(0.2)
    #         self.sendPulse()
    #         print(self.receivePulse())
    #         time.sleep(1)
    #         return self.distance
    #     else:
    #         if time.ticks_ms() - self.measureStartTime > self.timeout:
    #             #on réinitialise
    #             self.measureRuning = False
    #             self.callback(Pin.IRQ_RISING | Pin.IRQ_FALLING, None)
    #             print("ultrasonicSensor time out, last distance %s"%self.distance)
    #             return self.distance



    
    def distance_cm(self):
        self.sendPulse()       
        
        
        received_pulse = self.receivePulse()
        # print(received_pulse)
        # To calculate the distance we get the pulse_time and divide it by 2 
        # (the pulse walk the distance twice) and by 29.1 becasue
        # the sound speed on air (343.2 m/s), that It's equivalent to
        # 0.034320 cm/us that is 1cm each 29.1us
        if len(received_pulse)>= 1:
            pulse_time = received_pulse[0][1]
            if pulse_time > 18000:
                return None
            else:
                return int((pulse_time / 2.) / 29.1)
        else:
            return None

class ObstacleDetector():
    def __init__(self, ultrasonicSensor, minDist = 3 , maxDist = 30) :
        self.ultrasonicSensor = ultrasonicSensor
        self.minDist = minDist
        self.maxDist = maxDist  
        self.range = self.maxDist - self.minDist
        self.distance = 0.

    def isObstacleDetected(self):
        self.measuredDistance = self.ultrasonicSensor.distance_cm()
        if self.measuredDistance is not None:
            self.distance = self.measuredDistance
        #Sinon on ne fait rien, on continuera à travailler avec self.distance (dernière distance valide)


        if self.distance < self.minDist:
            return 1
        elif self.distance > self.maxDist:
            return 0
        else:
            # print(utime.ticks_ms())
            return 1 - (self.distance - self.minDist) / self.range 

