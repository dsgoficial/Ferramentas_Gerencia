import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.dockWidget  import DockWidget
from qgis import core
from functools import cmp_to_key
from .createProductModel import CreateProductModel

class CreateProduct(DockWidget):

    def __init__(
            self, 
            comboBoxPolygonLayer, 
            comboBoxPolygonLayerModel,
            sapCtrl,
            qgis
        ):
        super(CreateProduct, self).__init__(controller=sapCtrl)
        self.qgis = qgis
        self.sapCtrl = sapCtrl
        self.comboBoxPolygonLayerModel = comboBoxPolygonLayerModel
        self.comboBoxPolygonLayer = comboBoxPolygonLayer
        self.comboBoxPolygonLayer.currentIndexChanged.connect(self.updateAssociatedFields)
        self.mapLayerLayout.addWidget(self.comboBoxPolygonLayer)
        self.loadLots(self.controller.getSapLots())
        self.updateAssociatedFields(self.comboBoxPolygonLayer.currentIndex())
        self.setWindowTitle('Carregar Produtos')
        self.createProductModelDlg = None

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "createProduct.ui"
        )

    def clearInput(self):
        pass

    def validInput(self):
        return (
            self.comboBoxPolygonLayer.currentLayer()
            and
            self.getBlockId()
        )

    def updateAssociatedFields(self, currentIndex):
        if currentIndex < 0:
            return
        fields = self.comboBoxPolygonLayer.getCurrentLayerFields()
        for setting in [
                {
                    'combo': self.uuidFieldCb,
                    'fields': [''] + fields,
                    'default': 'uuid'
                },
                {
                    'combo': self.nameFieldCb,
                    'fields': [''] + fields,
                    'default': 'nome'
                },
                {
                    'combo': self.miFieldCb,
                    'fields': [''] + fields,
                    'default': 'mi'
                },
                {
                    'combo': self.inomFieldCb,
                    'fields': [''] + fields,
                    'default': 'inom'
                },
                {
                    'combo': self.scaleFieldCb,
                    'fields': [''] + fields,
                    'default': 'denominador_escala'
                },
                {
                    'combo': self.editionCb,
                    'fields': [''] + fields,
                    'default': 'edicao'
                }
            ]:
            combo = setting['combo']
            combo.clear()
            fieldSorted = sorted(setting['fields'], key=cmp_to_key(lambda a, b: 1 if b == setting['default'] else -1))
            if fieldSorted[0] != setting['default']:
                fieldSorted = sorted(setting['fields'], key=cmp_to_key(lambda a, b: 1 if b == '' else -1))
            combo.addItems(fieldSorted)

    def getAssociatedFields(self):
        return {
            'uuid': self.uuidFieldCb.currentText(),
            'nome': self.nameFieldCb.currentText(),
            'mi': self.miFieldCb.currentText(),
            'inom': self.inomFieldCb.currentText(),
            'denominador_escala': self.scaleFieldCb.currentText(),
            'edicao': self.editionCb.currentText()
        }

    def loadLots(self, lots):
        self.lotCb.clear()
        self.lotCb.addItem('...', None)
        for lot in lots:
            self.lotCb.addItem(
                lot['nome'], 
                lot['id']
            )

    def getBlockId(self):
        return self.lotCb.itemData(self.lotCb.currentIndex())

    def runFunction(self):
        layer = self.comboBoxPolygonLayer.currentLayer()
        if len([ f for f in layer.getFeatures() if f.geometry().wkbType() != core.QgsWkbTypes.MultiPolygon ]) != 0:
            self.showError('Aviso', 'A camada deve ser do tipo "MultiPolygon"!')
            return
        self.controller.createSapProducts(
            layer, 
            self.getBlockId(), 
            self.getAssociatedFields(), 
            self.onlySelectedCkb.isChecked()
        )

    @QtCore.pyqtSlot(bool)
    def on_templateLayerBtn_clicked(self):
        self.createProductModelDlg.close() if self.createProductModelDlg else ''
        self.createProductModelDlg = CreateProductModel(
            self,
            self.comboBoxPolygonLayerModel,
            self.sapCtrl
        )
        self.createProductModelDlg.create.connect(
            self.qgis.generateProductLayer
        )
        self.createProductModelDlg.show()