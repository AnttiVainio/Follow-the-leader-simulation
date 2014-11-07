'''
Created on 16.3.2012

@author: Antti Vainio
'''

from vector import vector
import random, abc

#not actually used here!
#used in main and simulation
class unitType:
    none, leader, follower = range(3)


class thinker():
    '''
    This class is an abstract class used by leader and follower classes.
    This class cannot be used straight away because it has one abstract method.
    The only thing the derivatives of this class are really supposed to do is to figure out where to seek or flee
        and then use the functions seekTarget() and fleeTarget() of this class to do that.
    
    In every frame of the simulation the think() function of this class should be called before the move() function.
    When the think() function is set up correctly in the derived class the self.current_force gets set
        and the move() function will then use that to move the thinker to its new position
        while also setting the self.current_force back to 0 for the next frame.
    '''
    
    __metaclass__ = abc.ABCMeta

    def __init__(self, x, y, max_speed = -1, max_force = -1, size = -1, random_position = True):
        '''
        x and y should be the window dimensions when random_position is True.
        '''
        if random_position: self.pos = vector(random.uniform(0, x), random.uniform(0, y))
        else: self.pos = vector(x, y)
        self.speed = vector(0, 0)
        if max_speed > 0: self.max_speed = max_speed
        else: self.randomizeMaxSpeed()
        self.current_force = vector(0, 0)
        if max_force > 0: self.max_force = max_force
        else: self.randomizeMaxForce()
        if size > 0: self.size = size
        else: self.randomizeSize()
        #This is used for drawing
        self.last_seek_target = vector(0, 0)
        
        
    #These three functions set the default randomized values for different attributes.
    def randomizeMaxSpeed(self):
        self.max_speed = random.uniform(0.4, 1.6)
    def randomizeMaxForce(self):
        self.max_force = random.uniform(0.05, 0.15)
    def randomizeSize(self):
        self.size = random.uniform(3.0, 8.0)
        
        
    def setPosition(self, v):
        self.pos = v
    
    
    def displace(self, v):
        self.pos+= v
        
        
    def move(self):
        '''
        This function actually moves this thinker to a new position
            using self.current_force that should be the desired force.
        '''
        self.current_force.clamp(0, self.max_force)
        self.speed+= self.current_force
        self.speed.clamp(0, self.max_speed)
        self.pos+= self.speed
        self.current_force = vector(0, 0)
        
        
    def steerDirection(self, v, weight):
        '''
        This function is used by seekTarget() and fleeTarget().
        This function also alters the self.current_force for the move() function.
        '''
        v.normalize()
        v*= self.max_speed
        force = v - self.speed
        force.clamp(0, self.max_force)
        force*= weight
        self.current_force+= force
        
    '''    
    These two functions should be used in the think() function of the derived classes.
    When called, the weight is mainly used for setting the relative weight between different calls to these functions
        as these functions can be called many times in a single think() function.
    
    Weight of 1.0 equals to maximum force or if the desired speed is smaller than the max force it equals to that speed.
    Weight bigger than 1.0 equals to bigger than maximum force
        and that can be used to override other calls to this function.
    Weight smaller than 1.0 equals to smaller than maximum force and that can be used for arrival.
    '''
    def seekTraget(self, v, weight):
        self.last_seek_target = v #for drawing purposes
        desired_speed = v - self.pos
        self.steerDirection(desired_speed, weight)
    def fleeTraget(self, v, weight):
        desired_speed = self.pos - v
        self.steerDirection(desired_speed, weight)
    
    
    @abc.abstractmethod
    def think(self, others):
        pass
        
        