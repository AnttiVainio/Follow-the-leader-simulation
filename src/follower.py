'''
Created on 16.3.2012

@author: Antti Vainio
'''

from thinker import thinker

class follower(thinker):
    '''
    This class is a very simple derivation of the thinker class.
    The class implements the required think() function where it tries to follow its leader.
    '''

    def __init__(self, leader, x, y, max_speed = -1, max_force = -1, size = -1, random_position = True):
        super(follower, self).__init__(x, y, max_speed, max_force, size, random_position)
        self.leader = leader
        self.is_leader = False
    
    
    def think(self, others):
        '''
        The follower tries to follow its leader while also trying to avoid other followers.
        If there is no leader to be followed the follower will still avoid others while also seeking to its own position.
            The result in that situation is that the followers scatter with a slowing speed.
        '''
        if not self.leader:
            self.seekTraget(self.pos, 0.2)
        else:
            #leader seeking
            away = self.pos - self.leader.pos
            away.normalize()
                #position to seek
            seek_pos = self.leader.pos + away * (self.size + self.leader.size) * 2.0
                #for distance to seek position
            distance = seek_pos - self.pos
            seek_pos+= self.leader.speed * distance.lenght / self.max_speed * 0.1
                #for arrival
            arrival_max_dist = (self.max_speed ** 2.0) / 2.0 / self.max_force
            if distance.lenght <= arrival_max_dist:
                seek_pos+= away * distance.lenght
                #go, seek!
            self.seekTraget(seek_pos, 1.0)
        #follower avoidance
        for i in others:
            if i.pos != self.pos:
                distance = i.pos - self.pos
                #this is 1/x^2 where x is distance
                #x is 1 when distance is (self.radius + other.radius) * 1.2
                distance = 1.0 / (distance.lenght / (self.size + i.size) / 1.2) ** 2.0
                self.fleeTraget(i.pos, distance)

