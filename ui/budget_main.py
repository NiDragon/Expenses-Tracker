from PyQt5.Qt import (QMainWindow, QMessageBox, QFileDialog, QDoubleValidator)
from ui.ui_budget_main import Ui_MainWindow
from structs.finance_item import *

from globals import app_name
from decimal import *

# Some constants for consistency
_DAYS_IN_WEEK = 7
# Based on days in a year divided by months in a year
_DAYS_IN_MONTH = Decimal(30.417)
_DAYS_IN_YEAR = 365
_WEEKS_IN_YEAR = 52
_MONTHS_IN_YEAR = 12


# Generate and display an error message with supplied text
def err_msg(title, text):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setText(text)
    msg.setWindowTitle(title)
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()


rounding_num = Decimal(10) ** -2


def round_decimal(num: Decimal) -> Decimal:
    return num.quantize(rounding_num)


# Calculate the total costs for all categories
# These are some really rough estimates based on some serious assumptions
def build_item(item):
    match item.freq:
        case Frequency.DAILY:
            item.daily = item.cost
            item.weekly = item.daily * _DAYS_IN_WEEK
            item.monthly = item.daily * _DAYS_IN_MONTH
            item.annually = item.daily * _DAYS_IN_YEAR
        case Frequency.WEEKLY:
            item.weekly = item.cost
            item.daily = round_decimal(item.weekly / Decimal(_DAYS_IN_WEEK))
            item.monthly = item.daily * _DAYS_IN_MONTH
            item.annually = item.weekly * _WEEKS_IN_YEAR
        case Frequency.MONTHLY:
            item.monthly = item.cost
            item.daily = round_decimal(item.monthly / Decimal(_DAYS_IN_MONTH))
            item.weekly = item.daily * _DAYS_IN_WEEK
            item.annually = item.monthly * _MONTHS_IN_YEAR
        case Frequency.ANNUALLY:
            item.annually = item.cost
            item.monthly = round_decimal(item.annually / Decimal(_MONTHS_IN_YEAR))
            item.weekly = round_decimal(item.annually / Decimal(_WEEKS_IN_YEAR))
            item.daily = round_decimal(item.annually / Decimal(_DAYS_IN_YEAR))


# Display a simple about popup
def on_about():
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setText("Made using Python and Qt")
    msg.setInformativeText("A program using PyQt5 that shows tracking personal expenses.")
    msg.setDetailedText("TODO: Implement exporting to csv, xml and pdf.")
    msg.setWindowTitle(f"About - {app_name()}")
    msg.setStandardButtons(QMessageBox.Ok)
    msg.setDefaultButton(QMessageBox.Ok)
    msg.exec_()


