import sys, os
import time
import pandas as pd

from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import uic
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QFileDialog,QTableWidgetItem
from PyQt5.QtGui import QPixmap

import filepath
from DataDescriber import DataDescriber
from DataGenerator import DataGenerator
from ModelInspector import ModelInspector
from lib.utils import read_json_file

class DeidWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(DeidWindow, self).__init__(parent)
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = uic.loadUi("ui/deid.ui", self)

##########################################################################################

class ResultWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(ResultWindow, self).__init__(parent)
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = uic.loadUi("ui/result.ui", self)
        self.ui.nextButton.clicked.connect(self.next_button_method)
        plot_dir = 'plot/'
        plot_list = os.listdir(plot_dir)
        self.plot_images = []
        for plot in plot_list:
            image = QPixmap()
            image.load(plot_dir + plot)
            image = image.scaled(731,441)
            self.plot_images.append(image)
        self.index = 0
        self.ui.pic_label.setPixmap(self.plot_images[self.index])
        
    
    @pyqtSlot()
    def next_button_method(self):
        self.index = (self.index + 1) % len(self.plot_images)
        self.ui.pic_label.setPixmap(self.plot_images[self.index])
##########################################################################################

class SynWindow(QtWidgets.QDialog):
    def __init__(self, data, parent=None):
        super(SynWindow, self).__init__(parent)
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = uic.loadUi("ui/syn.ui", self)
        self.df = data
        self.ui.selectButton.clicked.connect(self.select_button_method)
        self.ui.generateButton.clicked.connect(self.generate_button_method)
        self.ui.resultButton.clicked.connect(self.result_button_method)
        self.add_columns_toListView()
        self.synList = []
        self.category = {}
        self.part_category = {}
        self.dataType = {}
        self.part_dataType = {}

        self.ui.ori_tableWidget.setColumnCount(len(self.df.columns))
        self.ui.ori_tableWidget.setRowCount(len(self.df.index))
        self.ui.ori_tableWidget.setHorizontalHeaderLabels(self.df.columns.values.tolist())

        for i in range(len(self.df.index)):
            for j in range(len(self.df.columns)):
                self.ui.ori_tableWidget.setItem(i,j, QTableWidgetItem(str(self.df.iat[i,j])))

    @pyqtSlot()
    def result_button_method(self):
        self.resultWindow = ResultWindow(self)
        self.resultWindow.exec_()
        
    @pyqtSlot()
    def select_button_method(self):
        for i in range(self.column_listWidget.count()):
            item = self.column_listWidget.item(i)
            if item.checkState() == QtCore.Qt.Checked:
                self.synList.append(item.text())
        
        listWidgets = [self.ui.category_listWidget, self.ui.int_listWidget]
        for data in self.df.columns.values.tolist():
            for widget in listWidgets:
                item = QtWidgets.QListWidgetItem()
                item.setText(str(data))
                item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
                item.setCheckState(QtCore.Qt.Checked)
                widget.addItem(item)

    @pyqtSlot()
    def generate_button_method(self):
        for i in range(self.category_listWidget.count()):
            item = self.category_listWidget.item(i)
            if item.checkState() == QtCore.Qt.Checked:
                self.category[item.text()] = True
            else:
                self.category[item.text()] = False

        for i in range(self.int_listWidget.count()):
            item = self.int_listWidget.item(i)
            if item.checkState() == QtCore.Qt.Checked:
                self.dataType[item.text()] = 'Integer'
            else:
                self.dataType[item.text()] = 'String'
        
        for syn in self.synList:
            self.part_category[syn] = self.category[syn]
            self.part_dataType[syn] = self.dataType[syn]
        
        if len(self.synList) == len(self.df.columns.values.tolist()):
            self.full_syn()
        else:
            self.part_syn()
        
        self.get_result_image()

    def full_syn(self):
        self.df.to_csv('tmp/ori.csv', index=False)

        describer = DataDescriber()
        describer.describe_dataset_in_correlated_attribute_mode(
            dataset_file='tmp/ori.csv',
            epsilon=0,
            k=1,
            attribute_to_datatype=self.dataType,
            attribute_to_is_categorical=self.category
        )
        describer.save_dataset_description_to_file('tmp/tmp.json')
        generator = DataGenerator()

        generator.generate_dataset_in_correlated_attribute_mode(len(self.df), 'tmp/tmp.json')
        generator.save_synthetic_data('tmp/output.csv')

        self.syn_df = pd.read_csv('tmp/output.csv')
        self.ui.tableWidget.setColumnCount(len(self.syn_df.columns))
        self.ui.tableWidget.setRowCount(len(self.syn_df.index))
        self.ui.tableWidget.setHorizontalHeaderLabels(self.syn_df.columns.values.tolist())

        for i in range(len(self.syn_df.index)):
            for j in range(len(self.syn_df.columns)):
                self.ui.tableWidget.setItem(i,j, QTableWidgetItem(str(self.syn_df.iat[i,j])))
    
    def part_syn(self):
        self.df.to_csv('tmp/ori.csv', index=False)
        self.df[self.synList].to_csv('tmp/tmp.csv', index=False)

        describer = DataDescriber()
        describer.describe_dataset_in_independent_attribute_mode(
            dataset_file='tmp/tmp.csv',
            attribute_to_datatype=self.part_dataType,
            attribute_to_is_categorical=self.part_category
        )
        describer.save_dataset_description_to_file('tmp/tmp.json')

        generator = DataGenerator()
        generator.generate_dataset_in_independent_mode(len(self.df), 'tmp/tmp.json', seed=0)
        generator.save_synthetic_data('tmp/syn.csv')

        describer.describe_dataset_in_independent_attribute_mode(
            dataset_file='tmp/ori.csv',
            attribute_to_datatype=self.dataType,
            attribute_to_is_categorical=self.category
        )
        describer.save_dataset_description_to_file('tmp/tmp.json')

        self.syn_df = self.df
        _df = pd.read_csv('tmp/syn.csv')
        self.syn_df[self.synList] = _df[self.synList]

        self.ui.tableWidget.setColumnCount(len(self.syn_df.columns))
        self.ui.tableWidget.setRowCount(len(self.syn_df.index))
        self.ui.tableWidget.setHorizontalHeaderLabels(self.syn_df.columns.values.tolist())

        for i in range(len(self.syn_df.index)):
            for j in range(len(self.syn_df.columns)):
                self.ui.tableWidget.setItem(i,j, QTableWidgetItem(str(self.syn_df.iat[i,j])))

    def get_result_image(self):
        attribute_description = read_json_file('tmp/tmp.json')['attribute_description']
        inspector = ModelInspector(self.df, self.syn_df, attribute_description)

        for attribute in self.syn_df.columns:
            figure_filepath = 'plot/' + attribute + '.png'
            inspector.compare_histograms(attribute, figure_filepath)
    
        mutual_figure_filepath = 'plot/mutual_information_heatmap.png'
        inspector.mutual_information_heatmap(mutual_figure_filepath)

    def add_columns_toListView(self):
        for column in self.df.columns.values.tolist():
            item = QtWidgets.QListWidgetItem()
            item.setText(str(column))
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Checked)
            self.column_listWidget.addItem(item)

