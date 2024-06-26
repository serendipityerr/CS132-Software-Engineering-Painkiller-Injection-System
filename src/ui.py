import PyQt5
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import pyqtgraph as pg
import queue


class GlobalValue:
    # Define global variables
    total_amount_limit = 3 # 3ml per day
    short_period_amount_limit = 1 # 1ml per hour
    RT_injection_amount = float(0) # real-time injection amount
    RT_baseline_rate = float(0) # real-time baseline rate
    RT_bolus_rate = float(0) # real-time bolus rate
    maxBaselineRate = 0.1 # 0.1ml per minute
    minBaselineRate = 0.01 # 0.01ml per minute
    maxBolusRate = 0.5 # 0.5ml per shot
    minBolusRate = 0.2 # 0.2ml per shot
    startTime = 0 # initialize
    endTime = 0 # initialize
    flag_bolus = False
    q = queue.Queue()
    second = 0 # initialize second
    speed = 1 # initialize speed
    isStop = True
    q_day = queue.Queue()
    day_amount_queue = queue.Queue()
    time_queue = queue.Queue()

class Patient_UI():
    def __init__(self):
        self.window = QMainWindow()
        self.window.resize(400,300)
        self.window.move(200,200)
        self.window.setWindowTitle("Patient")
        self.window.setWindowIcon(QIcon("./icon/patient.png"))

        # button_requestBolus
        self.button_requestBolus = QPushButton("Request Bolus", self.window)
        self.button_requestBolus.move(130,120)
        self.button_requestBolus.resize(150,30)
        self.button_requestBolus.clicked.connect(self.requestBolus)
    
    def requestBolus(self):
        global GlobalValue
        if GlobalValue.isStop == False: # Tcover 1.1.1.1
            GlobalValue.flag_bolus = True
            # print("requestBolus")
        else: # Tcover 1.1.1.2
            return


