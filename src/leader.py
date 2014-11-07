'''
Created on 16.3.2012

@author: Antti Vainio
'''

from vector import vector
from thinker import thinker
import random

class leader(thinker):
    '''
    This class is derived from the thinker class.
    '''

    def __init__(self, user_controlled, x, y, max_speed = -1, max_force = -1, size = -1, random_position = True):
        super(leader, self).__init__(x, y, max_speed, max_force, size, random_position)
        self.is_leader = True
        self.user_controlled = user_controlled
        self.user_up = False
        self.user_down = False
        self.user_left = False
        self.user_right = False
        self.current_seek_target = self.pos
        self.randomizeSeekOffsetSpeed()
        
        
    def randomizeSeekOffsetSpeed(self):
        '''
        Sets a new random speed for the seek target itself to move.
        '''
        self.seek_offset_speed = vector(random.uniform(-2, 2), random.uniform(-2, 2))
        
        
    def displace(self, v):
        super(leader, self).displace(v)
        self.current_seek_target+= v
    
    
    def think(self, others):
        '''
        When the leader is user controlled the leader uses the same seek target logic as without user control.
            The target to be sought to is set in the direction desired by user.
        When the leader is not user controlled the seek target moves using self.seek_offset_speed.
            The position of seek target and self.seek_offset_speed
            is randomized at regular interval or when the leader gets too close to the seek target.
        '''
        if self.user_controlled:
            direction = vector(0, 0)
            if self.user_up: direction.y-= 100
            if self.user_down: direction.y+= 100
            if self.user_left: direction.x-= 100
            if self.user_right: direction.x+= 100
            self.current_seek_target = self.pos + direction
        else:
            distance = self.current_seek_target - self.pos
            if distance.lenght < 10.0 or random.randint(0, 300) == 0:
                self.current_seek_target = self.pos + vector(random.uniform(-50, 50), random.uniform(-50, 50))
                self.randomizeSeekOffsetSpeed()
            else:
                self.seek_offset_speed+= vector(random.uniform(-0.3, 0.3), random.uniform(-0.3, 0.3))
                self.seek_offset_speed.clamp(0, 2.5)
                self.current_seek_target+= self.seek_offset_speed
        #go, seek!
        self.seekTraget(self.current_seek_target, 1.0)
        
        