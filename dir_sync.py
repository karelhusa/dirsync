import glob
import sys

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QTreeView, QWidget, QVBoxLayout, QDirModel, QHBoxLayout, \
    QListView, QPushButton, QLabel, QLineEdit, QMessageBox
from PyQt5.QtGui import QStandardItem, QStandardItemModel, QIntValidator
from shutil import copyfile, move
from pathlib import Path
import datetime as dt

import os


def get_files(dir, last_days=1):
    files = []
    from_time = dt.datetime.now() - dt.timedelta(days=last_days)
    for f in os.listdir(dir):
        path = os.path.join(dir, f)
        mtime = dt.datetime.fromtimestamp(os.stat(path).st_mtime)
        if mtime > from_time:
            files.append(f)
    return files


class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'Přenos fotek'
        self.left = 30
        self.top = 30
        self.width = 940
        self.height = 680
        self.destination_dir = 'C:\\Users\\Karel\\Desktop\\dest'
        self.source_dir_pattern = 'C:\\Users\\K*\\Desktop\\source*'
        self.source_dir = "Nenastaven"
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.destination_model = QDirModel()
        self.destination_view = QTreeView()
        self.destination_view.setSortingEnabled(True)
        self.destination_view.sortByColumn(0, Qt.AscendingOrder)
        self.destination_view.setModel(self.destination_model)
        self.destination_view.setRootIndex(self.destination_model.index(self.destination_dir))

        self.source_model = QStandardItemModel()
        self.source_view = QListView()
        self.source_view.setModel(self.source_model)
        self.source_view.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.new_directory = QLineEdit()

        self.last_days_input = QLineEdit(str(1))
        self.last_days_input.setValidator(QIntValidator())
        self.last_days_input.editingFinished.connect(self.refresh_source)
        self.refresh_button = QPushButton("Obnovit")
        self.refresh_button.clicked.connect(self.refresh_source)

        new_directory_button = QPushButton("Vytvořit")
        new_directory_button.clicked.connect(self.create_dir)

        copy_button = QPushButton("Kopírovat")
        copy_button.clicked.connect(self.copy_files)
        move_button = QPushButton("Přesunout")
        move_button.clicked.connect(self.move_files)
        right_panel = QVBoxLayout()
        date_line = QHBoxLayout()
        date_line.addWidget(QLabel("Foťák - posledních dnů:"))
        date_line.addWidget(self.last_days_input)
        date_line.addWidget(self.refresh_button)
        right_panel.addLayout(date_line)
        right_panel.addWidget(self.source_view)
        button_line = QHBoxLayout()
        button_line.addWidget(copy_button)
        button_line.addWidget(move_button)
        right_panel.addLayout(button_line)

        windowLayout = QHBoxLayout()
        left_panel = QVBoxLayout()
        left_panel.addWidget(QLabel("Počítač"))
        left_panel.addWidget(self.destination_view)
        directory_line = QHBoxLayout()
        directory_line.addWidget(QLabel("Nová složka: "))
        directory_line.addWidget(self.new_directory)
        directory_line.addWidget(new_directory_button)
        left_panel.addLayout(directory_line)

        windowLayout.addLayout(left_panel)
        windowLayout.addLayout(right_panel)
        self.setLayout(windowLayout)
        self.show()
        self.refresh_source()

    def selected_files(self):
        selected_files = []
        for i in range(self.source_model.rowCount()):
            item = self.source_model.item(i)
            if item.checkState() == Qt.Checked:
                selected_files.append(item.text())
        return selected_files

    def refresh_source(self):
        self.source_model.clear()
        self.check_source_dir()
        if not os.path.exists(self.source_dir) or not os.path.isdir(self.source_dir):
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Foťák není připojen")
            msg.setInformativeText(f"Cesta {self.source_dir_pattern} není dostupná, připoj foťák a zapni jej.")
            msg.setWindowTitle("Nelze se spojit s foťákem")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
        else:
            for file_name in get_files(self.source_dir, int(self.last_days_input.text())):
                item = QStandardItem(file_name)
                check = Qt.Unchecked
                item.setCheckState(check)
                item.setCheckable(True)
                self.source_model.appendRow(item)

    def check_source_dir(self):
        dirs = glob.glob(self.source_dir_pattern)
        if len(dirs) >= 1:
            self.source_dir = dirs[0]
        else:
            self.source_dir = "Nedostupny"

    def refresh_destination(self):
        self.destination_model.refresh()

    def copy_files(self):
        for file in self.selected_files():
            print(file)
            copyfile(os.path.join(self.source_dir, file), os.path.join(self.dest_dir(), file))
        self.refresh_source()
        self.refresh_destination()

    def move_files(self):
        for file in self.selected_files():
            print(file)
            move(os.path.join(self.source_dir, file), os.path.join(self.dest_dir(), file))
        self.refresh_source()
        self.refresh_destination()

    def create_dir(self):
        name = self.new_directory.text().strip()
        print("Creating dir ", name)
        if name:
            Path(os.path.join(self.destination_dir, name)).mkdir(parents=True, exist_ok=True)
        self.refresh_destination()

    def dest_dir(self):
        index = self.destination_view.currentIndex()
        if index.isValid() and self.destination_model.isDir(index):
            return os.path.join(self.destination_dir, self.destination_model.fileName(index))
        else:
            return self.destination_dir


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())