'''
Created on 16.3.2012

@author: Antti Vainio
'''

from leader import leader
from follower import follower
from vector import vector
from thinker import unitType

class simulation():
    '''
    This class handles the calculation of simulation.
    
    A single frame can be calculated and executed just by calling calculateFrame() once.
    When a single frame is calculated,
        first the new positions for all the thinkers are calculated
        and only after that they are moved to their new positions.
    This is because if they were moved instantly
        the thinkers that were calculated after the first ones would use their new positions instead of their old ones.
        
    New thinkers can also be created and old ones removed with simple function calls to this class.
    Also when the window is resized this class should be informed for that
        as the random placement of thinkers use that information.
        
    This class also handles "moving the camera".
        This is done so that first the new "position" for the camera is determined
        and then all the thinkers are displaced so that they are in the middle of the window.
    This way the simulation area is practically infinite.
    '''

    def __init__(self, x, y, amount, force_leader = False):
        '''
        x and y are the current dimensions of the window.
        amount is the amount of followers to be created.
            If any followers are to be created a leader will also be created,
            otherwise no leader will be created.
        if force_leader is set a leader will be created even if no followers are created.
        '''
        self.framecount = 0 #1 is added to this every time calculateFrame() is called
        self.window_middle = vector(x, y) / 2.0
        self.mean_position = vector(0, 0)
        self.thinkers = []
        self.leader = None
        self.thinker_near_mouse = None
        self.active_thinker = None
        if amount or force_leader:
            self.thinkers.append(leader(False, x, y))
            self.leader = self.thinkers[0]
        for i in range(amount): self.thinkers.append(follower(self.leader, x, y))
        self.cam_movement = []
        self.cam_offset = vector(0, 0)
        self.camera_follow = True
        self.user_controlled_leader = False
        
        
    def setWindowSize(self, x, y):
        '''
        This should be called every time the window is resized.
        '''
        self.window_middle = vector(x, y) / 2.0
        del self.cam_movement[:]
        
        
    def move_camera(self, x, y):
        '''
        Is used for user forced camera movement.
        '''
        offset_vector = vector(x, y)
        for i in self.thinkers: i.displace(offset_vector)
        '''
        -1 is added there to "fix" an error
        This used to throw an out of range error probably because:
            len(self.cam_movement) is 35 at first which is also the maximum
            then in calculateFrame() cam_movement gets popped
            then the following 'for' reaches the end where there is no object anymore
                and throws an error
            this can happen because these two functions can be called simultaneously because of threading
        This "fix" only makes the last one of the camera trail dots (that is also soon to be deleted)
            not to move in the debug-drawing mode when user is moving the camera
        '''
        for i in range(len(self.cam_movement) - 1): self.cam_movement[i]+= offset_vector
        self.cam_offset+= offset_vector
        
        
    def setMousePosition(self, x = -1000, y = -1000):
        '''
        This is used to inform this class about the position of the mouse.
        '''
        best_thinker = None
        best_value = 300
        for i in self.thinkers:
            value = (i.pos.x - x) ** 2 + (i.pos.y - y) ** 2
            if value < best_value:
                best_thinker = i
                best_value = value
        self.thinker_near_mouse = best_thinker
        
        
    def chooseThinker(self):
        '''
        Sets the active thinker.
        '''
        self.active_thinker = self.thinker_near_mouse
        if not self.active_thinker: return unitType.none
        elif self.active_thinker.is_leader: return unitType.leader
        return unitType.follower
    
    
    def removeThinker(self, thinker):
        if thinker.is_leader:
            for i in self.thinkers: i.leader = None
            self.leader = None
        self.thinkers.remove(thinker)
        
        
    def createLeader(self, max_speed, max_force, size, random_position = True, x = 0, y = 0):
        old_leader = self.leader
        if random_position: self.thinkers.append(leader(self.user_controlled_leader, self.window_middle.x * 2.0, self.window_middle.y * 2.0, max_speed, max_force, size))
        else: self.thinkers.append(leader(self.user_controlled_leader, x, y, max_speed, max_force, size, False))
        self.leader = self.thinkers[-1]
        for i in range(len(self.thinkers) - 1): self.thinkers[i].leader = self.leader
        if old_leader: self.thinkers.remove(old_leader)
    
    
    def createFollower(self, max_speed, max_force, size, random_position = True, x = 0, y = 0):
        if random_position: self.thinkers.append(follower(self.leader, self.window_middle.x * 2.0, self.window_middle.y * 2.0, max_speed, max_force, size))
        else: self.thinkers.append(follower(self.leader, x, y, max_speed, max_force, size, False))
    
    
    def calculateFrame(self):
        '''
        First lets every thinker determine their new position.
        Then lets them move to their new positions
            and also displaces them so that they are in the middle of the window.
        Then calculates the new displacement values for the next frame.
        Finally handles camera trail and its displacement.
        '''
        if not len(self.thinkers): return
        self.framecount+= 1
        if self.camera_follow: offset_vector = self.mean_position
        else: offset_vector = vector(0, 0)
        self.mean_position = vector(0, 0)
        for i in self.thinkers:
            i.think(self.thinkers)
        for i in self.thinkers:
            i.move()
            i.displace(offset_vector)
            self.mean_position+= i.pos
        self.mean_position/= len(self.thinkers)
        self.mean_position = self.window_middle - self.mean_position
        #camera movement trail and offset
        if self.framecount % 20 == 0:
            if len(self.cam_movement) == 35: self.cam_movement.pop()
        for i in range(len(self.cam_movement)): self.cam_movement[i]+= offset_vector
            #for i in self.cam_movement: i+= offset_vector
        if self.framecount % 20 == 0: self.cam_movement.insert(0, self.window_middle + self.window_middle / 3.0)
        self.cam_offset+= offset_vector
        
        