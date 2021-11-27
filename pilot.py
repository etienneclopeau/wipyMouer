import utils
import parameters
import utime

# currentCommand = {'mode': "Manual", "blade": False, 'up': False, 'left': False, 'right': False, 'down': False}
currentCommand = {'mode': "Auto", "blade": False, 'up': False, 'left': False, 'right': False, 'down': False}
class Pilot():
    def __init__(self, durationOfPause, rotationDurationMin, rotationDurationMax, reverseDurationMin, reverseDurationMax, forwardMaxDuration):
        self.durationOfPause = durationOfPause
        
        self.rotationDurationMin = rotationDurationMin
        self.rotationDurationMax = rotationDurationMax
        self.reverseDurationMin = reverseDurationMin
        self.reverseDurationMax = reverseDurationMax


        self.currentSpeed = 0
        self.currentTurn = 0

        self.speedSmoother = utils.Smoother(windowLength = parameters.speedSmoothingWindow)
        self.turnSmoother = utils.Smoother(windowLength = parameters.rotationSmoothingWindow)

        self.rotationStarted = False
        self.rotationStartTime = 0
        self.rotationWantedDuration = 0

        self.reverseStarted = False
        self.reverseStartTime = 0
        self.reverseWantedDuration = 0

        self.blocked = False

        self.forwardStarted = False
        self.forwardStartTime = 0
        self.forwardMaxDuration = forwardMaxDuration

        self.blockageStartTime = 0


    def update(self, command, obstacleDetected = None, nbOfCurrentLimitOverPassing = None):
        if  command["mode"] == "Manual":
            self.manualUpdate(command)
        elif command["mode"] == "Auto":
            self.autoUpdate(obstacleDetected, nbOfCurrentLimitOverPassing)
        else:
            raise ValueError("%s not reconized"%command["mode"])
    
    def manualUpdate(self, command):
        
        self.currentSpeed = self.speedSmoother.smoothThis(parameters.motion_maxSpeed*command["up"] - parameters.motion_maxSpeed*command["down"])
        self.currentTurn = self.turnSmoother.smoothThis(parameters.motion_maxRotation*command["right"] - parameters.motion_maxRotation*command["left"])
        # print("speed", self.currentSpeed, " turn",self.currentTurn)
        print ('pilot Manual', self.currentSpeed,self.currentTurn )

    def autoUpdate(self, obstacleDetected, nbOfCurrentLimitOverPassing):
        if self.blocked : 
            print('blocked')
            self.currentSpeed = 0
            self.currentTurn = 0
            return
        elif self.reverseStarted:
            if nbOfCurrentLimitOverPassing > 30:
                print('blocage en reverse')
                if self.blockageStartTime == 0 :
                    self.blockageStartTime = utime.ticks_ms()
                else:
                    self.currentSpeed = self.speedSmoother.smoothThis(0)
                    self.currentTurn = self.turnSmoother.smoothThis(0)
                    print("duree blocage ",utime.ticks_ms() - self.blockageStartTime)
                    if utime.ticks_ms() - self.blockageStartTime > 1000:
                        self.blockageStartTime = 0
                        self.blocked = True
                        self.reverseStarted = False
            else:
                if utime.ticks_ms()- self.reverseStartTime > self.reverseWantedDuration:
                    print('end of reverse detected',utime.ticks_ms()- self.forwardStartTime)
                    self.startRotation()
                    self.reverseStarted = False
                elif utime.ticks_ms()- self.reverseStartTime < self.durationOfPause :
                    self.currentSpeed = self.speedSmoother.smoothThis(0)
                    self.currentTurn = self.turnSmoother.smoothThis(0)
                else:
                    self.currentSpeed = self.speedSmoother.smoothThis(-parameters.motion_maxSpeed)
                    self.currentTurn = self.turnSmoother.smoothThis(0)
        elif self.rotationStarted:
            if nbOfCurrentLimitOverPassing > 30:
                print('blocage en rotation')
                if self.blockageStartTime == 0 :
                    self.blockageStartTime = utime.ticks_ms()
                else:
                    self.currentSpeed = self.speedSmoother.smoothThis(0)
                    self.currentTurn = self.turnSmoother.smoothThis(0)
                    print("duree blocage ",utime.ticks_ms() - self.blockageStartTime)
                    if utime.ticks_ms() - self.blockageStartTime > 1000:
                        self.blockageStartTime = 0
                        self.blocked = True
                        self.rotationStarted = False
            else:
                if utime.ticks_ms()- self.rotationStartTime > self.rotationWantedDuration:
                    print('end of rotation detected',utime.ticks_ms()- self.forwardStartTime)
                    self.startForward()
                    self.rotationStarted = False
                elif utime.ticks_ms()- self.rotationStartTime < self.durationOfPause :
                    self.currentSpeed = self.speedSmoother.smoothThis(0)
                    self.currentTurn = self.turnSmoother.smoothThis(0)
                else:
                    self.currentSpeed = self.speedSmoother.smoothThis(0)
                    self.currentTurn = self.turnSmoother.smoothThis(parameters.motion_maxRotation)
        elif self.forwardStarted:
            if nbOfCurrentLimitOverPassing > 30:
                print('blocage en forward')
                if self.blockageStartTime == 0 :
                    self.blockageStartTime = utime.ticks_ms()
                else:
                    self.currentSpeed = self.speedSmoother.smoothThis(0)
                    self.currentTurn = self.turnSmoother.smoothThis(0)
                    print("duree blocage ",utime.ticks_ms() - self.blockageStartTime)
                    if utime.ticks_ms() - self.blockageStartTime > 1000:
                        self.blockageStartTime = 0
                        self.startReverse()
                        self.forwardStarted = False
            else:
                if utime.ticks_ms()- self.forwardStartTime > self.forwardMaxDuration:
                    print('max duration for forward detected',utime.ticks_ms()- self.forwardStartTime)
                    self.startReverse()
                    self.forwardStarted = False
                elif utime.ticks_ms()- self.forwardStartTime < self.durationOfPause :
                    self.currentSpeed = self.speedSmoother.smoothThis(0)
                    self.currentTurn = self.turnSmoother.smoothThis(0)
                else:
                    self.currentSpeed = self.speedSmoother.smoothThis(parameters.motion_maxSpeed)
                    self.currentTurn = self.turnSmoother.smoothThis(0)
        else:
            print('on démare en marche avant')
            self.startReverse()
        print ('pilot Auto', self.currentSpeed,self.currentTurn )

  
    
    def startRotation(self):
        self.rotationStarted = True
        self.rotationStartTime = utime.ticks_ms()
        self.rotationWantedDuration = utils.random(parameters.rotationDurationMin,parameters.rotationDurationMax)
        print('début rotation',self.rotationWantedDuration)

    def startReverse(self):
        self.reverseStarted = True
        self.reverseStartTime = utime.ticks_ms()
        self.reverseWantedDuration = utils.random(parameters.reverseDurationMin,parameters.reverseDurationMax)
        print('début reverse',self.reverseWantedDuration)
    
    def startForward(self):
        self.forwardStarted = True
        self.forwardStartTime = utime.ticks_ms()
        print('début forward')



class Dispatcher():
    def __init__(self, rightMotor, leftMotor):
        self.rightMotor = rightMotor
        self.leftMotor = leftMotor

    def dispatch(self, speed, turn):
        # print('dispatcher','   speed',speed,' turn',turn)
        self.rightMotor.setSpeed(speed-turn)
        self.leftMotor.setSpeed(speed+turn)



