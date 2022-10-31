import os, sys
from PyQt5 import QtCore, uic, QtWidgets
from Ferramentas_Gerencia.widgets.inputDialog  import InputDialog

class AddStyleForm(InputDialog):

    def __init__(self, parent=None):
        super(AddStyleForm, self).__init__(parent)
        

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addStyleForm.ui'
        )
        
    def clearInput(self):
        pass

    def validInput(self):
        return self.styleNameLe.text()

    def getData(self):
        return {
            'grupo_estilo_id': self.groupCb.itemData(self.groupCb.currentIndex())
        }

    def loadGroupStyles(self, styles):
        self.groupCb.clear()
        self.groupCb.addItem('...', None)
        for style in styles:
            self.groupCb.addItem(style['nome'], style['id'])

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        """ if not self.validInput():
            self.showError('Aviso', 'Informe um nome de estilo')
            return """
        self.accept()