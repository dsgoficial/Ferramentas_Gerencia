# -*- coding: utf-8 -*-
import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.config import Config
from Ferramentas_Gerencia.widgets.mDialog  import MDialog

class MEditLayers(MDialog):
    
    def __init__(self, sapCtrl):
        super(MEditLayers, self).__init__(controller=sapCtrl)
        self.tableWidget.setColumnHidden(5, True)

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'mEditLayers.ui'
        )

    def getColumnsIndexToSearch(self):
        return list(range(5))

    def addRow(self, layerId, layerName, layerSchema, layerAlias, layerDocumentation, layerInUse):
        idx = self.getRowIndex(layerId)
        if idx < 0:
            idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(idx)
        self.tableWidget.setItem(idx, 0, self.createNotEditableItem(layerId))
        self.tableWidget.setItem(idx, 1, self.createEditableItem(layerName))
        self.tableWidget.setItem(idx, 2, self.createNotEditableItem(layerSchema))
        self.tableWidget.setItem(idx, 3, self.createEditableItem(layerAlias))
        self.tableWidget.setItem(idx, 4, self.createEditableItem(layerDocumentation))
        self.tableWidget.setItem(idx, 5, self.createNotEditableItem(layerInUse))

    def addRows(self, layers):
        self.clearAllItems()
        for layerData in layers:
            self.addRow(
                layerData['id'], 
                layerData['nome'], 
                layerData['schema'],
                layerData['alias'],
                layerData['documentacao'],
                layerData['perfil'] or layerData['atributo']
            )
        self.adjustColumns()

    def getRowIndex(self, layerId):
        for idx in range(self.tableWidget.rowCount()):
            if not (
                    layerId == self.tableWidget.model().index(idx, 0).data()
                ):
                continue
            return idx
        return -1

    def getRowData(self, rowIndex):
        return {
            'id': int(self.tableWidget.model().index(rowIndex, 0).data()),
            'alias': self.tableWidget.model().index(rowIndex, 3).data(),
            'documentacao': self.tableWidget.model().index(rowIndex, 4).data()
        }  

    def saveTable(self):
        self.controller.updateLayers(self.getAllTableData())

    def removeSelected(self):
        deletedLayersIds = []
        ignored = False
        for qModelIndex in self.tableWidget.selectionModel().selectedRows():
            if not ( self.tableWidget.model().index(qModelIndex.row(),5).data() == 'False' ):
                ignored = True
                continue
            deletedLayersIds.append(int(self.tableWidget.model().index(qModelIndex.row(), 0).data()))
            self.tableWidget.removeRow(qModelIndex.row())
        if ignored:
            self.showInfo('Aviso', 'Algumas camadas não serão deletadas, pois estão em uso!')
        if deletedLayersIds:
            self.controller.deleteLayers(deletedLayersIds)