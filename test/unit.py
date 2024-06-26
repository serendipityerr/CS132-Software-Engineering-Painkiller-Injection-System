import sys
sys.path.append("../src")

import unittest
from unittest.mock import MagicMock
# import ui
from PyQt5.QtWidgets import *
from PyQt5.QtTest import *
from PyQt5.QtCore import *
from ui import *

class UnitTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Initialize the test environment and set class-level variables"""
        cls.app = QApplication([])

    def setUp(self):
        """Initialization of each test case"""
        self.patient_UI = Patient_UI()
        self.patient_UI.window.show()
        self.physician_UI = Physician_UI()
        self.physician_UI.window.show()
        self.physician_UI.textBrowser.window.show()
        self.physician_UI.figurePlot.window.show()
        self.physician_UI.figurePlot.plot_graph = MagicMock()
        self.physician_UI.figurePlot.pen = MagicMock()

    """ Test requestBolus() in Patient_UI """
    # ok
    def test_patient_ui_requestBolus1(self):
        GlobalValue.isStop = True
        GlobalValue.flag_bolus = False
        self.assertEqual(GlobalValue.isStop, True)
        self.assertEqual(GlobalValue.flag_bolus, False)
        self.patient_UI.requestBolus()
        self.assertEqual(GlobalValue.flag_bolus, False)
        GlobalValue.isStop = True
        GlobalValue.flag_bolus = False

    # ok
    def test_patient_ui_requestBolus2(self):
        GlobalValue.isStop = False
        self.assertEqual(GlobalValue.isStop, False)
        self.assertEqual(GlobalValue.flag_bolus, False)
        self.patient_UI.requestBolus()
        self.assertEqual(GlobalValue.flag_bolus, True)
        GlobalValue.isStop = True
        GlobalValue.flag_bolus = False



    """ Test setBaseline """
    def test_physician_ui_set_baseline(self):
        self.physician_UI.setBaseline()
        self.assertEqual(self.physician_UI.baselineRateText.window.isVisible(), True)

    """ Test setBolus """
    def test_physician_ui_set_bolus(self):
        self.physician_UI.setBolus()
        self.assertEqual(self.physician_UI.bolusRateText.window.isVisible(), True)


    """ Test speed_changed """
    # ok
    def test_physician_ui_speed(self):
        self.physician_UI.speedRateSlider.setValue(2)
        QTest.qWait(1000)
        self.assertEqual(GlobalValue.speed, 2)
        self.assertEqual(self.physician_UI.speedRateLabel2.text(), "2x")
        self.assertEqual(self.physician_UI.Timer.interval(), int(1000 / GlobalValue.speed))
        self.physician_UI.speedRateSlider.setValue(1)
    
    """ Test startInjection """
    # ok
    # all out of range
    def test_physician_ui_start_injection1(self):
        GlobalValue.RT_baseline_rate = GlobalValue.maxBaselineRate + 0.1
        GlobalValue.RT_bolus_rate = GlobalValue.maxBolusRate + 0.1
        with unittest.mock.patch.object(QMessageBox, 'warning', return_value=None) as mock_info:
            QTest.mouseClick(self.physician_UI.button_startInjection, Qt.LeftButton)
            mock_info.assert_called_once_with(self.physician_UI.window, "Warning", "Both Baseline rate and Bolus rate have not been set!", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        QTest.qWait(1000)

    # ok
    # bolus out of range
    def test_physician_ui_start_injection2(self):
        GlobalValue.RT_baseline_rate = GlobalValue.minBaselineRate
        GlobalValue.RT_bolus_rate = GlobalValue.maxBolusRate + 0.1
        with unittest.mock.patch.object(QMessageBox, 'warning', return_value=None) as mock_info:
            QTest.mouseClick(self.physician_UI.button_startInjection, Qt.LeftButton)
            mock_info.assert_called_once_with(self.physician_UI.window, "Warning", "Bolus Rate has not been set!", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        QTest.qWait(1000)

    # ok
    # baseline out of range
    def test_physician_ui_start_injection3(self):
        GlobalValue.RT_baseline_rate = GlobalValue.maxBaselineRate + 0.1
        GlobalValue.RT_bolus_rate = GlobalValue.minBolusRate
        with unittest.mock.patch.object(QMessageBox, 'warning', return_value=None) as mock_info:
            QTest.mouseClick(self.physician_UI.button_startInjection, Qt.LeftButton)
            mock_info.assert_called_once_with(self.physician_UI.window, "Warning", "Baseline Rate has not been set!", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        QTest.qWait(1000)

    # ok
    # all in the range
    def test_physician_ui_start_injection4(self):
        GlobalValue.RT_baseline_rate = GlobalValue.minBaselineRate
        GlobalValue.RT_bolus_rate = GlobalValue.minBolusRate
        self.physician_UI.startInjection()
        self.assertEqual(self.physician_UI.button_startInjection.isEnabled(), False)
        self.assertEqual(self.physician_UI.button_setBaseline.isEnabled(), False)
        self.assertEqual(self.physician_UI.button_setBolus.isEnabled(), False)
        self.assertEqual(GlobalValue.isStop, False)
        self.assertEqual(self.physician_UI.stop, False)

    # ok
    """ Test stopInjection """
    def test_physician_ui_stop_injection(self):
        self.physician_UI.stopInjection()
        self.assertEqual(self.physician_UI.button_startInjection.isEnabled(), True)
        self.assertEqual(self.physician_UI.button_setBaseline.isEnabled(), True)
        self.assertEqual(self.physician_UI.button_setBolus.isEnabled(), True)
        self.assertEqual(GlobalValue.isStop, True)
        self.assertEqual(self.physician_UI.stop, True)


    """ Test time_update in Physician_UI """
    def test_physician_ui_time_update1(self):
        # Before update
        self.physician_UI.stop = False
        last_second = self.physician_UI.second
        GlobalValue.flag_bolus = False
        GlobalValue.RT_baseline_rate = 0.1

        while GlobalValue.q.empty() == False:
            GlobalValue.q.get()
        assert GlobalValue.q.qsize() == 0

        while GlobalValue.q_day.empty() == False:
            GlobalValue.q_day.get()
        assert GlobalValue.q_day.qsize() == 0

        self.physician_UI.time_update()
        # After update
        now_second = self.physician_UI.second
        self.assertEqual(now_second-last_second, 1)
        self.assertEqual(self.physician_UI.textBrowser.StateStatusBar.currentMessage(), "Baseline Injection Successfully!")

        while GlobalValue.q.empty() == False:
            GlobalValue.q.get()
        assert GlobalValue.q.qsize() == 0

        while GlobalValue.q_day.empty() == False:
            GlobalValue.q_day.get()
        assert GlobalValue.q_day.qsize() == 0


    def test_physician_ui_time_update2(self):
        # Before update
        self.physician_UI.stop = False
        last_second = self.physician_UI.second
        GlobalValue.flag_bolus = False
        GlobalValue.RT_baseline_rate = 0.1

        while GlobalValue.q.empty() == False:
            GlobalValue.q.get()
        assert GlobalValue.q.qsize() == 0

        while GlobalValue.q_day.empty() == False:
            GlobalValue.q_day.get()
        assert GlobalValue.q_day.qsize() == 0
        
        for i in range(60):
            if i >= 50:
                GlobalValue.q.put(0.1)
            else:
                GlobalValue.q.put(0)

        for i in range(1440):
            if i >= 1430:
                GlobalValue.q_day.put(0.1)
            else:
                GlobalValue.q_day.put(0)

        self.physician_UI.time_update()
        # After update
        now_second = self.physician_UI.second
        self.assertEqual(now_second-last_second, 1)
        self.assertEqual(self.physician_UI.textBrowser.StateStatusBar.currentMessage(), "Over 1-hour Limit, Injection Failed!")

        while GlobalValue.q.empty() == False:
            GlobalValue.q.get()
        assert GlobalValue.q.qsize() == 0

        while GlobalValue.q_day.empty() == False:
            GlobalValue.q_day.get()
        assert GlobalValue.q_day.qsize() == 0

    def test_physician_ui_time_update3(self):
        # Before update
        self.physician_UI.stop = False
        last_second = self.physician_UI.second
        GlobalValue.flag_bolus = False
        GlobalValue.RT_baseline_rate = 0.1

        while GlobalValue.q.empty() == False:
            GlobalValue.q.get()
        assert GlobalValue.q.qsize() == 0

        while GlobalValue.q_day.empty() == False:
            GlobalValue.q_day.get()
        assert GlobalValue.q_day.qsize() == 0
        
        for i in range(60):
            GlobalValue.q.put(0)

        for i in range(1440):
            if i >= 1410:
                GlobalValue.q_day.put(0.1)
            else:
                GlobalValue.q_day.put(0)

        self.physician_UI.time_update()
        # After update
        now_second = self.physician_UI.second
        self.assertEqual(now_second-last_second, 1)
        self.assertEqual(self.physician_UI.textBrowser.StateStatusBar.currentMessage(), "Over 1-day Limit, Injection Failed!")

        while GlobalValue.q.empty() == False:
            GlobalValue.q.get()
        assert GlobalValue.q.qsize() == 0

        while GlobalValue.q_day.empty() == False:
            GlobalValue.q_day.get()
        assert GlobalValue.q_day.qsize() == 0
    
    def test_physician_ui_time_update4(self):
        # Before update
        self.physician_UI.stop = False
        last_second = self.physician_UI.second
        GlobalValue.flag_bolus = True
        GlobalValue.RT_baseline_rate = 0.1
        GlobalValue.RT_bolus_rate = 0.2

        while GlobalValue.q.empty() == False:
            GlobalValue.q.get()
        assert GlobalValue.q.qsize() == 0

        while GlobalValue.q_day.empty() == False:
            GlobalValue.q_day.get()
        assert GlobalValue.q_day.qsize() == 0

        self.physician_UI.time_update()
        # After update
        now_second = self.physician_UI.second
        self.assertEqual(now_second-last_second, 1)
        self.assertEqual(self.physician_UI.textBrowser.StateStatusBar.currentMessage(), "Baseline and Bolus Injection Successfully!")

        while GlobalValue.q.empty() == False:
            GlobalValue.q.get()
        assert GlobalValue.q.qsize() == 0

        while GlobalValue.q_day.empty() == False:
            GlobalValue.q_day.get()
        assert GlobalValue.q_day.qsize() == 0


    
    def test_physician_ui_time_update5(self):
        # Before update
        self.physician_UI.stop = False
        last_second = self.physician_UI.second
        GlobalValue.flag_bolus = True
        GlobalValue.RT_baseline_rate = 0.1
        GlobalValue.RT_bolus_rate = 0.2

        while GlobalValue.q.empty() == False:
            GlobalValue.q.get()
        assert GlobalValue.q.qsize() == 0

        while GlobalValue.q_day.empty() == False:
            GlobalValue.q_day.get()
        assert GlobalValue.q_day.qsize() == 0
        
        for i in range(60):
            if i >= 50:
                GlobalValue.q.put(0.1)
            else:
                GlobalValue.q.put(0)

        for i in range(1440):
            if i >= 1430:
                GlobalValue.q_day.put(0.1)
            else:
                GlobalValue.q_day.put(0)

        self.physician_UI.time_update()
        # After update
        now_second = self.physician_UI.second
        self.assertEqual(now_second-last_second, 1)
        self.assertEqual(self.physician_UI.textBrowser.StateStatusBar.currentMessage(), "Over 1-hour Limit, Injection Failed!")

        while GlobalValue.q.empty() == False:
            GlobalValue.q.get()
        assert GlobalValue.q.qsize() == 0

        while GlobalValue.q_day.empty() == False:
            GlobalValue.q_day.get()
        assert GlobalValue.q_day.qsize() == 0
          

    def test_physician_ui_time_update6(self):
        # Before update
        self.physician_UI.stop = False
        last_second = self.physician_UI.second
        GlobalValue.flag_bolus = True
        GlobalValue.RT_baseline_rate = 0.1
        GlobalValue.RT_bolus_rate = 0.2

        while GlobalValue.q.empty() == False:
            GlobalValue.q.get()
        assert GlobalValue.q.qsize() == 0

        while GlobalValue.q_day.empty() == False:
            GlobalValue.q_day.get()
        assert GlobalValue.q_day.qsize() == 0
        
        for i in range(60):
            GlobalValue.q.put(0)

        for i in range(1440):
            if i >= 1410:
                GlobalValue.q_day.put(0.1)
            else:
                GlobalValue.q_day.put(0)

        self.physician_UI.time_update()
        # After update
        now_second = self.physician_UI.second
        self.assertEqual(now_second-last_second, 1)
        self.assertEqual(self.physician_UI.textBrowser.StateStatusBar.currentMessage(), "Over 1-day Limit, Injection Failed!")

        while GlobalValue.q.empty() == False:
            GlobalValue.q.get()
        assert GlobalValue.q.qsize() == 0

        while GlobalValue.q_day.empty() == False:
            GlobalValue.q_day.get()
        assert GlobalValue.q_day.qsize() == 0


    def test_physician_ui_time_update7(self):
        # Before update
        self.physician_UI.stop = True
        last_second = self.physician_UI.second
        GlobalValue.flag_bolus = False
        GlobalValue.RT_baseline_rate = 0.1
        GlobalValue.RT_bolus_rate = 0.2

        while GlobalValue.q.empty() == False:
            GlobalValue.q.get()
        assert GlobalValue.q.qsize() == 0

        while GlobalValue.q_day.empty() == False:
            GlobalValue.q_day.get()
        assert GlobalValue.q_day.qsize() == 0
        
        self.physician_UI.time_update()
        # After update
        now_second = self.physician_UI.second
        self.assertEqual(now_second-last_second, 1)
        self.assertEqual(self.physician_UI.textBrowser.StateStatusBar.currentMessage(), "Injection Stopped!")

        while GlobalValue.q.empty() == False:
            GlobalValue.q.get()
        assert GlobalValue.q.qsize() == 0

        while GlobalValue.q_day.empty() == False:
            GlobalValue.q_day.get()
        assert GlobalValue.q_day.qsize() == 0


    def test_physician_ui_time_update8(self):
        # Before update
        self.physician_UI.stop = True
        last_second = self.physician_UI.second
        GlobalValue.flag_bolus = False
        GlobalValue.RT_baseline_rate = 0.1
        GlobalValue.RT_bolus_rate = 0.2

        while GlobalValue.q.empty() == False:
            GlobalValue.q.get()
        assert GlobalValue.q.qsize() == 0

        while GlobalValue.q_day.empty() == False:
            GlobalValue.q_day.get()
        assert GlobalValue.q_day.qsize() == 0
        
        for i in range(60):
            GlobalValue.q.put(0)

        for i in range(1440):
            GlobalValue.q_day.put(0)

        self.physician_UI.time_update()
        # After update
        now_second = self.physician_UI.second
        self.assertEqual(now_second-last_second, 1)
        self.assertEqual(self.physician_UI.textBrowser.StateStatusBar.currentMessage(), "Injection Stopped!")

        while GlobalValue.q.empty() == False:
            GlobalValue.q.get()
        assert GlobalValue.q.qsize() == 0

        while GlobalValue.q_day.empty() == False:
            GlobalValue.q_day.get()
        assert GlobalValue.q_day.qsize() == 0

    

    """ Set Rate """

    """ Test rate_changed in BolusSetRate """
    def test_physician_ui_BolusSetRate_rate_changed(self):
        self.physician_UI.bolusRateText.rate_changed()
        self.assertEqual(self.physician_UI.bolusRateText.textLabel.text(), "Bolus: " + str(float(self.physician_UI.bolusRateText.rateSlider.value()) / float(100)) + " ml/shot")

    """ Test rate_changed in BaselineSetRate """
    def test_physician_ui_BaselineSetRate_rate_changed(self):
        self.physician_UI.baselineRateText.rate_changed()
        self.assertEqual(self.physician_UI.baselineRateText.textLabel.text(), "Baseline: " + str(float(self.physician_UI.baselineRateText.rateSlider.value()) / float(100)) + " ml/min")

    
    """ Test setBolusRate confirm """
    # ok
    def test_setstate_bolus_func_confirm(self):
        self.physician_UI.setBolus()
        # QMessageBox.information(self.window, "Information", "Set Baseline rate successfully!", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        with unittest.mock.patch.object(QMessageBox, 'information', return_value=None) as mock_info:
            QTest.mouseClick(self.physician_UI.bolusRateText.confirm, Qt.LeftButton)
            mock_info.assert_called_once_with(self.physician_UI.bolusRateText.window, "Information", "Set Bolus rate successfully!", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        QTest.qWait(1000)

    """ Test setBaselineRate confirm """
    # ok
    def test_setstate_baseline_func_confirm(self): 
        self.physician_UI.setBaseline()
        # QMessageBox.information(self.window, "Information", "Set Baseline rate successfully!", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        with unittest.mock.patch.object(QMessageBox, 'information', return_value=None) as mock_info:
            QTest.mouseClick(self.physician_UI.baselineRateText.confirm, Qt.LeftButton)
            mock_info.assert_called_once_with(self.physician_UI.baselineRateText.window, "Information", "Set Baseline rate successfully!", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        QTest.qWait(1000)



    """ Test SetRate back """
    # ok
    def test_physician_ui_SetRate_back(self):
        self.physician_UI.setBaseline()
        self.physician_UI.baselineRateText.func_back()
        # QTest.mouseClick(self.physician_UI.baselineRateText.back, Qt.LeftButton)
        self.assertEqual(self.physician_UI.baselineRateText.window.isVisible(), False)

    


    """ TextBrowser """
    """ Test ShowSpeed in TextBrowser """
    def test_physician_ui_textBrowser_ShowSpeed(self):
        self.physician_UI.textBrowser.ShowSpeed()
        self.assertEqual(self.physician_UI.textBrowser.SpeedStatusBar.currentMessage(), "Speed: " + str(GlobalValue.speed) + "x")

    """ Test ShowBaseline in TextBrowser """
    def test_physician_ui_textBrowser_ShowBaseline(self):
        self.physician_UI.textBrowser.ShowBaseline()
        self.assertEqual(self.physician_UI.textBrowser.BaselineStatusBar.currentMessage(), "Baseline Rate: " + str(GlobalValue.RT_baseline_rate) + " ml/min")
    
    """ Test ShowBolus in TextBrowser """
    def test_physician_ui_textBrowser_ShowBolus(self):
        self.physician_UI.textBrowser.ShowBolus()
        self.assertEqual(self.physician_UI.textBrowser.BolusStatusBar.currentMessage(), "Bolus Rate: " + str(GlobalValue.RT_bolus_rate) + " ml/shot")

    """ Test ShowTime in TextBrowser """
    def test_physician_ui_textBrowser_ShowTime_1(self):
        self.physician_UI.textBrowser.ShowTime(1)
        self.assertEqual(self.physician_UI.textBrowser.TimeStatusBar.currentMessage(), "Pass Time: 1 minute")

    def test_physician_ui_textBrowser_ShowTime_2(self):
        self.physician_UI.textBrowser.ShowTime(2)
        self.assertEqual(self.physician_UI.textBrowser.TimeStatusBar.currentMessage(), "Pass Time: 2 minutes")

    def test_physician_ui_textBrowser_ShowTime_3(self):
        self.physician_UI.textBrowser.ShowTime(61)
        self.assertEqual(self.physician_UI.textBrowser.TimeStatusBar.currentMessage(), "Pass Time: 1 hour 1 minute")

    def test_physician_ui_textBrowser_ShowTime_4(self):
        self.physician_UI.textBrowser.ShowTime(62)
        self.assertEqual(self.physician_UI.textBrowser.TimeStatusBar.currentMessage(), "Pass Time: 1 hour 2 minutes")

    def test_physician_ui_textBrowser_ShowTime_5(self):
        self.physician_UI.textBrowser.ShowTime(121)
        self.assertEqual(self.physician_UI.textBrowser.TimeStatusBar.currentMessage(), "Pass Time: 2 hours 1 minute")

    def test_physician_ui_textBrowser_ShowTime_6(self):
        self.physician_UI.textBrowser.ShowTime(122)
        self.assertEqual(self.physician_UI.textBrowser.TimeStatusBar.currentMessage(), "Pass Time: 2 hours 2 minutes")
    
    """ Test ShowAmount in TextBrowser """
    def test_physician_ui_textBrowser_ShowAmount(self):
        self.physician_UI.textBrowser.ShowAmount(3.0)
        self.assertEqual(self.physician_UI.textBrowser.AmountStatusBar.currentMessage(), "Total injection amount: 3.0 ml")
    
    """ Test ShowShortPeriod in TextBrowser """
    def test_physician_ui_textBrowser_ShowShortPeriod(self):
        self.physician_UI.textBrowser.ShowShortPeriod(1.0)
        self.assertEqual(self.physician_UI.textBrowser.ShortPeriodStatusBar.currentMessage(), "1-Hour injection amount: 1.0 ml")

    """ Test ShowState in TextBrowser """
    # ok
    def test_physician_ui_textBrowser_ShowState_1(self):
        self.physician_UI.textBrowser.ShowState("baseline_injection_success")
        self.assertEqual(self.physician_UI.textBrowser.StateStatusBar.currentMessage(), "Baseline Injection Successfully!")

    # ok
    def test_physician_ui_textBrowser_ShowState_2(self):
        self.physician_UI.textBrowser.ShowState("bolus_injection_success")
        self.assertEqual(self.physician_UI.textBrowser.StateStatusBar.currentMessage(), "Baseline and Bolus Injection Successfully!")
        
    # ok
    def test_physician_ui_textBrowser_ShowState_3(self):
        self.physician_UI.textBrowser.ShowState("injection_failed")
        self.assertEqual(self.physician_UI.textBrowser.StateStatusBar.currentMessage(), "Over 1-hour Limit, Injection Failed!")
    
    # ok
    def test_physician_ui_textBrowser_ShowState_4(self):
        self.physician_UI.textBrowser.ShowState("Towards total amount")
        self.assertEqual(self.physician_UI.textBrowser.StateStatusBar.currentMessage(), "Over 1-day Limit, Injection Failed!")

    # ok
    def test_physician_ui_textBrowser_ShowState_5(self):
        self.physician_UI.textBrowser.ShowState("stop injection")
        self.assertEqual(self.physician_UI.textBrowser.StateStatusBar.currentMessage(), "Injection Stopped!")


    """ Figure """
    """ Test show_graph in Figure """
    def test_physician_ui_show_graph_Figure1(self):
        x_list = []
        y_list = []
        for i in range(1440):
            x_list.append(i+2)
            y_list.append(0.01)
        self.physician_UI.figurePlot.show_graph(x_list, y_list)
        self.physician_UI.figurePlot.plot_graph.setXRange.assert_called_with(x_list[0], x_list[1439])
        
    def test_physician_ui_show_graph_Figure2(self):
        x_list = []
        y_list = []
        for i in range(10):
            x_list.append(i)
            y_list.append(0.01)
        self.physician_UI.figurePlot.show_graph(x_list, y_list)
        self.physician_UI.figurePlot.plot_graph.plot.assert_called_with(x_list, y_list, pen=self.physician_UI.figurePlot.pen)


if __name__ == '__main__':
    unittest.main()