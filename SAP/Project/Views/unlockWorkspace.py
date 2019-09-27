# -*- coding: utf-8 -*-
import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.utils import msgBox

class UnlockWorkspace(QtWidgets.QWidget):

    dialog_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 
        'unlockWorkspace.ui'
    )

    icon_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 
        '..',
        '..',
        '..',
        'icons',
        'extract.png'
    )

    run = QtCore.pyqtSignal()

    extractValues = QtCore.pyqtSignal()

    def __init__(self, iface):
        super(UnlockWorkspace, self).__init__()
        self.iface = iface
        uic.loadUi(self.dialog_path, self)
        self.extract_field_btn.setIcon(QtGui.QIcon(self.icon_path))
        self.extract_field_btn.setIconSize(QtCore.QSize(24,24))
        self.extract_field_btn.setToolTip('Extrair valores mediante seleções')
        self.extract_field_btn.clicked.connect(
            self.extractValues.emit
        )
        self.ok_btn.clicked.connect( 
            self.validate_input    
        )

    def validate_input(self):
        if self.workspace_ids_le.text():
            self.run.emit()
        else:
            html = "<p>Preencha todos os campos!</p>"
            msgBox.show(text=html, title=u"Erro", parent=self)

    def get_input_data(self):
        return {
            "param" : {
                "unidade_trabalho_ids" : [ int(d) for d in self.workspace_ids_le.text().split(',')]
            },
            "function_name" : "unlock_workspace"
        }

    def get_extraction_config(self):
        return [
            {
                "layer_name" : "atividade_id",
                "field_name" : "atividade_id",
                "all_selection" : True
            },
            {
                "layer_name" : "atividades_em_execucao",
                "field_name" : "atividade_id",
                "all_selection" : True
            },
            {
                "layer_name" : "ultimas_atividades_finalizadas",
                "field_name" : "atividade_id",
                "all_selection" : True
            },
            {
                "layer_name" : "subfase_",
                "field_name" : "atividade_id",
                "all_selection" : True
            }
        ]