class Physician_UI():
    def __init__(self):

        # main window
        self.window = QMainWindow()
        self.window.resize(600,400)
        self.window.move(700,100)
        self.window.setWindowTitle("Physician")
        self.window.setWindowIcon(QIcon("./icon/physician.png"))

        self.bolusRateLabel = QLabel(self.window)
        self.bolusRateLabel.setText("Bolus Rate: NaN ml/shot")
        self.bolusRateLabel.move(325,210)
        self.bolusRateLabel.resize(300,30)

        self.baselineRateLabel = QLabel(self.window)
        self.baselineRateLabel.setText("Baseline Rate: NaN ml/min")
        self.baselineRateLabel.move(65,210)
        self.baselineRateLabel.resize(300,30)

        self.textBrowser = TextBrowser()

        self.figurePlot = FigurePlot()

        # set baseline rate text editor
        self.baselineRateText = SetRate("Baseline Rate", self.baselineRateLabel, self.textBrowser)

        # set baseline rate text editor
        self.bolusRateText = SetRate("Bolus Rate", self.bolusRateLabel, self.textBrowser)

        self.speedRateLabel1 = QLabel("Set your Speed Rate Here", self.window)
        self.speedRateLabel1.move(195,50)
        self.speedRateLabel1.resize(250,30)
        self.speedRateLabel1.setToolTip("n Speed Rate means 1 second in real world equals to n minutes in simulated time")

        self.speedRateLabel2 = QLabel("1x", self.window)
        self.speedRateLabel2.move(450,85)
        self.speedRateLabel2.resize(60,30)
        self.speedRateLabel2.setToolTip("n Speed Rate means 1 second in real world equals to n minutes in simulated time")

        # set speed rate text editor
        self.speedRateSlider = QSlider(Qt.Horizontal, self.window)
        self.speedRateSlider.setMinimum(1)
        self.speedRateSlider.setMaximum(10)
        self.speedRateSlider.setSingleStep(1)
        self.speedRateSlider.setValue(1)
        self.speedRateSlider.move(200,85)
        self.speedRateSlider.resize(200,30)
        self.speedRateSlider.setTickPosition(QSlider.TicksBelow)
        self.speedRateSlider.setTickInterval(1)
        self.speedRateSlider.valueChanged.connect(self.speed_changed)
        self.speedRateSlider.setToolTip("n Speed Rate means 1 second in real world equals to n minutes in simulated time")

        # button_setBaseline
        self.button_setBaseline = QPushButton(" Set Baseline", self.window)
        self.button_setBaseline.move(95,150)
        self.button_setBaseline.resize(160,40)
        self.button_setBaseline.clicked.connect(self.setBaseline)
        self.button_setBaseline.setIcon(QIcon("./icon/setting.png"))

        # button_setBolus
        self.button_setBolus = QPushButton(" Set Bolus", self.window)
        self.button_setBolus.move(350,150)
        self.button_setBolus.resize(150,40)
        self.button_setBolus.clicked.connect(self.setBolus)
        self.button_setBolus.setIcon(QIcon("./icon/setting.png"))

        # button_startInjection
        self.button_startInjection = QPushButton("Start Injection", self.window) # start baseline injection
        self.button_startInjection.move(95,270)
        self.button_startInjection.resize(160,40)
        self.button_startInjection.clicked.connect(self.startInjection)

        # button_stopInjection
        self.button_stopInjection = QPushButton("Stop Injection", self.window) # start baseline injection
        self.button_stopInjection.move(345,270)
        self.button_stopInjection.resize(160,40)
        self.button_stopInjection.clicked.connect(self.stopInjection)

        # Timer
        self.Timer = QTimer(self.window)
        self.Timer.timeout.connect(self.time_update)

        self.second = 0
        self.stop = True

    def setBaseline(self):
        self.baselineRateText.window.show() # Statement Tcover 1.2.1.1
        # print("setBaseline")

    def setBolus(self):
        self.bolusRateText.window.show() # Statement Tcover 1.2.2.1
        # print("setBolus")

    def speed_changed(self):
        global GlobalValue # Statement Tcover1.2.3.1
        GlobalValue.speed = self.speedRateSlider.value()
        # print(GlobalValue.speed)
        self.speedRateLabel2.setText(str(GlobalValue.speed) + "x")
        self.textBrowser.ShowSpeed()
        self.Timer.setInterval(int(1000 / GlobalValue.speed))

    def startInjection(self):
        global GlobalValue
        if (GlobalValue.RT_bolus_rate < GlobalValue.minBolusRate or GlobalValue.RT_bolus_rate > GlobalValue.maxBolusRate) and (GlobalValue.RT_baseline_rate < GlobalValue.minBaselineRate or GlobalValue.RT_baseline_rate > GlobalValue.maxBaselineRate): # Branch Tcover1.2.4.1
            # print("Both Baseline rate and Bolus rate have not been set!")
            QMessageBox.warning(self.window, "Warning", "Both Baseline rate and Bolus rate have not been set!", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            return
        elif (GlobalValue.RT_bolus_rate < GlobalValue.minBolusRate or GlobalValue.RT_bolus_rate > GlobalValue.maxBolusRate) and (GlobalValue.RT_baseline_rate >= GlobalValue.minBaselineRate and GlobalValue.RT_baseline_rate <= GlobalValue.maxBaselineRate): # Branch Tcover1.2.4.2
            # print("Bolus Rate has not been set!")
            QMessageBox.warning(self.window, "Warning", "Bolus Rate has not been set!", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            return
        elif (GlobalValue.RT_bolus_rate >= GlobalValue.minBolusRate and GlobalValue.RT_bolus_rate <= GlobalValue.maxBolusRate) and (GlobalValue.RT_baseline_rate < GlobalValue.minBaselineRate or GlobalValue.RT_baseline_rate > GlobalValue.maxBaselineRate): # Branch Tcover1.2.4.3
            # print("Baseline Rate has not been set!")
            QMessageBox.warning(self.window, "Warning", "Baseline Rate has not been set!", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            return
        self.button_startInjection.setEnabled(False) # Branch Tcover1.2.4.4
        self.button_setBaseline.setEnabled(False)
        self.button_setBolus.setEnabled(False)
        self.textBrowser.window.show()
        self.figurePlot.window.show()
        GlobalValue.isStop = False
        self.stop = False
        self.Timer.start(int(1000 / GlobalValue.speed))
        #print("startInjection")
        
    def stopInjection(self):
        self.stop = True # Statement Tcover1.2.5.1
        GlobalValue.isStop = True
        self.button_startInjection.setEnabled(True)
        self.button_setBaseline.setEnabled(True)
        self.button_setBolus.setEnabled(True)
        # print("stopInjection")

    def time_update(self):
        global GlobalValue
        if self.stop == False: # Branch Tcover1.2.6.1
            RT_short_period_injection_amount = float(0)
            RT_one_day_injection_amount = float(0)
            self.second += 1
            # print("Since starting, it past %d second"% self.second)
            self.textBrowser.ShowTime(str(self.second))
            # print("flag_bolus: " + str(GlobalValue.flag_bolus))
            if GlobalValue.flag_bolus == False: # didn't request bolus # Branch Tcover1.2.6.2
                
                if GlobalValue.q.qsize() == 60: # Branch Tcover1.2.6.3
                    GlobalValue.q.get()

                if GlobalValue.q_day.qsize() == 1440: # Branch Tcover1.2.6.4
                    GlobalValue.q_day.get()
                    GlobalValue.day_amount_queue.get()
                    GlobalValue.time_queue.get()

                GlobalValue.RT_injection_amount = round(GlobalValue.RT_injection_amount + GlobalValue.RT_baseline_rate,2)

                RT_short_period_injection_amount = round(RT_short_period_injection_amount + GlobalValue.RT_baseline_rate,2)
                RT_one_day_injection_amount = round(RT_one_day_injection_amount + GlobalValue.RT_baseline_rate,2)
                queueList = list(GlobalValue.q.queue)
                q_dayList = list(GlobalValue.q_day.queue)
                
                for i in range(len(queueList)): 
                    RT_short_period_injection_amount = round(RT_short_period_injection_amount + queueList[i],2)

                for i in range(len(q_dayList)): 
                    RT_one_day_injection_amount = round(RT_one_day_injection_amount + q_dayList[i],2)

                # print("RT_one_day_injection_amount: " + str(RT_one_day_injection_amount))
                
                if RT_short_period_injection_amount > GlobalValue.short_period_amount_limit or RT_one_day_injection_amount > GlobalValue.total_amount_limit: # Branch Tcover1.2.6.5
                    if RT_short_period_injection_amount > GlobalValue.short_period_amount_limit: # Branch Tcover1.2.6.6
                        # print("Towards one hour limit")
                        self.textBrowser.ShowState("injection_failed")
                    if RT_one_day_injection_amount > GlobalValue.total_amount_limit: # Branch Tcover1.2.6.7
                        # print("Towards one day limit")
                        self.textBrowser.ShowState("Towards total amount")
                    GlobalValue.RT_injection_amount = round(GlobalValue.RT_injection_amount - GlobalValue.RT_baseline_rate,2)
                    RT_short_period_injection_amount = round(RT_short_period_injection_amount - GlobalValue.RT_baseline_rate,2)
                    RT_one_day_injection_amount = round(RT_one_day_injection_amount - GlobalValue.RT_baseline_rate,2)
                    GlobalValue.q.put(float(0))
                    GlobalValue.q_day.put(float(0))
                    GlobalValue.day_amount_queue.put(RT_one_day_injection_amount)
                    GlobalValue.time_queue.put(self.second)
                else: # Branch Tcover1.2.6.8
                    GlobalValue.q.put(GlobalValue.RT_baseline_rate)
                    GlobalValue.q_day.put(GlobalValue.RT_baseline_rate)
                    GlobalValue.day_amount_queue.put(RT_one_day_injection_amount)
                    GlobalValue.time_queue.put(self.second)
                    self.textBrowser.ShowState("baseline_injection_success")

                q_day_amount_queue_list = list(GlobalValue.day_amount_queue.queue)
                q_time_queue_list = list(GlobalValue.time_queue.queue)
                self.figurePlot.show_graph(q_time_queue_list, q_day_amount_queue_list)
                # print("RT_injection_amount: " + str(RT_one_day_injection_amount))
                # print("RT_short_period_injection_amount: " + str(RT_short_period_injection_amount))
                self.textBrowser.ShowAmount(str(RT_one_day_injection_amount))
                self.textBrowser.ShowShortPeriod(str(RT_short_period_injection_amount))

                # print(len(list(GlobalValue.q.queue)))
                # print(list(GlobalValue.q.queue))
                # print("----------------------------------------------------------------")
            else: # request bolus # Branch Tcover1.2.6.9
                GlobalValue.flag_bolus = False

                if GlobalValue.q.qsize() == 60: # Branch Tcover1.2.6.10
                    GlobalValue.q.get()

                if GlobalValue.q_day.qsize() == 1440: # Branch Tcover1.2.6.11
                    GlobalValue.q_day.get()
                    GlobalValue.day_amount_queue.get()
                    GlobalValue.time_queue.get()

                GlobalValue.RT_injection_amount = round(GlobalValue.RT_injection_amount + GlobalValue.RT_baseline_rate + GlobalValue.RT_bolus_rate,2)

                RT_short_period_injection_amount = round(RT_short_period_injection_amount + GlobalValue.RT_baseline_rate + GlobalValue.RT_bolus_rate,2)
                RT_one_day_injection_amount = round(RT_one_day_injection_amount + GlobalValue.RT_baseline_rate + GlobalValue.RT_bolus_rate,2)
                queueList = list(GlobalValue.q.queue)
                q_dayList = list(GlobalValue.q_day.queue)
                
                for i in range(len(queueList)): 
                    RT_short_period_injection_amount = round(RT_short_period_injection_amount + queueList[i],2)

                for i in range(len(q_dayList)): 
                    RT_one_day_injection_amount = round(RT_one_day_injection_amount + q_dayList[i],2)
                

                if RT_short_period_injection_amount > GlobalValue.short_period_amount_limit or RT_one_day_injection_amount > GlobalValue.total_amount_limit: # Branch Tcover1.2.6.12
                    if RT_short_period_injection_amount > GlobalValue.short_period_amount_limit: # Branch Tcover1.2.6.13
                        # print("Towards one hour limit")
                        self.textBrowser.ShowState("injection_failed")
                    if RT_one_day_injection_amount > GlobalValue.total_amount_limit: # Branch Tcover1.2.6.14
                        # print("Towards one day limit")
                        self.textBrowser.ShowState("Towards total amount")
                    GlobalValue.RT_injection_amount = round(GlobalValue.RT_injection_amount - (GlobalValue.RT_baseline_rate + GlobalValue.RT_bolus_rate),2)
                    RT_short_period_injection_amount = round(RT_short_period_injection_amount - (GlobalValue.RT_baseline_rate + GlobalValue.RT_bolus_rate),2)
                    RT_one_day_injection_amount = round(RT_one_day_injection_amount - (GlobalValue.RT_baseline_rate + GlobalValue.RT_bolus_rate),2)
                    GlobalValue.q.put(float(0))
                    GlobalValue.q_day.put(float(0))
                    GlobalValue.day_amount_queue.put(RT_one_day_injection_amount)
                    GlobalValue.time_queue.put(self.second)
                    
                else: # Branch Tcover1.2.6.15
                    GlobalValue.q.put(GlobalValue.RT_baseline_rate + GlobalValue.RT_bolus_rate)
                    GlobalValue.q_day.put(GlobalValue.RT_baseline_rate + GlobalValue.RT_bolus_rate)
                    GlobalValue.day_amount_queue.put(RT_one_day_injection_amount)
                    GlobalValue.time_queue.put(self.second)
                    self.textBrowser.ShowState("bolus_injection_success")

                q_day_amount_queue_list = list(GlobalValue.day_amount_queue.queue)
                q_time_queue_list = list(GlobalValue.time_queue.queue)
                self.figurePlot.show_graph(q_time_queue_list, q_day_amount_queue_list)
                # print("RT_injection_amount: " + str(RT_one_day_injection_amount))
                # print("RT_short_period_injection_amount: " + str(RT_short_period_injection_amount))
                self.textBrowser.ShowAmount(str(RT_one_day_injection_amount))
                self.textBrowser.ShowShortPeriod(str(RT_short_period_injection_amount))
                
                # print(len(list(GlobalValue.q.queue)))
                # print(list(GlobalValue.q.queue))
                # print("----------------------------------------------------------------")
        else: # Branch Tcover1.2.6.16
            RT_short_period_injection_amount = float(0)
            RT_one_day_injection_amount = float(0)
            self.second += 1
            # print("Since starting, it past %d second"% self.second)
            self.textBrowser.ShowTime(str(self.second))
            # print("flag_bolus: " + str(GlobalValue.flag_bolus))
            if GlobalValue.q.qsize() == 60: # Branch Tcover1.2.6.17
                GlobalValue.q.get()
                
            if GlobalValue.q_day.qsize() == 1440: # Branch Tcover1.2.6.18
                GlobalValue.q_day.get()
                GlobalValue.day_amount_queue.get()
                GlobalValue.time_queue.get()

            queueList = list(GlobalValue.q.queue)
            q_dayList = list(GlobalValue.q_day.queue)
            
            for i in range(len(queueList)): 
                RT_short_period_injection_amount = round(RT_short_period_injection_amount + queueList[i],2)
                
            for i in range(len(q_dayList)): 
                RT_one_day_injection_amount = round(RT_one_day_injection_amount + q_dayList[i],2)
            
            GlobalValue.q.put(float(0))
            GlobalValue.q_day.put(float(0))
            GlobalValue.day_amount_queue.put(RT_one_day_injection_amount)
            GlobalValue.time_queue.put(self.second)
            # print("Stop Injection")
            self.textBrowser.ShowState("stop injection")

            q_day_amount_queue_list = list(GlobalValue.day_amount_queue.queue)
            q_time_queue_list = list(GlobalValue.time_queue.queue)
            self.figurePlot.show_graph(q_time_queue_list, q_day_amount_queue_list)
            # print("RT_injection_amount: " + str(RT_one_day_injection_amount))
            # print("RT_short_period_injection_amount: " + str(RT_short_period_injection_amount))
            self.textBrowser.ShowAmount(str(RT_one_day_injection_amount))
            self.textBrowser.ShowShortPeriod(str(RT_short_period_injection_amount))
            
            # print(len(list(GlobalValue.q.queue)))
            # print(list(GlobalValue.q.queue))
            # print("----------------------------------------------------------------")

       
class SetRate():
    def __init__(self, name, label, textBrowser):
        self.name = name # use for judging setting bolus rate or baseline rate
        # main window
        self.window = QMainWindow()
        self.window.resize(600,400)
        self.window.move(200,200)
        self.window.setWindowTitle(name + " Setting")
        self.window.setWindowIcon(QIcon("./icon/setting.png"))

        self.label = label

        if self.name == "Bolus Rate":
            self.textLabel = QLabel("Bolus: NaN ml/shot", self.window)
            self.textLabel.resize(200,30)
            self.textLabel.move(220,150)
            self.textLabel.setToolTip("0.2 <= Bolus <= 0.5")
        if self.name == "Baseline Rate":
            self.textLabel = QLabel("Baseline: NaN ml/min", self.window)
            self.textLabel.resize(200,30)
            self.textLabel.move(210,150)
            self.textLabel.setToolTip("0.01 <= Baseline <= 0.1")
        
        self.confirm = QPushButton("Confirm", self.window)
        self.confirm.move(140,230)
        self.confirm.resize(130,30)
        self.confirm.clicked.connect(self.func_confirm)

        self.back = QPushButton("Back", self.window)
        self.back.move(340,230)
        self.back.resize(130,30)
        self.back.clicked.connect(self.func_back)

        self.rateSlider = QSlider(Qt.Horizontal, self.window)
        self.rateSlider.setSingleStep(1)
        self.rateSlider.setTickPosition(QSlider.TicksBelow)
        self.rateSlider.setTickInterval(1)
        self.rateSlider.valueChanged.connect(self.rate_changed)
        if self.name == "Bolus Rate":
            self.rateSlider.move(150,100)
            self.rateSlider.resize(300,30)
            self.rateSlider.setMinimum(20)
            self.rateSlider.setMaximum(50)
            self.rateSlider.setValue(20)
            self.rateSlider.setToolTip("0.2 <= Bolus <= 0.5")
        if self.name == "Baseline Rate":
            self.rateSlider.move(200,100)
            self.rateSlider.resize(200,30)
            self.rateSlider.setMinimum(1)
            self.rateSlider.setMaximum(10)
            self.rateSlider.setValue(1)
            self.rateSlider.setToolTip("0.01 <= Baseline <= 0.1")

        self.textBrowser = textBrowser

    def rate_changed(self):
        if self.name == "Bolus Rate": # Branch Tcover1.3.1.1
            val = float(self.rateSlider.value()) / float(100)
            self.textLabel.setText("Bolus: " + str(val) + " ml/shot")
            
        if self.name == "Baseline Rate": # Branch Tcover1.3.1.2
            val = float(self.rateSlider.value()) / float(100)
            self.textLabel.setText("Baseline: " + str(val) + " ml/min")
            
    def func_confirm(self):
        newRate = float(self.rateSlider.value()) / float(100)
        global GlobalValue
        # Consider different situations
        if self.name == "Bolus Rate": # Branch Tcover1.3.2.1
            QMessageBox.information(self.window, "Information", "Set Bolus rate successfully!", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            GlobalValue.RT_bolus_rate = newRate
            self.textBrowser.ShowBolus()
            self.label.setText("Bolus Rate: " + str(newRate) + " ml/shot")
            self.window.close()
        if self.name == "Baseline Rate": # Branch Tcover1.3.2.2
            QMessageBox.information(self.window, "Information", "Set Baseline rate successfully!", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            GlobalValue.RT_baseline_rate = newRate
            self.textBrowser.ShowBaseline()
            self.label.setText("Baseline Rate: " + str(newRate) + " ml/min")
            self.window.close()

    def func_back(self):
        self.window.close() # Statement Tcover 1.3.3.1


# TextBrowser for showing real-time information after starting injection
class TextBrowser():
    def __init__(self):
        global GlobalValue
        self.window = QMainWindow()
        self.window.resize(800,600)
        self.window.move(150,650)
        self.window.setWindowTitle("Show")
        self.window.setWindowIcon(QIcon("./icon/display.png"))

        self.SpeedStatusBar = QStatusBar(self.window)
        self.SpeedStatusBar.resize(400,25)
        self.SpeedStatusBar.move(230,80)
        self.SpeedStatusBar.showMessage("Speed: " + str(GlobalValue.speed) + "x")
        self.SpeedStatusBar.setFont(QFont('Times', 11))
        self.SpeedStatusBar.setSizeGripEnabled(False)
        self.SpeedStatusBar.setToolTip("nx Speed Rate means 1 second in real world equals to n minutes in simulated time")

        self.BaselineStatusBar = QStatusBar(self.window)
        self.BaselineStatusBar.resize(400,25)
        self.BaselineStatusBar.move(230,140)
        self.BaselineStatusBar.showMessage("Baseline Rate: NaN ml/min")
        self.BaselineStatusBar.setFont(QFont('Times', 11)) 
        self.BaselineStatusBar.setSizeGripEnabled(False)

        self.BolusStatusBar = QStatusBar(self.window)
        self.BolusStatusBar.resize(400,25)
        self.BolusStatusBar.move(230,200)
        self.BolusStatusBar.showMessage("Bolus Rate: NaN ml/min")
        self.BolusStatusBar.setFont(QFont('Times', 11)) 
        self.BolusStatusBar.setSizeGripEnabled(False)

        self.TimeStatusBar = QStatusBar(self.window)
        self.TimeStatusBar.resize(400,25)
        self.TimeStatusBar.move(230,260)
        #self.TimeStatusBar.showMessage("Pass Time: "+str(100)+" minutes")
        self.TimeStatusBar.setFont(QFont('Times', 11)) 
        self.TimeStatusBar.setSizeGripEnabled(False)

        self.AmountStatusBar = QStatusBar(self.window)
        self.AmountStatusBar.resize(400,25)
        self.AmountStatusBar.move(230,320)
        #self.AmountStatusBar.showMessage("Total injection amount: "+str(2.0)+" ml")
        self.AmountStatusBar.setFont(QFont('Times', 11)) 
        self.AmountStatusBar.setSizeGripEnabled(False)

        self.ShortPeriodStatusBar = QStatusBar(self.window)
        self.ShortPeriodStatusBar.resize(400,25)
        self.ShortPeriodStatusBar.move(230,380)
        #self.ShortPeriodStatusBar.showMessage("1-Hour injection amount: "+str(1.0)+" ml")
        self.ShortPeriodStatusBar.setFont(QFont('Times', 11)) 
        self.ShortPeriodStatusBar.setSizeGripEnabled(False)

        self.StateStatusBar = QStatusBar(self.window)
        self.StateStatusBar.resize(500,25)
        self.StateStatusBar.move(230,440)
        self.StateStatusBar.setFont(QFont('Times', 11)) 
        self.StateStatusBar.setSizeGripEnabled(False)

    def ShowSpeed(self):
        global GlobalValue # Statement Tcover1.4.1.1
        self.SpeedStatusBar.showMessage("Speed: " + str(GlobalValue.speed) + "x")
    
    def ShowBaseline(self): # Statement Tcover1.4.2.1
        global GlobalValue
        self.BaselineStatusBar.showMessage("Baseline Rate: " + str(GlobalValue.RT_baseline_rate) + " ml/min")
    
    def ShowBolus(self):
        global GlobalValue # Statement Tcover1.4.3.1
        self.BolusStatusBar.showMessage("Bolus Rate: " + str(GlobalValue.RT_bolus_rate) + " ml/shot")

    def ShowTime(self, second):
        if int(second) == 1: # Branch Tcover1.4.4.1
            self.TimeStatusBar.showMessage("Pass Time: " + str(second) + " minute")
        elif int(second) >= 2 and int(second) < 60: # Branch Tcover1.4.4.2
            self.TimeStatusBar.showMessage("Pass Time: " + str(second) + " minutes")
        elif int(second) >= 60: # Branch Tcover1.4.4.3
            hour = int(int(second) / 60)
            sec = int(second) - hour * 60
            if hour == 1: # Branch Tcover1.4.4.4
                if sec == 1: # Branch Tcover1.4.4.5
                    self.TimeStatusBar.showMessage("Pass Time: "+ str(hour) + " hour " + str(sec) + " minute")
                else: # Branch Tcover1.4.4.6
                    self.TimeStatusBar.showMessage("Pass Time: "+ str(hour) + " hour " + str(sec) + " minutes")
            else: # Branch Tcover1.4.4.7
                if sec == 1: # Branch Tcover1.4.4.8
                    self.TimeStatusBar.showMessage("Pass Time: "+ str(hour) + " hours " + str(sec) + " minute")
                else: # Branch Tcover1.4.4.9
                    self.TimeStatusBar.showMessage("Pass Time: "+ str(hour) + " hours " + str(sec) + " minutes")
        QApplication.processEvents()

    def ShowAmount(self, amount):
        self.AmountStatusBar.showMessage("Total injection amount: "+str(amount)+" ml") # Statement Tcover1.4.5.1
        QApplication.processEvents()

    def ShowShortPeriod(self, shortPeriod):
        self.ShortPeriodStatusBar.showMessage("1-Hour injection amount: "+str(shortPeriod)+" ml") # Statement Tcover1.4.6.1
        QApplication.processEvents()

    def ShowState(self, state):
        global GlobalValue
        if state == "baseline_injection_success": # Branch Tcover1.4.7.1
            self.StateStatusBar.showMessage("Baseline Injection Successfully!")
        if state == "bolus_injection_success": # Branch Tcover1.4.7.2
            self.StateStatusBar.showMessage("Baseline and Bolus Injection Successfully!")
        if state == "injection_failed": # Branch Tcover1.4.7.3
            self.StateStatusBar.showMessage("Over 1-hour Limit, Injection Failed!")
        if state == "Towards total amount": # Branch Tcover1.4.7.4
            self.StateStatusBar.showMessage("Over 1-day Limit, Injection Failed!")
        if state == "stop injection": # Branch Tcover1.4.7.5
            self.StateStatusBar.showMessage("Injection Stopped!")

class FigurePlot():
    def __init__(self):
        self.window = QMainWindow()
        self.window.setWindowTitle("Displaying")
        self.window.resize(1500,800)
        self.window.move(1000,600)
        self.window.setWindowIcon(QIcon("./icon/figure.png"))

        self.plot_graph = pg.PlotWidget()
        self.plot_graph.setBackground("w")
        self.plot_graph.addLegend()

        self.window.setCentralWidget(self.plot_graph)
        # self.pen = pg.mkPen(color=(255, 0, 0), width=5)
        self.pen = pg.mkPen(color=(255, 0, 0))
        self.imaginal_line_pen = pg.mkPen(color=(0, 0, 255), style=Qt.DashLine)
        self.imaginal_line_x = [0,1e6]
        self.imaginal_line_y = [3,3]

        self.plot_graph.setLabel("left", "Total Injection Amount (ml)")
        self.plot_graph.setLabel("bottom", "Time (min)")
        self.plot_graph.setXRange(0,1440)
        self.plot_graph.setYRange(0,3)
        self.plot_graph.setTitle("Total Injection Amount vs Time")

        self.plot_graph.plot(self.imaginal_line_x, self.imaginal_line_y, pen=self.imaginal_line_pen)
        # self.window.show()

    def show_graph(self, x_list, y_list):
        if len(x_list) >= 1440: # Branch Tcover1.5.1.1
            self.plot_graph.setXRange(x_list[0],x_list[1439])
            self.plot_graph.plot(x_list, y_list, pen=self.pen)
        else: # Branch Tcover1.5.1.2
            self.plot_graph.plot(x_list, y_list, pen=self.pen)



if __name__=="__main__":
    app = QApplication([])
    UI_patient = Patient_UI()
    UI_physician = Physician_UI()
    UI_patient.window.show()
    UI_physician.window.show()
    app.exec_()