import sys
sys.path.append("../src")

import unittest
from unittest import mock
from unittest.mock import MagicMock
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

    """
        Users (Physicians) set the baseline and bolus to 0.02 and 0.2, set speed 2x, users (Patients) request bolus, nothing happened, start injection
        After 15s, users (Patients) request bolus, bolus injected successfully, after 1s, users (Patients) request bolus, 
        bolus inject failed, after 5s, reach hour limit, test show board, users (Physicians) stop injection, reset baseline, bolus rate
        and speed as 0.1, 0.5 and 4x, users (Patients) request bolus, nothing happened, users (Physicians) restart the injection, 
        until reach day limit.
    """
    def test_integration(self):
        # Set baseline 0.02
        QTest.mouseClick(self.physician_UI.button_setBaseline, Qt.LeftButton)
        QTest.qWait(1000)
        self.assertEqual(self.physician_UI.baselineRateText.window.isVisible(), True)
        self.physician_UI.baselineRateText.rateSlider.setValue(2)
        with unittest.mock.patch.object(QMessageBox, 'information', return_value=None) as mock_info:
            QTest.mouseClick(self.physician_UI.baselineRateText.confirm, Qt.LeftButton)
            mock_info.assert_called_once_with(self.physician_UI.baselineRateText.window, "Information", "Set Baseline rate successfully!", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        QTest.qWait(1000)
        self.assertEqual(GlobalValue.RT_baseline_rate, 0.02)
        
        # Set bolus 0.2
        QTest.mouseClick(self.physician_UI.button_setBolus, Qt.LeftButton)
        QTest.qWait(1000)
        self.assertEqual(self.physician_UI.bolusRateText.window.isVisible(), True)
        self.physician_UI.bolusRateText.rateSlider.setValue(20)
        with unittest.mock.patch.object(QMessageBox, 'information', return_value=None) as mock_info:
            QTest.mouseClick(self.physician_UI.bolusRateText.confirm, Qt.LeftButton)
            mock_info.assert_called_once_with(self.physician_UI.bolusRateText.window, "Information", "Set Bolus rate successfully!", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        QTest.qWait(1000)
        self.assertEqual(GlobalValue.RT_bolus_rate, 0.2)

        # Set Speed 2x
        self.physician_UI.speedRateSlider.setValue(2)
        QTest.qWait(1000)
        self.assertEqual(GlobalValue.speed, 2)

        # Request Bolus
        self.assertEqual(GlobalValue.flag_bolus, False)
        QTest.mouseClick(self.patient_UI.button_requestBolus, Qt.LeftButton)
        QTest.qWait(1000)
        self.assertEqual(GlobalValue.flag_bolus, False)

        # Start Injection
        QTest.mouseClick(self.physician_UI.button_startInjection, Qt.LeftButton)
        past = GlobalValue.RT_injection_amount
        QTest.qWait(1000)
        now = GlobalValue.RT_injection_amount
        self.assertEqual((now - past > GlobalValue.RT_bolus_rate), False)

        QTest.qWait(14000)

        # Request bolus successfully
        past = GlobalValue.RT_injection_amount
        QTest.mouseClick(self.patient_UI.button_requestBolus, Qt.LeftButton)
        QTest.qWait(1000)
        now = GlobalValue.RT_injection_amount
        self.assertEqual((now - past > GlobalValue.RT_bolus_rate), True)

        # Request bolus Failed
        past = GlobalValue.RT_injection_amount
        QTest.mouseClick(self.patient_UI.button_requestBolus, Qt.LeftButton)
        QTest.qWait(1000)
        now = GlobalValue.RT_injection_amount
        self.assertEqual((now - past > GlobalValue.RT_bolus_rate), False)

        QTest.qWait(5000)

        self.assertEqual(self.physician_UI.textBrowser.StateStatusBar.currentMessage(), "Over 1-hour Limit, Injection Failed!")

        # Stop Injection
        QTest.mouseClick(self.physician_UI.button_stopInjection, Qt.LeftButton)
        QTest.qWait(1000)

        # Set baseline 0.1
        QTest.mouseClick(self.physician_UI.button_setBaseline, Qt.LeftButton)
        QTest.qWait(1000)
        self.assertEqual(self.physician_UI.baselineRateText.window.isVisible(), True)
        self.physician_UI.baselineRateText.rateSlider.setValue(10)
        with unittest.mock.patch.object(QMessageBox, 'information', return_value=None) as mock_info:
            QTest.mouseClick(self.physician_UI.baselineRateText.confirm, Qt.LeftButton)
            mock_info.assert_called_once_with(self.physician_UI.baselineRateText.window, "Information", "Set Baseline rate successfully!", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        QTest.qWait(1000)
        self.assertEqual(GlobalValue.RT_baseline_rate, 0.1)
        
        # Set bolus 0.5
        QTest.mouseClick(self.physician_UI.button_setBolus, Qt.LeftButton)
        QTest.qWait(1000)
        self.assertEqual(self.physician_UI.bolusRateText.window.isVisible(), True)
        self.physician_UI.bolusRateText.rateSlider.setValue(50)
        with unittest.mock.patch.object(QMessageBox, 'information', return_value=None) as mock_info:
            QTest.mouseClick(self.physician_UI.bolusRateText.confirm, Qt.LeftButton)
            mock_info.assert_called_once_with(self.physician_UI.bolusRateText.window, "Information", "Set Bolus rate successfully!", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        QTest.qWait(1000)
        self.assertEqual(GlobalValue.RT_bolus_rate, 0.5)

        # Set Speed 4x
        self.physician_UI.speedRateSlider.setValue(4)
        QTest.qWait(1000)
        self.assertEqual(GlobalValue.speed, 4)

        # Request bolus Failed
        past = GlobalValue.RT_injection_amount
        QTest.mouseClick(self.patient_UI.button_requestBolus, Qt.LeftButton)
        QTest.qWait(1000)
        now = GlobalValue.RT_injection_amount
        self.assertEqual((now - past > GlobalValue.RT_bolus_rate), False)

        # Start Injection
        QTest.mouseClick(self.physician_UI.button_startInjection, Qt.LeftButton)
        past = GlobalValue.RT_injection_amount
        QTest.qWait(1000)
        now = GlobalValue.RT_injection_amount
        self.assertEqual((now - past > GlobalValue.RT_bolus_rate), False)

        QTest.qWait(30000)

        self.assertEqual(GlobalValue.RT_injection_amount, 3.0)  













if __name__ == '__main__':
    unittest.main()