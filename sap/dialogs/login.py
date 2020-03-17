# -*- coding: utf-8 -*-
import os, sys
from PyQt5 import QtCore, uic, QtWidgets
from Ferramentas_Gerencia.config import Config
from Ferramentas_Gerencia.sap.interfaces.ILogin  import ILogin
from Ferramentas_Gerencia.sap.factory.messageSingleton  import MessageSingleton

class Login(QtWidgets.QDialog, ILogin):

    uiPath = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        '..',
        'uis',
        'login.ui'
    )

    def __init__(self, loginCtrl):
        super(Login, self).__init__(loginCtrl=loginCtrl)
        uic.loadUi(self.uiPath, self)
        self.version_text.setText("<b>versão: {}</b>".format(Config.VERSION))
        
    def loadData(self, user, server):
        self.userLe.setText(user) 
        self.serverLe.setText(server)  
        self.passwordLe.setText("")

    def showView(self):
        self.exec_()

    def closeView(self):
        self.close()

    def showError(self, title, text):
        MessageSingleton.getInstance().showError(
            self,
            title, 
            text
        )
        
    def validInput(self):
        test = ( 
            self.serverLe.text() 
            and  
            self.userLe.text() 
            and
            self.passwordLe.text()
        )
        return test

    @QtCore.pyqtSlot(bool)
    def on_submitBtn_clicked(self):
        if not self.validInput():
            html = u'<p style="color:red">Todos os campos devem ser preenchidos!</p>'
            self.showError('Aviso', html)
            return
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        try:
            self.login()
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()

    def login(self):
        user = self.userLe.text() 
        password = self.passwordLe.text()
        server = self.serverLe.text() 
        self.loginCtrl.authUser(user, password, server)

    
        


    