import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.dockWidgetAutoComplete  import DockWidgetAutoComplete

 
class UnlockWorkspace(DockWidgetAutoComplete):

    def __init__(self, sapCtrl):
        super(UnlockWorkspace, self).__init__(controller=sapCtrl)
        self.setWindowTitle('Desbloquear Unidades de Trabalho')

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "unlockWorkspace.ui"
        )

    def clearInput(self):
        return  self.workspacesIdsLe.setText('')

    def validInput(self):
        return  self.workspacesIdsLe.text()

    def getWorkspacesIds(self):
        return [ int(d) for d in self.workspacesIdsLe.text().split(',') if d ]

    def runFunction(self):
        self.controller.unlockSapWorkspace(
            self.getWorkspacesIds()
        )
    
    def autoCompleteInput(self):
        values = self.controller.getValuesFromLayer('unlockWorkspace', 'workUnit')
        self.workspacesIdsLe.setText(values)