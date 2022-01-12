import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.inputDialogV2  import InputDialogV2

class UserProfileManager(InputDialogV2):

    save = QtCore.pyqtSignal(dict)

    def __init__(self, controller, parent=None):
        super(UserProfileManager, self).__init__(controller, parent)
        self.setWindowTitle('Associar Usuários para Perfis')

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'userProfileManager.ui'
        )

    def loadProfiles(self, data):
        self.profileCb.clear()
        self.profileCb.addItem('...', None)
        for d in data:
            self.profileCb.addItem(d['nome'], d['id'])

    def getData(self):
        return {}

    @QtCore.pyqtSlot(bool)
    def on_addSettingBtn_clicked(self):
        self.getController().openAddProfileProductionSetting(
            self,
            self.addRowSettingTable
        )

    def addRowSettingTable(self):
        pass

    @QtCore.pyqtSlot(bool)
    def on_createProfileBtn_clicked(self):
        self.getController().openCreateProfileProduction(
            self,
            self.updateProfiles
        )

    def updateProfiles(self):
        pass

    def closeEvent(self, e):
        self.closeChildren(QtWidgets.QDialog)
        super().closeEvent(e)

    def closeChildren(self, typeWidget):
        [ d.close() for d in self.findChildren(typeWidget) ]