import sys
sys.path.append("../src")

import unittest
from unittest import mock
from unittest.mock import MagicMock
# import ui
from PyQt5.QtWidgets import *
from PyQt5.QtTest import *
from PyQt5.QtCore import *
from ui import *

class MyTest(unittest.TestCase):

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

    # ok
    """ UseCase1: Set Baseline Rate to 0.1 """
    def test_use_case_set_baseline(self):
        QTest.mouseClick(self.physician_UI.button_setBaseline, Qt.LeftButton)
        QTest.qWait(1000)
        self.assertEqual(self.physician_UI.baselineRateText.window.isVisible(), True)
        self.physician_UI.baselineRateText.rateSlider.setValue(10)
        with unittest.mock.patch.object(QMessageBox, 'information', return_value=None) as mock_info:
            QTest.mouseClick(self.physician_UI.baselineRateText.confirm, Qt.LeftButton)
            mock_info.assert_called_once_with(self.physician_UI.baselineRateText.window, "Information", "Set Baseline rate successfully!", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        QTest.qWait(1000)
        self.assertEqual(GlobalValue.RT_baseline_rate, 0.1)
        GlobalValue.RT_baseline_rate = 0.0

    # ok
    """ UseCase2: Enter in the set-baseline-rate window but do nothing and back to the main window """
    def test_use_case_set_baseline_back(self):
        QTest.mouseClick(self.physician_UI.button_setBaseline, Qt.LeftButton)
        QTest.qWait(1000)
        self.assertEqual(self.physician_UI.baselineRateText.window.isVisible(), True)
        self.physician_UI.baselineRateText.rateSlider.setValue(10)
        QTest.mouseClick(self.physician_UI.baselineRateText.back, Qt.LeftButton)
        self.assertEqual(GlobalValue.RT_baseline_rate, 0)

    # ok
    """ UseCase3: Set Bolus Rate to 0.5 """
    def test_use_case_set_bolus(self):
        QTest.mouseClick(self.physician_UI.button_setBolus, Qt.LeftButton)
        QTest.qWait(1000)
        self.assertEqual(self.physician_UI.bolusRateText.window.isVisible(), True)
        self.physician_UI.bolusRateText.rateSlider.setValue(50)
        with unittest.mock.patch.object(QMessageBox, 'information', return_value=None) as mock_info:
            QTest.mouseClick(self.physician_UI.bolusRateText.confirm, Qt.LeftButton)
            mock_info.assert_called_once_with(self.physician_UI.bolusRateText.window, "Information", "Set Bolus rate successfully!", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        QTest.qWait(1000)
        self.assertEqual(GlobalValue.RT_bolus_rate, 0.5)
        GlobalValue.RT_bolus_rate = 0.0

    # ok
    """ UseCase4: Enter in the set-bolus-rate window but do nothing and back to the main window """
    def test_use_case_set_bolus_back(self):
        QTest.mouseClick(self.physician_UI.button_setBolus, Qt.LeftButton)
        QTest.qWait(1000)
        self.assertEqual(self.physician_UI.bolusRateText.window.isVisible(), True)
        self.physician_UI.bolusRateText.rateSlider.setValue(10)
        QTest.mouseClick(self.physician_UI.bolusRateText.back, Qt.LeftButton)
        self.assertEqual(GlobalValue.RT_bolus_rate, 0)
    
    # ok
    """ UseCase5: Start injection after setting the two rates and then stop injection """
    def test_physician_ui_start_stop_injection(self):
        GlobalValue.RT_baseline_rate = GlobalValue.minBaselineRate
        GlobalValue.RT_bolus_rate = GlobalValue.minBolusRate
        QTest.mouseClick(self.physician_UI.button_startInjection, Qt.LeftButton)
        QTest.qWait(1000)
        self.assertEqual(self.physician_UI.button_startInjection.isEnabled(), False)
        self.assertEqual(self.physician_UI.button_setBaseline.isEnabled(), False)
        self.assertEqual(self.physician_UI.button_setBolus.isEnabled(), False)
        self.assertEqual(GlobalValue.isStop, False)
        self.assertEqual(self.physician_UI.stop, False)
        QTest.mouseClick(self.physician_UI.button_stopInjection, Qt.LeftButton)
        QTest.qWait(1000)
        self.assertEqual(self.physician_UI.button_startInjection.isEnabled(), True)
        self.assertEqual(self.physician_UI.button_setBaseline.isEnabled(), True)
        self.assertEqual(self.physician_UI.button_setBolus.isEnabled(), True)
        self.assertEqual(GlobalValue.isStop, True)
        self.assertEqual(self.physician_UI.stop, True)
        GlobalValue.RT_baseline_rate = 0.0
        GlobalValue.RT_bolus_rate = 0.0

    # ok
    """ UseCase6: Start injection after setting the two rates and then request bolus and then stop injection """
    def test_physician_ui_start_request_bolus_stop_injection(self):
        GlobalValue.RT_baseline_rate = GlobalValue.minBaselineRate
        GlobalValue.RT_bolus_rate = GlobalValue.minBolusRate
        QTest.mouseClick(self.physician_UI.button_startInjection, Qt.LeftButton)
        QTest.qWait(1000)
        past = GlobalValue.RT_injection_amount
        QTest.mouseClick(self.patient_UI.button_requestBolus, Qt.LeftButton)
        QTest.qWait(2000)
        now = GlobalValue.RT_injection_amount
        self.assertEqual((now - past > GlobalValue.minBolusRate), True)
        QTest.mouseClick(self.physician_UI.button_stopInjection, Qt.LeftButton)
        QTest.qWait(1000)
        self.assertEqual(self.physician_UI.button_startInjection.isEnabled(), True)
        self.assertEqual(self.physician_UI.button_setBaseline.isEnabled(), True)
        self.assertEqual(self.physician_UI.button_setBolus.isEnabled(), True)
        self.assertEqual(GlobalValue.isStop, True)
        self.assertEqual(self.physician_UI.stop, True)
        GlobalValue.RT_baseline_rate = 0.0
        GlobalValue.RT_bolus_rate = 0.0

    # ok
    """ UseCase7: Start injection after setting the two rates and then stop injection and then request bolus """
    def test_physician_ui_start_stop_injection_request_bolus(self):
        GlobalValue.RT_baseline_rate = GlobalValue.minBaselineRate
        GlobalValue.RT_bolus_rate = GlobalValue.minBolusRate
        QTest.mouseClick(self.physician_UI.button_startInjection, Qt.LeftButton)
        QTest.qWait(1000)
        QTest.mouseClick(self.physician_UI.button_stopInjection, Qt.LeftButton)
        QTest.qWait(1000)
        self.assertEqual(self.physician_UI.button_startInjection.isEnabled(), True)
        self.assertEqual(self.physician_UI.button_setBaseline.isEnabled(), True)
        self.assertEqual(self.physician_UI.button_setBolus.isEnabled(), True)
        self.assertEqual(GlobalValue.isStop, True)
        self.assertEqual(self.physician_UI.stop, True)
        past = GlobalValue.RT_injection_amount
        QTest.mouseClick(self.patient_UI.button_requestBolus, Qt.LeftButton)
        QTest.qWait(2000)
        now = GlobalValue.RT_injection_amount
        self.assertEqual((now - past > GlobalValue.minBolusRate), False)
        GlobalValue.RT_baseline_rate = 0.0
        GlobalValue.RT_bolus_rate = 0.0

    # ok
    """ UseCase8: request bolus before starting injection, then start injection """
    def test_physician_ui_request_bolus_before_start(self):
        GlobalValue.RT_baseline_rate = GlobalValue.minBaselineRate
        GlobalValue.RT_bolus_rate = GlobalValue.minBolusRate
        self.assertEqual(GlobalValue.isStop, True)
        self.assertEqual(GlobalValue.flag_bolus, False)
        QTest.mouseClick(self.patient_UI.button_requestBolus, Qt.LeftButton)
        QTest.qWait(1000)
        self.assertEqual(GlobalValue.flag_bolus, False)
        QTest.mouseClick(self.physician_UI.button_startInjection, Qt.LeftButton)
        past = GlobalValue.RT_injection_amount
        QTest.qWait(1000)
        now = GlobalValue.RT_injection_amount
        self.assertEqual((now - past > GlobalValue.minBolusRate), False)
        GlobalValue.RT_baseline_rate = 0.0
        GlobalValue.RT_bolus_rate = 0.0
        

    # ok
    """ UseCase9: Start injection after setting the two rates and then stop injection and then reset the baseline rate """
    def test_physician_ui_start_stop_reset_baseline_rate_injection(self):
        GlobalValue.RT_baseline_rate = GlobalValue.minBaselineRate
        GlobalValue.RT_bolus_rate = GlobalValue.minBolusRate
        QTest.mouseClick(self.physician_UI.button_startInjection, Qt.LeftButton)
        QTest.qWait(1000)
        QTest.mouseClick(self.physician_UI.button_stopInjection, Qt.LeftButton)
        QTest.qWait(1000)
        QTest.mouseClick(self.physician_UI.button_setBaseline, Qt.LeftButton)
        QTest.qWait(1000)
        self.assertEqual(self.physician_UI.baselineRateText.window.isVisible(), True)
        self.physician_UI.baselineRateText.rateSlider.setValue(10)
        with unittest.mock.patch.object(QMessageBox, 'information', return_value=None) as mock_info:
            QTest.mouseClick(self.physician_UI.baselineRateText.confirm, Qt.LeftButton)
            mock_info.assert_called_once_with(self.physician_UI.baselineRateText.window, "Information", "Set Baseline rate successfully!", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        QTest.qWait(1000)
        self.assertEqual(GlobalValue.RT_baseline_rate, 0.1)
        GlobalValue.RT_baseline_rate = 0.0
        GlobalValue.RT_bolus_rate = 0.0

    # ok
    """ UseCase10: Start injection after setting the two rates and then stop injection and then reset the bolus rate """
    def test_physician_ui_start_stop_reset_bolus_rate_injection(self):
        GlobalValue.RT_baseline_rate = GlobalValue.minBaselineRate
        GlobalValue.RT_bolus_rate = GlobalValue.minBolusRate
        QTest.mouseClick(self.physician_UI.button_startInjection, Qt.LeftButton)
        QTest.qWait(1000)
        QTest.mouseClick(self.physician_UI.button_stopInjection, Qt.LeftButton)
        QTest.qWait(1000)
        QTest.mouseClick(self.physician_UI.button_setBolus, Qt.LeftButton)
        QTest.qWait(1000)
        self.assertEqual(self.physician_UI.bolusRateText.window.isVisible(), True)
        self.physician_UI.bolusRateText.rateSlider.setValue(50)
        with unittest.mock.patch.object(QMessageBox, 'information', return_value=None) as mock_info:
            QTest.mouseClick(self.physician_UI.bolusRateText.confirm, Qt.LeftButton)
            mock_info.assert_called_once_with(self.physician_UI.bolusRateText.window, "Information", "Set Bolus rate successfully!", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        QTest.qWait(1000)
        self.assertEqual(GlobalValue.RT_bolus_rate, 0.5)
        GlobalValue.RT_baseline_rate = 0.0
        GlobalValue.RT_bolus_rate = 0.0



if __name__ == '__main__':
    unittest.main()