'''
Created on 16.3.2012

@author: Antti Vainio
'''

import math

class vector():
    '''
    This is a simple vector class.
    The length of a vector is calculated automagically every time x or y is modified.
    '''

    def __init__(self, x, y):
        self._x = x
        self._y = y
        self.x = x
        self.y = y
        self.updateLenght()
        
        
    def updateLenght(self):
        self.lenght = math.sqrt(self._x * self._x + self._y * self._y)
        
        
    def setX(self, value):
        self._x = value
        self.updateLenght()
    def getX(self):
        return self._x
    
    x = property(getX, setX)
    
    
    def setY(self, value):
        self._y = value
        self.updateLenght()
    def getY(self):
        return self._y
    
    y = property(getY, setY)
        
        
    def __add__(self, v):
        return vector(self.x + v.x, self.y + v.y)
    
    
    def __sub__(self, v):
        return vector(self.x - v.x, self.y - v.y)
    
    
    def __mul__(self, a):
        return vector(self.x * a, self.y * a)


    def __div__(self, a):
        if a == 0: return
        return vector(self.x / a, self.y / a)
    
    
    def __eg__(self, v):
        return self.x == v.x and self.y == v.y
    
    
    def __ne__(self, v):
        return not self == v
    
    
    def normalize(self):
        l = self.lenght
        if l == 0: return
        self.x/= l
        self.y/= l
        
        
    def clamp(self, minV, maxV):
        '''
        Clamps length.
        '''
        if self.lenght < minV or self.lenght > maxV:
            l = max(minV, min(maxV, self.lenght))
            self.normalize()
            self.x*= l
            self.y*= l
            
            
    def invert(self):
        self.x = -self.x
        self.y = -self.y
        
        