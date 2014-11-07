'''
Created on 28.2.2012

@author: Antti Vainio
'''

import sys, time
from PyQt4 import QtGui, Qt, QtCore
from simulation import simulation
from thinker import unitType
from vector import vector
from threads import runProgram, runPaint

DEFAULT_WIDTH = 800
DEFAULT_HEIGHT = 600
SIDE_BAR_WIDTH = 250
DEFAULT_FPS = 60
DEFAULT_RANDOM_AMOUNT = 10 #amount of followers when a new random simulation is created
THINKER_DEFAULT_SPEED = "1.0"
THINKER_DEFAULT_FORCE = "0.1"
THINKER_DEFAULT_SIZE = "5.0"

DEBUG = False #default drawing state


class mainWindow(QtGui.QMainWindow):
    '''
    This is the GUI class.
    
    All the GUI elements (e.g. buttons and other stuff) are put into place in initUI() function.
    
    The program is run in two threads (on top of the main thread) that are both started in __init__() function.
    One thread runs the simulation and the other updates the graphics.
    
    The visualization of the simulation along with the fps counter is updated in paintEvent() function.
    '''
    
    def __init__(self):
        try:
            super(mainWindow, self).__init__()
            #init stuff
            self.current_window_width = DEFAULT_WIDTH
            self.current_window_height = DEFAULT_HEIGHT
            self.simulation = simulation(self.current_window_width, self.current_window_height, DEFAULT_RANDOM_AMOUNT)
            self.frame_times = []
            for i in range(21): self.frame_times.append(time.clock()) #This is for the fps counter
            self.target_fps = DEFAULT_FPS
            self.old_mouse_pos = vector(0, 0)
            self.creating_leader = False
            self.creating_follower = False
            #init UI
            self.initUI()
            #start threads
            self.runThread = runProgram(self)
            self.runThread.start()
            self.paintThread = runPaint(self)
            self.paintThread.start()
        except:
            print "An error occurred in program initialization!"
            raise
        
        
    def paintEvent(self, e):
        '''
        Everything should be drawn here.
        This is also where the fps counter is updated.
        The drawing order is:
            background
            thinkers (with debug information)
            camera trail (debug)
            thinker placement mode thinker
            side bar area
        '''
        current_fps = float(len(self.frame_times) - 1) / float(self.frame_times[0] - self.frame_times[-1])
        self.fps_viewer.setText("FPS: " + str(int(current_fps)) + " / " + str(self.target_fps))
        
        painter = QtGui.QPainter()
        painter.begin(self)
        pen = QtGui.QPen(Qt.QColor(160, 160, 160))
        painter.setPen(pen)
        
        #background
        painter.setBrush(Qt.QColor(255, 255, 255))
        cam_offsetx = int(self.simulation.cam_offset.x)
        cam_offsety = int(self.simulation.cam_offset.y)
        bg_startx = cam_offsetx % 100 - 100
        bg_starty = cam_offsety % 100 - 100
        skip = bool((cam_offsetx / 100) % 2) ^ bool((cam_offsety / 100) % 2)
        for i in range(bg_starty, self.current_window_height, 100):
            skip = not skip
            skip2 = skip
            for j in range(bg_startx, self.current_window_width, 100):
                skip2 = not skip2
                if skip2:
                    painter.drawRect(j, i, 100, 100)
        painter.setBrush(QtGui.QBrush())
        
        #thinkers
        for i in self.simulation.thinkers:
            if self.dmode_debug.isChecked() or i == self.simulation.active_thinker:
                pen.setColor(Qt.QColor(0, 200, 0))
                pen.setWidth(1)
                painter.setPen(pen)
                painter.drawEllipse(i.last_seek_target.x - 2, i.last_seek_target.y - 2, 4, 4)
                painter.drawLine(i.pos.x, i.pos.y, i.last_seek_target.x, i.last_seek_target.y)
            pen.setWidth(2)
            if i.is_leader: pen.setColor(Qt.QColor(255, 0, 0))
            else: pen.setColor(Qt.QColor(0, 0, 255))
            painter.setPen(pen)
            painter.drawEllipse(i.pos.x - i.size, i.pos.y - i.size, i.size * 2.0, i.size * 2.0)
            pen.setColor(Qt.QColor(200, 0, 0))
            painter.setPen(pen)
            painter.drawLine(i.pos.x, i.pos.y, i.pos.x + i.speed.x * 15.0, i.pos.y + i.speed.y * 15.0)
        if self.simulation.thinker_near_mouse and self.simulation.thinker_near_mouse != self.simulation.active_thinker:
            i = self.simulation.thinker_near_mouse
            pen.setColor(Qt.QColor(255, 0, 0, 200))
            painter.setPen(pen)
            painter.drawEllipse(i.pos.x - i.size - 5.0, i.pos.y - i.size - 5.0, i.size * 2.0 + 10.0, i.size * 2.0 + 10.0)
        if self.simulation.active_thinker:
            i = self.simulation.active_thinker
            pen.setColor(Qt.QColor(0, 0, 255, 200))
            painter.setPen(pen)
            painter.drawEllipse(i.pos.x - i.size - 5.0, i.pos.y - i.size - 5.0, i.size * 2.0 + 10.0, i.size * 2.0 + 10.0)
            
        pen.setWidth(2)
        
        #camera trail
        if self.dmode_debug.isChecked():
            pen.setColor(Qt.QColor(0, 0, 255))
            painter.setPen(pen)
            for i in self.simulation.cam_movement: painter.drawPoint(i.x, i.y)
            
        #creation mode
        if self.old_mouse_pos.x > SIDE_BAR_WIDTH:
            if self.creating_leader:
                pen.setColor(Qt.QColor(255, 0, 0))
                painter.setPen(pen)
                painter.drawEllipse(self.old_mouse_pos.x - 5.0, self.old_mouse_pos.y - 5.0, 10.0, 10.0)
            if self.creating_follower:
                pen.setColor(Qt.QColor(0, 0, 255))
                painter.setPen(pen)
                painter.drawEllipse(self.old_mouse_pos.x - 5.0, self.old_mouse_pos.y - 5.0, 10.0, 10.0)
        
        #buttons
        pen = QtGui.QPen(Qt.QColor(255, 200, 0, 100))
        painter.setPen(pen)
        painter.setBrush(Qt.QColor(255, 200, 0, 100))
        painter.drawRect(0, 0, SIDE_BAR_WIDTH, self.current_window_height)
        
        painter.end()
        '''
        End of paintEvent()
        '''
        
        
    def stopThreads(self):
        self.runThread.die()
        self.paintThread.die()
    #program should be now quit
    def closeEvent(self, event):
        self.stopThreads()
        event.accept()
    def quitProgram(self):
        self.stopThreads()
        QtGui.qApp.quit()
        
        
    #window got resized
    def resizeEvent(self, size):
        self.current_window_width = size.size().width()
        self.current_window_height = size.size().height()
        self.simulation.setWindowSize(self.current_window_width, self.current_window_height)
        
        
    #moved mouse
    def mouseMoveEvent(self, event):
        '''
        This informs the simulation about the position of the mouse
            and moves camera around when the mid mouse button is pressed.
        '''
        #sets the mouse position to "nowhere"
        if event.x() < SIDE_BAR_WIDTH or self.creating_leader or self.creating_follower: self.simulation.setMousePosition()
        #now actually set the mouse position
        else: self.simulation.setMousePosition(event.x(), event.y())
        #move camera
        if event.buttons() & QtCore.Qt.MidButton:
            self.simulation.move_camera(event.x() - self.old_mouse_pos.x, event.y() - self.old_mouse_pos.y)
        self.old_mouse_pos = vector(event.x(), event.y())
        
        
    def mousePressEvent(self, event):
        '''
        Things that happen with mouse buttons are done here.
        Hoverer, the camera movement with mid mouse button is done in mouseMoveEvent() above.
        '''
        #create/choose a thinker
        if event.button() == QtCore.Qt.LeftButton:
            if self.creating_leader:
                if event.x() > SIDE_BAR_WIDTH:
                    self.createLeader(event.x(), event.y())
                    self.resetCreationState()
            elif self.creating_follower:
                if event.x() > SIDE_BAR_WIDTH: self.createFollower(event.x(), event.y())
            else: self.updateChosenState(self.simulation.chooseThinker())
        #remove a thinker
        elif event.button() == QtCore.Qt.RightButton:
            if self.simulation.thinker_near_mouse and not self.creating_leader and not self.creating_follower:
                self.simulation.removeThinker(self.simulation.thinker_near_mouse)
                self.clearChoose()
        #uncheck camera follow button
        elif event.button() == QtCore.Qt.MidButton:
            if self.camera_check.isChecked(): self.camera_check.click()
            
            
    def keyPressEvent(self, event):
        '''
        pressed/released keyboard key
        User's leader control is done here.
        '''
        if not self.simulation.leader: return
        if event.key() == QtCore.Qt.Key_W:
            self.setLeaderControl(True)
            self.simulation.leader.user_up = True
        if event.key() == QtCore.Qt.Key_S:
            self.setLeaderControl(True)
            self.simulation.leader.user_down = True
        if event.key() == QtCore.Qt.Key_A:
            self.setLeaderControl(True)
            self.simulation.leader.user_left = True
        if event.key() == QtCore.Qt.Key_D:
            self.setLeaderControl(True)
            self.simulation.leader.user_right = True
    def keyReleaseEvent(self, event):
        if not self.simulation.leader: return
        if event.key() == QtCore.Qt.Key_W: self.simulation.leader.user_up = False
        if event.key() == QtCore.Qt.Key_S: self.simulation.leader.user_down = False
        if event.key() == QtCore.Qt.Key_A: self.simulation.leader.user_left = False
        if event.key() == QtCore.Qt.Key_D: self.simulation.leader.user_right = False
        
        
    def setLeaderControl(self, value):
        if value:
            self.simulation.user_controlled_leader = True #new leaders will also be user controlled
            if self.simulation.leader: self.simulation.leader.user_controlled = True
            if not self.leader_check.isChecked(): self.leader_check.click()
        else:
            self.simulation.user_controlled_leader = False
            if self.simulation.leader: self.simulation.leader.user_controlled = False
            if self.leader_check.isChecked(): self.leader_check.click()
            
            
    def removeActiveUnit(self):
        '''
        Similar as in mousePressEvent().
        This one is used by the 'remove this unit' -button.
        '''
        self.simulation.removeThinker(self.simulation.active_thinker)
        self.clearChoose()
        
        
    def clearChoose(self):
        '''
        This does some important things when unit choice is cleared.
        '''
        self.simulation.thinker_near_mouse = None
        self.simulation.active_thinker = None
        self.updateChosenState(unitType.none)
        
        
    def updateAttributeTexts(self):
        if self.simulation.active_thinker:
            self.speed_text.setText("Max speed: %.3f"%self.simulation.active_thinker.max_speed)
            self.force_text.setText("Max force: %.3f"%self.simulation.active_thinker.max_force)
            self.size_text.setText("Size: %.3f"%self.simulation.active_thinker.size)
        else:
            self.speed_text.setText("Max speed: -")
            self.force_text.setText("Max force: -")
            self.size_text.setText("Size: -")
        
        
    def updateChosenState(self, unit_type):
        '''
        Something is chosen or unchosen.
        '''
        if unit_type == unitType.leader or unit_type == unitType.follower:
            self.placement_random.setDisabled(True)
            self.placement_user.setDisabled(True)
            self.leader_button.hide()
            self.follower_button.hide()
            self.attribute_button.show()
            self.remove_button.show()
            if unit_type == unitType.leader:
                self.chosen_text.setText("Chosen unit: the leader")
            elif unit_type == unitType.follower:
                self.chosen_text.setText("Chosen unit: a follower")
        else:
            self.chosen_text.setText("Chosen unit: none")
            self.placement_random.setDisabled(False)
            self.placement_user.setDisabled(False)
            self.resetCreationState()
            self.attribute_button.hide()
            self.remove_button.hide()
        self.updateAttributeTexts()
        
        
    def resetButtons(self):
        '''
        This should be called when the old simulation is discarded and a new one is created.
        This function sets the stated the buttons back to the default ones.
        However, the state of the fps slider is not set here
            because its desired state depends on whether the simulation is cleared or a new random simulation is created.
            The state is set either in clearSimulation() or in randomSimulation().
        Also the states of the draw mode or the help text are not changed.
        '''
        self.resetCreationState()
        self.attribute_button.hide()
        self.remove_button.hide()
        if not self.attr1_check.isChecked(): self.attr1_check.click()
        if not self.attr2_check.isChecked(): self.attr2_check.click()
        if not self.attr3_check.isChecked(): self.attr3_check.click()
        if self.leader_check.isChecked(): self.leader_check.click()
        if not self.camera_check.isChecked(): self.camera_check.click()
        self.attr1_line.setText(THINKER_DEFAULT_SPEED)
        self.attr2_line.setText(THINKER_DEFAULT_FORCE)
        self.attr3_line.setText(THINKER_DEFAULT_SIZE)
        self.updateChosenState(unitType.none)
        self.placement_random.click()
        
        
    def clearSimulation(self):
        self.simulation = simulation(self.current_window_width, self.current_window_height, 0)
        self.fps_slider.setValue(0)
        self.resetButtons()
        
        
    def randomSimulation(self):
        dialog = QtGui.QInputDialog()
        value, ok = dialog.getInt(self, "Random simulation", "How many followers?", DEFAULT_RANDOM_AMOUNT, 0)
        if ok:
            self.simulation = simulation(self.current_window_width, self.current_window_height, value, True)
            self.fps_slider.setValue(60)
            self.resetButtons()
        
        
    def fpsSliderEvent(self, value):
        self.target_fps = value
        
        
    def cameraFollowEvent(self, value):
        '''
        Event for 'Camera follows' -check button.
        '''
        self.simulation.camera_follow = value
        
        
    def showHelpEvent(self, value):
        '''
        Event for 'Show help' -check button.
        '''
        self.help_text.setVisible(value)
        
        
    def getThinkerAttributes(self):
        '''
        This function gives the desired attributes when a new thinker is created or an old one is modified.
        If a random value is wanted for an attribute -1 is returned.
        '''
        if self.attr1_check.isChecked(): attr1 = -1
        else: 
            try: attr1 = float(self.attr1_line.text())
            except ValueError:
                message = QtGui.QMessageBox(QtGui.QMessageBox.Warning, "Error", "Invalid value for Max speed: " + self.attr1_line.text())
                message.exec_()
                raise
        if self.attr2_check.isChecked(): attr2 = -1
        else: 
            try: attr2 = float(self.attr2_line.text())
            except ValueError:
                message = QtGui.QMessageBox(QtGui.QMessageBox.Warning, "Error", "Invalid value for Max force: " + self.attr2_line.text())
                message.exec_()
                raise
        if self.attr3_check.isChecked(): attr3 = -1
        else: 
            try: attr3 = float(self.attr3_line.text())
            except ValueError:
                message = QtGui.QMessageBox(QtGui.QMessageBox.Warning, "Error", "Invalid value for Size: " + self.attr3_line.text())
                message.exec_()
                raise
        if not (attr1 and attr2 and attr3):
            message = QtGui.QMessageBox(QtGui.QMessageBox.Warning, "Error", "Any value can't be 0")
            message.exec_()
            raise ValueError
        return attr1, attr2, attr3
    
    
    def updateThinkerAttributes(self):
        try: attr1, attr2, attr3 = self.getThinkerAttributes()
        except ValueError: return
        if attr1 < 0: self.simulation.active_thinker.randomizeMaxSpeed()
        else: self.simulation.active_thinker.max_speed = attr1
        if attr2 < 0: self.simulation.active_thinker.randomizeMaxForce()
        else: self.simulation.active_thinker.max_force = attr2
        if attr3 < 0: self.simulation.active_thinker.randomizeSize()
        else: self.simulation.active_thinker.size = attr3
        self.updateAttributeTexts()
        
        
    def resetCreationState(self):
        '''
        User stops placing new thinkers.
        '''
        self.leader_button.show()
        self.follower_button.show()
        self.leader_button.setText("Recreate leader")
        self.follower_button.setText("Create follower")
        self.creating_leader = False
        self.creating_follower = False
        
        
    '''
    These two functions are for the 'Create thinker' / 'Stop creating thinker' - buttons.
    If the user is in thinker placement mode the button will exit that mode.
    Otherwise a new thinker is created or the user is put into the thinker creation mode.
    '''
    def leaderButtonEvent(self):
        if self.creating_leader: self.resetCreationState()
        elif self.placement_user.isChecked():
            self.creating_leader = True
            self.follower_button.hide()
            self.leader_button.setText("Stop creating leader")
        else: self.createLeader()
    def followerButtonEvent(self):
        if self.creating_follower: self.resetCreationState()
        elif self.placement_user.isChecked():
            self.creating_follower = True
            self.leader_button.hide()
            self.follower_button.setText("Stop creating follower")
        else: self.createFollower()
        
        
    def createLeader(self, x = -1, y = -1):
        try: attr1, attr2, attr3 = self.getThinkerAttributes()
        except ValueError: return
        if x < 0: self.simulation.createLeader(attr1, attr2, attr3)
        else: self.simulation.createLeader(attr1, attr2, attr3, False, x, y)
    def createFollower(self, x = -1, y = -1):
        try: attr1, attr2, attr3 = self.getThinkerAttributes()
        except ValueError: return
        if x < 0: self.simulation.createFollower(attr1, attr2, attr3)
        else: self.simulation.createFollower(attr1, attr2, attr3, False, x, y)
        
        
    def initUI(self):
        '''
        This is where all the GUI elements are created.
        There is also the UIcreateAttribute() function, below this function, that creates attribute bars.
        '''
        self.setMouseTracking(True) #to get mouse tracking even when no mouse button is pressed
        self.central_widget = QtGui.QWidget(self)
        self.central_widget.setMouseTracking(True)
        self.setCentralWidget(self.central_widget)
        
        #action that creates a new empty simulation
        new_simulation_action = QtGui.QAction(QtGui.QIcon('./img/clear.png'), '&Clear simulation', self)
        new_simulation_action.setShortcut('CTRL+N')
        new_simulation_action.triggered.connect(self.clearSimulation)
        #action that creates a new random simulation
        new_random_action = QtGui.QAction(QtGui.QIcon('./img/random.png'), '&Random simulation', self)
        new_random_action.setShortcut('CTRL+R')
        new_random_action.triggered.connect(self.randomSimulation)
        #action that quits the program
        exit_action = QtGui.QAction(QtGui.QIcon('./img/exit.png'), '&Exit', self)
        exit_action.setShortcut('CTRL+Q')
        exit_action.triggered.connect(self.quitProgram)
        
        #tool bar
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('&File')
        file_menu.addAction(new_simulation_action)
        file_menu.addAction(new_random_action)
        file_menu.addAction(exit_action)
        
        #fonts
        bold_text = QtGui.QFont()
        bold_text.setBold(True)
        
        #buttons and stuff
            #layout
        main_layout = QtGui.QHBoxLayout()
        self.central_widget.setLayout(main_layout)
        self.side_bar = QtGui.QVBoxLayout()
        self.side_bar.setAlignment(QtCore.Qt.AlignTop)
        main_layout.addLayout(self.side_bar)
            #help text
        self.help_text = QtGui.QLabel(\
            "    HELP:\n" +\
            "Move mouse on a unit: highlight unit\n" +\
            "Click mouse1 on a unit: select unit\n" +\
            "Click mouse2 on a unit: remove unit\n" +\
            "Hold down mouse3: move simulation scene (disables camera follow)\n" +\
            "WSAD: control leader (enables leader control)"\
            ,self.central_widget)
        self.help_text.setMouseTracking(True) #mouse is not tracked without this on top of this widget
        help_font = QtGui.QFont()
        help_font.setPointSize(11)
        self.help_text.setFont(help_font)
        self.help_text.setAlignment(QtCore.Qt.AlignTop)
        main_layout.addWidget(self.help_text)
        main_layout.addStretch(1)
            #fps
        self.fps_viewer = QtGui.QLabel(self.central_widget)
        self.fps_viewer.setFont(bold_text)
        self.side_bar.addWidget(self.fps_viewer)
        self.fps_slider = QtGui.QSlider(QtCore.Qt.Horizontal, self.central_widget)
        self.fps_slider.setMaximumWidth(SIDE_BAR_WIDTH - 20)
        self.fps_slider.setMaximum(150)
        self.fps_slider.setValue(DEFAULT_FPS)
        self.fps_slider.valueChanged[int].connect(self.fpsSliderEvent)
        self.side_bar.addWidget(self.fps_slider)
            #control leader
        self.leader_check = QtGui.QCheckBox("Control leader", self.central_widget)
        self.leader_check.stateChanged.connect(self.setLeaderControl)
        self.side_bar.addWidget(self.leader_check)
            #camera follows
        self.camera_check = QtGui.QCheckBox("Camera follows", self.central_widget)
        self.camera_check.stateChanged.connect(self.cameraFollowEvent)
        self.side_bar.addWidget(self.camera_check)
            #show help
        help_check = QtGui.QCheckBox("Show help", self.central_widget)
        help_check.stateChanged.connect(self.showHelpEvent)
        self.side_bar.addWidget(help_check)
            #draw mode
        dmode_text = QtGui.QLabel("Draw mode:", self.central_widget)
        dmode_text.setFont(bold_text)
        self.side_bar.addWidget(dmode_text)
        dmode_buttons = QtGui.QButtonGroup(self.central_widget)
        self.dmode_normal = QtGui.QRadioButton("Normal", self.central_widget)
        self.dmode_debug = QtGui.QRadioButton("Debug", self.central_widget)
        dmode_buttons.addButton(self.dmode_normal, 0)
        dmode_buttons.addButton(self.dmode_debug, 1)
        dmode_layout = QtGui.QHBoxLayout()
        dmode_layout.addWidget(self.dmode_normal)
        dmode_layout.addWidget(self.dmode_debug)
        dmode_layout.addStretch(1)
        self.side_bar.addLayout(dmode_layout)
            #small space
        self.side_bar.addSpacerItem(QtGui.QSpacerItem(SIDE_BAR_WIDTH, 30))
            #chosen text and attributes
        self.chosen_text = QtGui.QLabel(self.central_widget)
        self.chosen_text.setFont(bold_text)
        self.side_bar.addWidget(self.chosen_text)
        self.speed_text = QtGui.QLabel(self.central_widget)
        self.side_bar.addWidget(self.speed_text)
        self.force_text = QtGui.QLabel(self.central_widget)
        self.side_bar.addWidget(self.force_text)
        self.size_text = QtGui.QLabel(self.central_widget)
        self.side_bar.addWidget(self.size_text)
            #placement
        placement_text = QtGui.QLabel("Placement:", self.central_widget)
        placement_text.setFont(bold_text)
        self.side_bar.addWidget(placement_text)
        placement_buttons = QtGui.QButtonGroup(self.central_widget)
        self.placement_random = QtGui.QRadioButton("Random", self.central_widget)
        self.placement_user = QtGui.QRadioButton("User defined", self.central_widget)
        placement_buttons.addButton(self.placement_random, 0)
        placement_buttons.addButton(self.placement_user, 1)
        placement_layout = QtGui.QHBoxLayout()
        placement_layout.addWidget(self.placement_random)
        placement_layout.addWidget(self.placement_user)
        placement_layout.addStretch(1)
        self.side_bar.addLayout(placement_layout)
            #thinker attributes
        self.attr1_line = QtGui.QLineEdit(self.central_widget)
        self.attr1_check = QtGui.QCheckBox("Randomize", self.central_widget)
        self.UIcreateAttribute("Max speed:", self.attr1_line, self.attr1_check)
        self.attr2_line = QtGui.QLineEdit(self.central_widget)
        self.attr2_check = QtGui.QCheckBox("Randomize", self.central_widget)
        self.UIcreateAttribute("Max force:", self.attr2_line, self.attr2_check)
        self.attr3_line = QtGui.QLineEdit(self.central_widget)
        self.attr3_check = QtGui.QCheckBox("Randomize", self.central_widget)
        self.UIcreateAttribute("Size:", self.attr3_line, self.attr3_check)
            #creation buttons
        self.leader_button = QtGui.QPushButton(self.central_widget)
        self.leader_button.clicked.connect(self.leaderButtonEvent)
        self.follower_button = QtGui.QPushButton(self.central_widget)
        self.follower_button.clicked.connect(self.followerButtonEvent)
        thinker_buttons = QtGui.QHBoxLayout()
        thinker_buttons.addWidget(self.leader_button)
        thinker_buttons.addWidget(self.follower_button)
        thinker_buttons.addStretch(1)
        self.side_bar.addLayout(thinker_buttons)
            #modify buttons
        self.attribute_button = QtGui.QPushButton("Update attributes", self.central_widget)
        self.attribute_button.clicked.connect(self.updateThinkerAttributes)
        self.remove_button = QtGui.QPushButton("Remove this unit", self.central_widget)
        self.remove_button.clicked.connect(self.removeActiveUnit)
        thinker_mod_buttons = QtGui.QHBoxLayout()
        thinker_mod_buttons.addWidget(self.attribute_button)
        thinker_mod_buttons.addWidget(self.remove_button)
        thinker_mod_buttons.addStretch(1)
        self.side_bar.addLayout(thinker_mod_buttons)
        
        self.resetButtons()
        if DEBUG: self.dmode_debug.click()
        else: self.dmode_normal.click()
        help_check.click()
        
        self.setGeometry(300, 50, DEFAULT_WIDTH, DEFAULT_HEIGHT)
        self.setWindowTitle("Follow the leader -simulation")
        self.show()
        
        
    def UIcreateAttribute(self, name, line, check):
        '''
        Creates an attribute bar.
        Creates a text label and places it and the given line edit bar and check box into a horizontal layout.
        '''
        attr_validator = QtGui.QDoubleValidator(self.central_widget)
        attr_validator.setBottom(0.01)
        attr1_text = QtGui.QLabel(name, self.central_widget)
        bold_text = QtGui.QFont()
        bold_text.setBold(True)
        attr1_text.setFont(bold_text)
        self.side_bar.addWidget(attr1_text)
        line.setValidator(attr_validator)
        #check.stateChanged.connect(line.setDisabled)
        check.stateChanged.connect(lambda x: line.setDisabled(x))
        layout = QtGui.QHBoxLayout()
        layout.addWidget(line)
        layout.addWidget(check)
        layout.addStretch(1)
        self.side_bar.addLayout(layout)



if __name__ == '__main__':
    try:
        app = QtGui.QApplication(sys.argv)
        window = mainWindow()
        sys.exit(app.exec_())
    except OverflowError:
        print "Overflow error!"
        raise
    except ZeroDivisionError:
        print "Division by 0!"
        raise
    except FloatingPointError:
        print "Floating point error!"
        raise
    except SystemExit:
        raise
    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise

