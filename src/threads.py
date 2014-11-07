'''
Created on 6.4.2012

@author: Antti Vainio
'''

import time, threading

class runProgram(threading.Thread):
    '''
    A thread for running calculations.
    The loop also waits appropriate times to get to the requested fps.
    If the fps is set to 0 it will wait not running simulation until the fps is other than 0.
    The calculation of the delay between frames is made so that even if the calculation takes long
        it tries to get to the targeted fps by shortening the delay.
    '''
    
    def __init__(self, parent):
        super(runProgram, self).__init__()
        self.stop = False
        self.parent = parent
        
        
    def die(self):
        self.stop = True
        
        
    def run(self):
        while not self.stop:
            try:
                start_time = time.clock()
                self.parent.simulation.calculateFrame()
                self.parent.frame_times.pop()
                self.parent.frame_times.insert(0, time.clock())
                targetfps = float(self.parent.target_fps)
                if targetfps > 0: time.sleep(max(0.0, 1.0 / targetfps - time.clock() + start_time))
                while self.parent.target_fps <= 0 and not self.stop: #wait for requested fps to be other than 0
                    time.sleep(0.1)
            except:
                print "An error occurred in calculation thread!"
                
                
                
class runPaint(threading.Thread):
    '''
    A thread for drawing.
    This thread is supposed to call the paintEvent() of the GUI at regular intervals
        to get the graphics update in real time.
    The calculation of delay between frames is not as complex as for the runProgram class
        but instead the delay is constant.
    This means that if the drawing takes long the fps will get worse.
    '''
    
    def __init__(self, parent):
        super(runPaint, self).__init__()
        self.stop = False
        self.parent = parent
        
        
    def die(self):
        self.stop = True
        
        
    def run(self):
        while not self.stop:
            try:
                self.parent.update()
                time.sleep(1.0 / 20.0)
            except:
                print "An error occurred in drawing thread!"
                
                