import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.dockWidget  import DockWidget
 
class  ImportLayers(DockWidget):

    def __init__(self, sapCtrl):
        super(ImportLayers, self).__init__(controller=sapCtrl)
        self.setWindowTitle('Importar Camadas')
        
    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "openManagement.ui"
        )

    def clearInput(self):
        pass

    def validInput(self):
        return  True

    def runFunction(self):
        self.controller.openManagementImportLayers()