import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.dockWidget  import DockWidget
 
class  LoadLayersQgisProject(DockWidget):

    def __init__(self, sapCtrl):
        super(LoadLayersQgisProject, self).__init__(controller=sapCtrl)
        self.setWindowTitle('Carregar Camadas de Acompanhamento')

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "loadLayersQgisProject.ui"
        )

    def clearInput(self):
        self.projectInProgressCkb.setChecked(False)

    def validInput(self):
        return  True

    def runFunction(self):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        try:
            self.controller.loadLayersQgisProject(
                self.projectInProgressCkb.isChecked()
            )
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()
        self.close()
        