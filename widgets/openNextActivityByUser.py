import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.dockWidget  import DockWidget
 
class OpenNextActivityByUser(DockWidget):

    def __init__(self, users, sapCtrl):
        super(OpenNextActivityByUser, self).__init__(controller=sapCtrl)
        self.loadUsers( users )
        self.setWindowTitle('Abrir Atividade do Operador')

    def loadUsers(self, users):
        for user in sorted(
                    users, 
                    key=lambda user: '{0} {1}'.format(user['tipo_posto_grad'], user['nome_guerra'])
                ):
            self.usersCb.addItem(
                '{0} {1}'.format(user['tipo_posto_grad'], user['nome_guerra']), 
                user['id']
            )

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "openNextActivityByUser.ui"
        )

    def clearInput(self):
        self.nextActivityCkb.setChecked(False)

    def validInput(self):
        return  self.getUserId() != None

    def getUserId(self):
        return self.usersCb.itemData(self.usersCb.currentIndex())

    def runFunction(self):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        result = self.controller.openSapNextActivityByUser(
            self.getUserId(),
            self.nextActivityCkb.isChecked()
        )
        QtWidgets.QApplication.restoreOverrideCursor()
        self.close() if result else ''