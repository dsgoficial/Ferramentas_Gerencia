# -*- coding: utf-8 -*-
import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.config import Config
from Ferramentas_Gerencia.widgets.mDialogV2  import MDialogV2
from .addProjectForm import AddProjectForm
import json

class MProjects(MDialogV2):
    
    def __init__(self, 
                controller,
                qgis,
                sap,
                addProjectForm=AddProjectForm
            ):
        super(MProjects, self).__init__(controller=controller)
        self.addProjectForm = addProjectForm
        self.qgis = qgis
        self.sap = sap
        self.addProjectFormDlg = None
        self.tableWidget.setColumnHidden(0, True)
        self.fetchData()

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'mProjects.ui'
        )
    
    def getColumnsIndexToSearch(self):
        return [2,3,4]

    def fetchData(self):
        data = self.sap.getProjects()
        self.addRows(data)

    def addRows(self, projects):
        self.clearAllItems()
        for project in projects:
            self.addRow(
                project['id'],
                project['nome'],
                project['descricao'],
                project['nome_abrev'],
                json.dumps(project)
            )
        self.adjustColumns()

    def addRow(self, 
            primaryKey, 
            name,
            description,
            alias,
            dump
        ):
        idx = self.getRowIndex(primaryKey)
        if idx < 0:
            idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(idx)
        self.tableWidget.setItem(idx, 0, self.createNotEditableItem(primaryKey))
        self.tableWidget.setItem(idx, 2, self.createNotEditableItem(name))
        self.tableWidget.setItem(idx, 3, self.createNotEditableItem(description))
        self.tableWidget.setItem(idx, 4, self.createNotEditableItem(alias))
        self.tableWidget.setItem(idx, 5, self.createNotEditableItem(dump))
        optionColumn = 1
        self.tableWidget.setCellWidget(
            idx, 
            optionColumn, 
            self.createRowEditWidget(
                self.tableWidget,
                idx,
                optionColumn, 
                self.handleEditBtn, 
                self.handleDeleteBtn
            )
        )

    def handleEditBtn(self, index):
        data = self.getRowData(index.row())
        self.addProjectFormDlg.close() if self.addProjectFormDlg else None
        self.addProjectFormDlg = self.addProjectForm(
            self.controller,
            self.sap,
            self.qgis,
            self
        )
        self.addProjectFormDlg.activeEditMode(True)
        self.addProjectFormDlg.setData(data)
        self.addProjectFormDlg.save.connect(self.fetchData)
        self.addProjectFormDlg.show()

        
    def handleDeleteBtn(self, index):
        data = self.getRowData(index.row())
        message = self.sap.deleteProjects([data['id']])
        self.showInfo('Aviso', message)
        self.fetchData()

    def getRowIndex(self, primaryKey):
        for idx in range(self.tableWidget.rowCount()):
            if not (
                    primaryKey == self.tableWidget.model().index(idx, 0).data()
                ):
                continue
            return idx
        return -1

    def getRowData(self, rowIndex):
        data = json.loads(self.tableWidget.model().index(rowIndex, 5).data())
        return {
            'id': data['id'],
            'nome': data['nome'],
            'descricao': data['descricao'],
            'nome_abrev': data['nome_abrev'],
            'finalizado': data['finalizado']
        }

    @QtCore.pyqtSlot(bool)
    def on_addFormBtn_clicked(self):
        self.addProjectFormDlg.close() if self.addProjectFormDlg else None
        self.addProjectFormDlg = self.addProjectForm(
            self.controller,
            self.sap,
            self.qgis,
            self
        )
        self.addProjectFormDlg.save.connect(self.fetchData)
        self.addProjectFormDlg.show()