# Main window logic class
class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.connect()
        self.ItemData = []
        self.onlyInt = QDoubleValidator()
        self.onlyInt.setDecimals(2)
        self.AItemCost.setValidator(self.onlyInt)
        self.setWindowTitle(app_name())
        self.lastSaveFile = ""

        # track unsaved changes
        self.hasChanges = False

    def on_add_item(self):
        if self.AItemName.text() == "":
            err_msg("Invalid Input!", "Name cannot be blank!")
            return

        if self.AItemCost.text() == "":
            err_msg("Invalid Input!", "Cost cannot be blank!")
            return

        item = FinanceItem()
        item.name = self.AItemName.text()

        item.cost = Decimal(self.AItemCost.text())

        item.note = self.AItemNote.text()

        if self.rbDaily.isChecked():
            item.freq = Frequency.DAILY
        elif self.rbWeekly.isChecked():
            item.freq = Frequency.WEEKLY
        elif self.rbMonthly.isChecked():
            item.freq = Frequency.MONTHLY
        elif self.rbAnnually.isChecked():
            item.freq = Frequency.ANNUALLY

        build_item(item)

        self.AItemCost.clear()
        self.AItemNote.clear()
        self.AItemName.clear()

        self.ItemData.append(item)

        # notes are optional
        if item.note != "":
            self.lbItemsBox.addItem(f'{item.name} - ${item.cost} ({item.freq.name}) Note: {item.note}')
        else:
            self.lbItemsBox.addItem(f'{item.name} - ${item.cost} ({item.freq.name})')

        self.recalc()

        self.hasChanges = True

    def recalc(self):
        daily = Decimal(0)
        weekly = Decimal(0)
        monthly = Decimal(0)
        annually = Decimal(0)

        for item in self.ItemData:
            daily += item.daily
            weekly += item.weekly
            monthly += item.monthly
            annually += item.annually

        self.DailyTotal.setText(f'${daily}')
        self.WeeklyTotal.setText(f'${weekly}')
        self.MonthlyTotal.setText(f'${monthly}')
        self.AnnualTotal.setText(f'${annually}')

        self.lbItemsBox.selectedItems().clear()

    def on_remove_item(self):
        # make sure we have a selection
        if not self.lbItemsBox.selectedItems():
            return

        selected_item = None

        for item in self.lbItemsBox.selectedItems():
            selected_item = item
            break

        index_object = self.lbItemsBox.indexFromItem(selected_item)
        index = index_object.row().__index__()

        # remove item from data and list box
        del self.ItemData[index]
        self.lbItemsBox.takeItem(index)

        self.recalc()

        self.hasChanges = True

    def save_file(self):
        file = open(self.lastSaveFile, "w+")

        file.write(f'{len(self.ItemData)}\n')

        for item in self.ItemData:
            file.write(f'{item.name}, {item.cost}, {item.freq.name}, {item.note}\n')

        file.flush()
        file.close()

        self.hasChanges = False

    def on_save_file(self):
        # nothing to save
        if len(self.ItemData) == 0:
            return

        if self.lastSaveFile == "":
            filename = QFileDialog.getSaveFileName(caption="Save Finance Data (*.fdf)",
                                                   filter="Finance Data File (*.fdf)")
            if filename[0] != "":
                self.lastSaveFile = filename[0]
                self.save_file()
        else:
            self.save_file()

    def open_file(self):
        file = open(self.lastSaveFile)

        num_entries = int(file.readline())
        for i in range(0, num_entries):
            item = FinanceItem()
            line = file.readline().strip()
            objects = line.split(",")

            if objects[0] == "":
                continue

            item.name = objects[0]
            item.cost = Decimal(objects[1])

            item.freq = Frequency[objects[2].strip()]
            item.note = objects[3].strip()

            build_item(item)

            self.ItemData.append(item)

            # notes are optional
            if item.note != "":
                self.lbItemsBox.addItem(f'{item.name} - ${item.cost} ({item.freq.name}) Note: {item.note}')
            else:
                self.lbItemsBox.addItem(f'{item.name} - ${item.cost} ({item.freq.name})')

        self.recalc()

    def on_open_file(self):
        # ask if we should proceed
        if self.hasChanges:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("There is unsaved data load anyway?")
            msg.setWindowTitle("Question")
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            if msg.exec_() == QMessageBox.No:
                return

        # remove any old data
        self.ItemData.clear()
        self.lbItemsBox.clear()
        self.hasChanges = False

        # get a file to open
        filename = QFileDialog.getOpenFileName(caption="Open Finance Data (*.fdf)",
                                               filter="Finance Data File (*.fdf)")

        # check if we got a name
        if filename[0] != 0:
            self.lastSaveFile = filename[0]
            self.open_file()

    def on_save_as(self):
        if len(self.ItemData) == 0:
            return

        filename = QFileDialog.getSaveFileName(caption="Save Finance Data (*.fdf)",
                                               filter="Finance Data File (*.fdf)")
        if filename[0] != "":
            self.lastSaveFile = filename[0]
            self.save_file()

    def connect(self):
        self.actionAbout.triggered.connect(on_about)
        self.actionOpen.triggered.connect(self.on_open_file)
        self.actionSave.triggered.connect(self.on_save_file)
        self.actionSaveAs.triggered.connect(self.on_save_as)
        self.actionExit.triggered.connect(self.close)
        self.actionAddItem.clicked.connect(self.on_add_item)
        self.actionRemoveItem.clicked.connect(self.on_remove_item)
