import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.sap.dockWidgets.dockWidgetAutoComplete  import DockWidgetAutoComplete
 
class AddNewRevisionCorrection(DockWidgetAutoComplete):

    def __init__(self, sapCtrl):
        super(AddNewRevisionCorrection, self).__init__(sapCtrl=sapCtrl)

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "addNewRevisionCorrection.ui"
        )

    def clearInput(self):
        self.workspacesIdLe.setText('')

    def validInput(self):
        return self.workspacesIdLe.text()

    def getWorkspacesIds(self):
        return [ int(d) for d in self.workspacesIdLe.text().split(',') if d ]

    def runFunction(self):
        self.sapCtrl.addNewRevisionCorrection(
            self.getWorkspacesIds()
        )
    
    def autoCompleteInput(self):
        values = self.sapCtrl.getValuesFromLayer('addNewRevisionCorrection', 'workUnit')
        self.workspacesIdLe.setText(values)