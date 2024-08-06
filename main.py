import sys

from PyQt5.Qt import QApplication
from ui.budget_main import MainWindow


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