######################################################################################################################################################

class InputFileWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(InputFileWindow, self).__init__(parent)
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = uic.loadUi("ui/inputfile.ui", self)
        self.ui.pushButton.clicked.connect(self.file_select_button_method)
        self.ui.doneButton.clicked.connect(self.done_button_method)

    @pyqtSlot()
    def file_select_button_method(self):
        self.listWidget.clear()
        self.fname = QFileDialog.getOpenFileName(self)
        self.ui.lineEdit.setText(self.fname[0])
        
        self.df = pd.read_csv(self.fname[0])
        self.add_columns_toListView()
    
    def add_columns_toListView(self):
        for column in self.df.columns.values.tolist():
            item = QtWidgets.QListWidgetItem()
            item.setText(str(column))
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Checked)
            self.listWidget.addItem(item)

    @pyqtSlot()
    def done_button_method(self):
        self.df = pd.read_csv(self.fname[0])
        for i in range(self.listWidget.count()):
            item = self.listWidget.item(i)
            if item.checkState() != QtCore.Qt.Checked:
                self.df = self.df.drop(item.text(), axis=1)
            
        self.ui.tableWidget.setColumnCount(len(self.df.columns))
        self.ui.tableWidget.setRowCount(len(self.df.index))
        self.ui.tableWidget.setHorizontalHeaderLabels(self.df.columns.values.tolist())

        for i in range(len(self.df.index)):
            for j in range(len(self.df.columns)):
                self.ui.tableWidget.setItem(i,j, QTableWidgetItem(str(self.df.iat[i,j])))

######################################################################################################################################################
# main form

class Form(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = uic.loadUi("ui/main.ui", self)
        self.df = pd.DataFrame()
        self.ui.deidButton.clicked.connect(self.slot_deid_button_method)
        self.ui.inputButton.clicked.connect(self.slot_fileinput_button_method)
        self.ui.outputButton.clicked.connect(self.slot_fileoutput_button_method)
        self.ui.syndataButton.clicked.connect(self.syn_button_method)

        self.ui.show()

    @pyqtSlot()
    def slot_deid_button_method(self):
        self.deidWindow = DeidWindow(self)
        self.deidWindow.show()

    @pyqtSlot()
    def slot_fileinput_button_method(self):
        self.inputfileWindow = InputFileWindow(self)
        self.inputfileWindow.exec_()
        self.df = self.inputfileWindow.df
        self.refresh_table()
    
    def refresh_table(self):
        self.ui.tableWidget.setColumnCount(len(self.df.columns))
        self.ui.tableWidget.setRowCount(len(self.df.index))
        self.ui.tableWidget.setHorizontalHeaderLabels(self.df.columns.values.tolist())

        for i in range(len(self.df.index)):
            for j in range(len(self.df.columns)):
                self.ui.tableWidget.setItem(i,j, QTableWidgetItem(str(self.df.iat[i,j])))

    @pyqtSlot()
    def slot_fileoutput_button_method(self):
        fname = QFileDialog.getSaveFileName(self)
        self.df.to_csv(fname[0], index=False)

    @pyqtSlot()
    def syn_button_method(self):
        self.synWindow = SynWindow(parent=self, data=self.df)
        self.synWindow.exec_()
        self.df = self.synWindow.df
        self.refresh_table()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = Form()
    sys.exit(app.exec())