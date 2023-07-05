import json, requests, socket
import os
import re

from Ferramentas_Gerencia.modules.sap.factories.loginSingleton import LoginSingleton
from Ferramentas_Gerencia.modules.utils.factories.utilsFactory import UtilsFactory
from Ferramentas_Gerencia.modules.sap.factories.dataModelFactory import DataModelFactory

SSL_VERIFY=False

TIMEOUT = 60 * 2

class SapHttp:   

    def __init__(self, 
            qgis, 
            fmeCtrl,
            loginSingleton=LoginSingleton,
            messageFactory=UtilsFactory().createMessageFactory(),
            dataModelFactory=DataModelFactory()
        ):
        super(SapHttp, self).__init__()
        self.qgis = qgis
        self.fmeCtrl = fmeCtrl
        self.messageFactory = messageFactory
        self.activityDataModel = dataModelFactory.createDataModel('SapActivity')
        self.loginView = loginSingleton.getInstance(loginCtrl=self)
        self.server = None
        self.token = None

    def showErrorMessageBox(self, parent, title, message):
        errorMessageBox = self.messageFactory.createMessage('ErrorMessageBox')
        errorMessageBox.show(parent, title, message)

    def showQuestionMessageBox(self, parent, title, message):
        questionMessageBox = self.messageFactory.createMessage('QuestionMessageBox')
        return questionMessageBox.show(parent, title, message)
    
    def showInfoMessageBox(self, parent, title, message):
        infoMessageBox = self.messageFactory.createMessage('InfoMessageBox')
        infoMessageBox.show(parent, title, message)

    def login(self):
        self.loginView.loadData(
            user=self.qgis.getSettingsVariable('sapmanager:user'), 
            server=self.qgis.getSettingsVariable('sapmanager:server')
        )
        return self.loginView.showView()

    def saveLoginData(self, user, password, server):
        self.qgis.setSettingsVariable('sapmanager:user', user)
        self.qgis.setSettingsVariable('sapmanager:password', password)
        self.qgis.setSettingsVariable('sapmanager:server', server)

    def authUser(self, user, password, server):
        try:
            self.setServer(server)
            response = self.loginAdminUser(
                user, 
                password,
                self.qgis.getVersion(),
                self.qgis.getPluginsVersions()
            )
            self.setToken(response['dados']['token'])
            self.loginView.accept()      
        except Exception as e:
            self.showErrorMessageBox(self.loginView, 'Aviso', str(e))
        finally:
            self.saveLoginData(user, password, server)
        return True   

    def getActivityDataById(self, activityId):
        acitivityData = self.openActivity(activityId)
        acitivityData['user'] = self.qgis.getSettingsVariable('sapmanager:user')
        acitivityData['password'] = self.qgis.getSettingsVariable('sapmanager:password')
        return acitivityData

    def getNextActivityDataByUser(self, userId, nextActivity):
        acitivityData = self.openNextActivityByUser(userId, nextActivity)
        acitivityData['user'] = self.qgis.getSettingsVariable('sapmanager:user')
        acitivityData['password'] = self.qgis.getSettingsVariable('sapmanager:password')
        return acitivityData

    def getActivity(self):
        return self.activityDataModel     

    def downloadQgisProject(self, destPath):
        try:
            projectXml = self.getQgisProject()
            with open(destPath, 'w') as f:
                f.write(projectXml)
            self.showInfoMessageBox(self.qgis.getMainWindow(), 'Aviso', 'Projeto criado com sucesso!')
        except Exception as e:
            self.showErrorMessageBox(self.qgis.getMainWindow(), 'Aviso', str(e))

    def httpPost(self, url, postData, headers, timeout=TIMEOUT):
        if self.getToken():
            headers['authorization'] = self.getToken()
        session = requests.Session()
        session.trust_env = False
        response = session.post(url, data=json.dumps(postData), verify=SSL_VERIFY, headers=headers, timeout=timeout)
        self.checkError(response)
        return response

    def httpGet(self, url): 
        headers = {}
        if self.getToken():
            headers['authorization'] = self.getToken()
        session = requests.Session()
        session.trust_env = False
        response = session.get(url, verify=SSL_VERIFY, headers=headers, timeout=TIMEOUT)
        self.checkError(response)
        return response

    def httpPut(self, url, postData={}, headers={}, timeout=TIMEOUT):
        if self.getToken():
            headers['authorization'] = self.getToken()
        session = requests.Session()
        session.trust_env = False
        response = session.put(url, data=json.dumps(postData), verify=SSL_VERIFY, headers=headers, timeout=timeout)
        self.checkError(response)
        return response

    def httpDelete(self, url, postData={}, headers={}):
        if self.getToken():
            headers['authorization'] = self.getToken()
        session = requests.Session()
        session.trust_env = False
        response = session.delete(url, data=json.dumps(postData), verify=SSL_VERIFY, headers=headers, timeout=TIMEOUT)
        self.checkError(response)
        return response

    def setServer(self, server):
        self.server = "{0}/api".format(server)

    def getServer(self):
        return self.server

    def setToken(self, token):
        self.token = token

    def getToken(self):
        return self.token

    def getProductionProfiles(self):
        response = self.httpGet(
            url="{0}/gerencia/perfil_producao".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return [{'nome': 'Sem perfis de produção', 'id': False}]
    
    def createProductionProfiles(self, data):
        response = self.httpPostJson(
            url="{0}/gerencia/perfil_producao".format(self.getServer()),
            postData={
                "perfil_producao" : data
            }
        )
        return response.json()['message']

    def updateProductionProfiles(self, data):
        response = self.httpPutJson(
            url="{0}/gerencia/perfil_producao".format(self.getServer()),
            postData={
                "perfil_producao" : data
            }
        )
        return response.json()['message']

    def deleteProductionProfiles(self, data):
        response = self.httpDeleteJson(
            url="{0}/gerencia/perfil_producao".format(self.getServer()),
            postData={
                "perfil_producao_ids" : data
            }
        )
        return response.json()['message']

    def getUsers(self):
        response = self.httpGet(
            url="{0}/usuarios".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return [{'nome': 'Sem usuários', 'id': False}]

    def loginAdminUser(self, user, password, gisVersion, pluginsVersion):
        response = self.httpPostJson(
            url="{0}/login".format(self.getServer()), 
            postData={
                "usuario" : user,
                "senha" : password,
                'plugins' : pluginsVersion,
                'qgis' : gisVersion,
                'cliente' : 'sap_fg'
            }
        )
        responseJson = response.json()
        if not self.validVersion(responseJson):
            raise Exception("Versão do servidor sap errada")
        if not self.isAdminUser(responseJson):
            raise Exception("Usuário não é administrador")
        return responseJson

    def validVersion(self, responseJson):
        return ('version' in responseJson and responseJson['version'].split('.')[0] == '2')

    def isAdminUser(self, responseJson):
        return ('administrador' in responseJson['dados'] and responseJson['dados']['administrador'])

    def httpPostJson(self, url, postData, timeout=TIMEOUT):
        headers = {
            'content-type' : 'application/json'
        }
        return  self.httpPost(
            url, 
            postData,
            headers,
            timeout=timeout
        )

    def checkError(self, response):
        if response.status_code == 429:
            raise Exception('Excesso de requisições, aguarde um momento!')
        if response.status_code == 404:
            raise Exception('Servidor não encontrado!')
        if response.status_code == 413:
            raise Exception('Request Entity Too Large!')
        if response.status_code == 504:
            raise Exception('Tempo excedido!')
        if response.status_code == 403:
            raise Exception('Token expirado, faça o login novamente!')
        if not response.ok:
            raise Exception(response.json()['message'])
        

    def httpPutJson(self, url, postData):
        headers = {
            'content-type' : 'application/json'
        }
        return  self.httpPut(
            url, 
            postData,
            headers
        )

    def httpDeleteJson(self, url, postData):
        headers = {
            'content-type' : 'application/json'
        }
        return  self.httpDelete(
            url, 
            postData,
            headers
        )

    def advanceActivityToNextStep(self, activityIds, endStep):
        response = self.httpPostJson(
            url="{0}/gerencia/atividade/avancar".format(self.getServer()),
            postData={
                "atividade_ids" : activityIds,
                "concluida" : endStep
            }
        )
        return response.json()['message']

    def createPriorityGroupActivity(self, activityIds, priority, profileId):
        response = self.httpPostJson(
            url="{0}/gerencia/fila_prioritaria_grupo".format(self.getServer()),
            postData={
                "atividade_ids" : activityIds,
                "prioridade" : int(priority),
                "perfil_producao_id" : profileId
            }
        )
        return response.json()['message']

    def fillCommentActivity(self, activityIds, commentActivity, commentWorkspace):
        response = self.httpPutJson(
            url="{0}/gerencia/observacao".format(self.getServer()),
            postData={
                "atividade_ids" : activityIds,
                "observacao_atividade" : commentActivity,
                "observacao_unidade_trabalho" : commentWorkspace
            }
        )
        return response.json()['message']

    def getCommentsByActivity(self, activityId):
        response = self.httpGet(
            url="{0}/gerencia/atividade/{1}/observacao".format(self.getServer(), activityId)
        )
        return response.json()['dados']

    def openActivity(self, activityId):
        response = self.httpGet(
            url="{0}/gerencia/atividade/{1}".format(self.getServer(), activityId),
        )
        return response.json()

    #interface
    def openNextActivityByUser(self, userId, nextActivity):
        params = '?proxima=true' if nextActivity else ''
        response = self.httpGet(
            url="{0}/gerencia/atividade/usuario/{1}{2}".format(self.getServer(), userId, params)
        )
        return response.json()
        
    #interface
    def lockWorkspace(self, workspacesIds):
        response = self.httpPostJson(
            url="{0}/gerencia/unidade_trabalho/disponivel".format(self.getServer()),
            postData={
                "unidade_trabalho_ids" : workspacesIds,
                "disponivel" : False
            }
        )
        return response.json()['message']

    #interface
    def pauseActivity(self, workspacesIds):
        response = self.httpPostJson(
            url="{0}/gerencia/atividade/pausar".format(self.getServer()),
            postData={
                "unidade_trabalho_ids" : workspacesIds
            }
        )
        return response.json()['message']
    
    #interface
    def restartActivity(self, workspacesIds):
        response = self.httpPostJson(
            url="{0}/gerencia/atividade/reiniciar".format(self.getServer()),
            postData={
                "unidade_trabalho_ids" : workspacesIds
            }
        )
        return response.json()['message']
    
    #interface
    def returnActivityToPreviousStep(self, activityIds, preserveUser):
        response = self.httpPostJson(
            url="{0}/gerencia/atividade/voltar".format(self.getServer()),
            postData={
                "atividade_ids" : activityIds,
                "manter_usuarios" : preserveUser
            }
        )
        return response.json()['message']

    #interface
    def setPriorityActivity(self, activityIds, priority, userId):
        response = self.httpPostJson(
            url="{0}/gerencia/fila_prioritaria".format(self.getServer()),
            postData={
                "atividade_ids" : activityIds,
                "prioridade" : int(priority),
                "usuario_prioridade_id" : userId
            }
        )
        return response.json()['message']

     #interface
    def unlockWorkspace(self, workspacesIds):
        response = self.httpPostJson(
            url="{0}/gerencia/unidade_trabalho/disponivel".format(self.getServer()),
            postData={
                "unidade_trabalho_ids" : workspacesIds,
                "disponivel" : True
            }
        )
        return response.json()['message']

    def getStyles(self):
        response = self.httpGet(
            url="{0}/projeto/estilos".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return []

    def getGroupStyles(self):
        response = self.httpGet(
            url="{0}/projeto/grupo_estilos".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return []

    def createGroupStyles(self, data):
        response = self.httpPostJson(
            url="{0}/projeto/grupo_estilos".format(self.getServer()),
            postData={
                'grupo_estilos': data
            }
        )
        return response.json()['message']

    def deleteGroupStyles(self, data):
        response = self.httpDeleteJson(
            url="{0}/projeto/grupo_estilos".format(self.getServer()),
            postData={
                'grupo_estilos_ids': data
            }
        )
        return response.json()['message']

    def updateGroupStyles(self, data):
        response = self.httpPutJson(
            url="{0}/projeto/grupo_estilos".format(self.getServer()),
            postData={
                'grupo_estilos': data
            }
        )
        return response.json()['message']

    def getStyleNames(self):
        response = self.httpGet(
            url="{0}/projeto/estilos".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return []
    
    def createStyles(self, data):
        response = self.httpPostJson(
            url="{0}/projeto/estilos".format(self.getServer()),
            postData={
                "estilos" : data,
            }
        )
        return response.json()['message']

    def updateStyles(self, data):
        response = self.httpPutJson(
            url="{0}/projeto/estilos".format(self.getServer()),
            postData={
                "estilos" : data,
            }
        )
        return response.json()['message']

    def deleteStyles(self, ids):
        response = self.httpDeleteJson(
            url="{0}/projeto/estilos".format(self.getServer()),
            postData={
                'estilos_ids': ids
            }  
        )
        return response.json()['message']

    def getModels(self):
        response = self.httpGet(
            url="{0}/projeto/modelos".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return []

    def createModels(self, data):
        response = self.httpPostJson(
            url="{0}/projeto/modelos".format(self.getServer()),
            postData={
                "modelos" : data,
            }
        )
        return response.json()['message']

    def updateModels(self, data):
        response = self.httpPutJson(
            url="{0}/projeto/modelos".format(self.getServer()),
            postData={
                'modelos': data
            }    
        )
        return response.json()['message']

    def deleteModels(self, ids):
        response = self.httpDeleteJson(
            url="{0}/projeto/modelos".format(self.getServer()),
            postData={
                'modelos_ids': ids
            }  
        )
        return response.json()['message']

    def getRules(self):
        response = self.httpGet(
            url="{0}/projeto/regras".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return []

    def createRules(self, data):
        response = self.httpPostJson(
            url="{0}/projeto/regras".format(self.getServer()),
            postData={
                'regras': data
            }
        )
        return response.json()['message']

    def updateRules(self, data):
        response = self.httpPutJson(
            url="{0}/projeto/regras".format(self.getServer()),
            postData={
                'regras': data
            }
        )
        return response.json()['message']

    def deleteRules(self, ids):
        response = self.httpDeleteJson(
            url="{0}/projeto/regras".format(self.getServer()),
            postData={
                'regras_ids': ids
            }
        )
        return response.json()['message']

    def getRuleSet(self):
        response = self.httpGet(
            url="{0}/projeto/grupo_regras".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return []

    def createRuleSet(self, data):
        response = self.httpPostJson(
            url="{0}/projeto/grupo_regras".format(self.getServer()),
            postData={
                'grupo_regras': data
            }
        )
        return response.json()['message']

    def updateRuleSet(self, data):
        response = self.httpPutJson(
            url="{0}/projeto/grupo_regras".format(self.getServer()),
            postData={
                'grupo_regras': data
            }
        )
        return response.json()['message']

    def deleteRuleSet(self, ids):
        response = self.httpDeleteJson(
            url="{0}/projeto/grupo_regras".format(self.getServer()),
            postData={
                'grupo_regras_ids': ids
            }
        )
        return response.json()['message']
    
    def getQgisProject(self):
        response = self.httpGet(
            url="{0}/gerencia/projeto_qgis".format(self.getServer())
        )
        if response:
            return response.json()['dados']['projeto']
        return []

    def getLayersQgisProject(self, projectInProgress):
        params = '?em_andamento=true' if projectInProgress else ''
        response = self.httpGet(
            url="{0}/gerencia/view_acompanhamento{1}".format(self.getServer(), params)
        )
        if response:
            return response.json()['dados']
        return []

    def updateBlockedActivities(self):
        response = self.httpPut(
            url="{0}/gerencia/atividades_bloqueadas".format(self.getServer())
        )
        return response.json()['message']

    def synchronizeUserInformation(self):
        response = self.httpPut(
            url="{0}/usuarios/sincronizar".format(self.getServer())
        )
        return response.json()['message']

    def getUsersFromAuthService(self):
        response = self.httpGet(
            url="{0}/usuarios/servico_autenticacao".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return []
        
    def importUsersAuthService(self, usersIds):
        response = self.httpPostJson(
            url="{0}/usuarios".format(self.getServer()),
            postData={
                'usuarios': usersIds,
            }
        )
        return response.json()['message']

    def updateUsersPrivileges(self, usersData):
        response = self.httpPutJson(
            url="{0}/usuarios".format(self.getServer()),
            postData={
                'usuarios': usersData
            }    
        )
        return response.json()['message']

    def deleteActivities(self, activityIds):
        response = self.httpDeleteJson(
            url="{0}/projeto/atividades".format(self.getServer()),
            postData={
                'atividades_ids': activityIds
            }    
        )
        return response.json()['message']
    
    def createActivities(self, workspacesIds, stepId):
        response = self.httpPostJson(
            url="{0}/projeto/atividades".format(self.getServer()),
            postData={
                'unidade_trabalho_ids': workspacesIds,
                'etapa_id': stepId
            }    
        )
        return response.json()['message']

    def getDatabases(self):
        response = self.httpGet(
            url="{0}/projeto/banco_dados".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return []

    def getLayers(self):
        response = self.httpGet(
            url="{0}/projeto/configuracao/camadas".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return []

    def getAuthDatabase(self):
        response = self.httpGet(
            url="{0}/projeto/login".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return []

    def resetPrivileges(self):
        response = self.httpPut(
            url="{0}/gerencia/atividades/permissoes".format(self.getServer()),
            timeout=60*5
        )
        return response.json()['message']

    def importLayers(self, layersImported):
        response = self.httpPostJson(
            url="{0}/projeto/configuracao/camadas".format(self.getServer()),
            postData={
                'camadas': layersImported
            }    
        )
        return response.json()['message']

    def getLayers(self):
        response = self.httpGet(
            url="{0}/projeto/configuracao/camadas".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return []

    def deleteLayers(self, layersIds):
        response = self.httpDeleteJson(
            url="{0}/projeto/configuracao/camadas".format(self.getServer()),
            postData={
                'camadas_ids': layersIds
            }    
        )
        return response.json()['message']

    def updateLayers(self, layersData):
        response = self.httpPutJson(
            url="{0}/projeto/configuracao/camadas".format(self.getServer()),
            postData={
                'camadas': layersData
            }    
        )
        return response.json()['message']

    def getLots(self):
        response = self.httpGet(
            url="{0}/projeto/lote".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return []

    def alterBlock(self, workspacesIds, lotId):
        response = self.httpPutJson(
            url="{0}/projeto/unidade_trabalho/bloco".format(self.getServer()),
            postData={
                'unidade_trabalho_ids': workspacesIds,
                'bloco_id': lotId
            }    
        )
        return response.json()['message']

    def revokePrivileges(self, dbHost, dbPort, dbName):
        response = self.httpPostJson(
            url="{0}/gerencia/banco_dados/revogar_permissoes".format(self.getServer()),
            postData={
                "servidor" : dbHost,
                "porta" : int(dbPort),
                "banco" : dbName
            }
        )
        return response.json()['message']

    def getFmeServers(self):
        response = self.httpGet(
            url="{0}/projeto/configuracao/gerenciador_fme".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return []

    def createFmeServers(self, fmeServers):
        response = self.httpPostJson(
            url="{0}/projeto/configuracao/gerenciador_fme".format(self.getServer()),
            postData={
                'gerenciador_fme': fmeServers
            }   
        )
        return response.json()['message']

    def updateFmeServers(self, fmeServers):
        response = self.httpPutJson(
            url="{0}/projeto/configuracao/gerenciador_fme".format(self.getServer()),
            postData={
                'gerenciador_fme': fmeServers
            } 
        )
        return response.json()['message']

    def deleteFmeServers(self, fmeServersIds):
        response = self.httpDeleteJson(
            url="{0}/projeto/configuracao/gerenciador_fme".format(self.getServer()),
            postData={
                'servidores_id': fmeServersIds
            }  
        )
        return response.json()['message']

    def getFmeProfiles(self):
        response = self.httpGet(
            url="{0}/projeto/configuracao/perfil_fme".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return []

    def createFmeProfiles(self, fmeProfiles):
        response = self.httpPostJson(
            url="{0}/projeto/configuracao/perfil_fme".format(self.getServer()),
            postData={
                'perfis_fme': fmeProfiles
            }   
        )
        return response.json()['message']

    def updateFmeProfiles(self, fmeProfiles):
        response = self.httpPutJson(
            url="{0}/projeto/configuracao/perfil_fme".format(self.getServer()),
            postData={
                'perfis_fme': fmeProfiles
            } 
        )
        return response.json()['message']

    def deleteFmeProfiles(self, fmeProfilesIds):
        response = self.httpDeleteJson(
            url="{0}/projeto/configuracao/perfil_fme".format(self.getServer()),
            postData={
                'perfil_fme_ids': fmeProfilesIds
            }  
        )
        return response.json()['message']
    
    def getPhases(self):
        response = self.httpGet(
            url="{0}/projeto/fases".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return []

    def getSubphases(self):
        response = self.httpGet(
            url="{0}/projeto/subfases".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return []

    def getSteps(self):
        response = self.httpGet(
            url="{0}/projeto/etapas".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return []

    def deleteUserActivities(self, userId):
        response = self.httpDelete(
            url="{0}/perigo/atividades/usuario/{1}".format(self.getServer(), userId)
        )
        if response:
            return response.json()['message']
        return []

    def getInputTypes(self):
        response = self.httpGet(
            url="{0}/projeto/tipo_insumo".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return []

    def getInputGroups(self):
        response = self.httpGet(
            url="{0}/projeto/grupo_insumo".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return []

    def createInputGroups(self, inputGroups):
        response = self.httpPostJson(
            url="{0}/projeto/grupo_insumo".format(self.getServer()),
            postData={
                'grupo_insumos': inputGroups
            }   
        )
        return response.json()['message']

    def updateInputGroups(self, inputGroups):
        response = self.httpPutJson(
            url="{0}/projeto/grupo_insumo".format(self.getServer()),
            postData={
                'grupo_insumos': inputGroups
            } 
        )
        return response.json()['message']

    def deleteInputGroups(self, inputGroupIds):
        response = self.httpDeleteJson(
            url="{0}/projeto/grupo_insumo".format(self.getServer()),
            postData={
                'grupo_insumos_ids': inputGroupIds
            }  
        )
        return response.json()['message']

    def deleteAssociatedInputs(self, workspacesIds, inputGroupId):
        response = self.httpDeleteJson(
            url="{0}/projeto/insumos".format(self.getServer()),
            postData={
                'unidade_trabalho_ids': workspacesIds,
                'grupo_insumo_id': inputGroupId
            }  
        )
        return response.json()['message']

    def deleteWorkUnits(self, workspacesIds):
        response = self.httpDeleteJson(
            url="{0}/projeto/unidade_trabalho".format(self.getServer()),
            postData={
                'unidade_trabalho_ids': workspacesIds
            }  
        )
        return response.json()['message']

    def getProductionLines(self):
        def sortByName(elem):
            return elem['linha_producao']
        response = self.httpGet(
            url="{0}/projeto/linha_producao".format(self.getServer())
        )
        if response:
            productionLines = response.json()['dados']
            productionLines.sort(key=sortByName)
            return productionLines
        return []

    def createInputs(self, inputGroupCode, inputGroupId, inputs):
        response = self.httpPostJson(
            url="{0}/projeto/insumo".format(self.getServer()),
            postData={
                'tipo_insumo': inputGroupCode,
                'grupo_insumo': inputGroupId,
                'insumos': inputs
            }   
        )
        return response.json()['message']

    def createProducts(self, lotId, products):
        response = self.httpPostJson(
            url="{0}/projeto/produto".format(self.getServer()),
            postData={
                'lote_id': lotId,
                'produtos': products
            }   
        )
        return response.json()['message']

    def getRoutines(self):
        response = self.httpGet(
            url="{0}/projeto/tipo_rotina".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return []

    def getAssociationStrategies(self):
        response = self.httpGet(
            url="{0}/projeto/tipo_estrategia_associacao".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return []

    def associateInputs(self, workspacesIds, inputGroupId, associationStrategyId, defaultPath):
        response = self.httpPostJson(
            url="{0}/projeto/unidade_trabalho/insumos".format(self.getServer()),
            postData={
                'unidade_trabalho_ids': workspacesIds,
                'grupo_insumo_id': inputGroupId,
                'estrategia_id': associationStrategyId,
                'caminho_padrao': defaultPath
            }   
        )
        return response.json()['message']

    def loadWorkUnit(self, lotId, subphaseIds, workUnits):
        response = self.httpPostJson(
            url="{0}/projeto/unidade_trabalho".format(self.getServer()),
            postData={
                'lote_id': lotId,
                'subfase_ids': subphaseIds,
                'unidades_trabalho': workUnits
            }   
        )
        return response.json()['message']

    def getProductionData(self):
        response = self.httpGet(
            url="{0}/projeto/dado_producao".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return []

    def getProductionDataType(self):
        response = self.httpGet(
            url="{0}/projeto/tipo_dado_producao".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return []

    def copyWorkUnit(self, workspacesIds, stepsIds, associateInputs):
        response = self.httpPostJson(
            url="{0}/projeto/unidade_trabalho/copiar".format(self.getServer()),
            postData={
                'unidade_trabalho_ids': workspacesIds,
                'subfase_ids': stepsIds,
                'associar_insumos': associateInputs
            },
            timeout=TIMEOUT
        )
        return response.json()['message']

    def getModelProfiles(self):
        response = self.httpGet(
            url="{0}/projeto/configuracao/perfil_modelo".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return []

    def createModelProfiles(self, data):
        response = self.httpPostJson(
            url="{0}/projeto/configuracao/perfil_modelo".format(self.getServer()),
            postData={
                'perfis_modelo': data
            }   
        )
        return response.json()['message']

    def updateModelProfiles(self, data):
        response = self.httpPutJson(
            url="{0}/projeto/configuracao/perfil_modelo".format(self.getServer()),
            postData={
                'perfis_modelo': data
            }    
        )
        return response.json()['message']

    def deleteModelProfiles(self, ids):
        response = self.httpDeleteJson(
            url="{0}/projeto/configuracao/perfil_modelo".format(self.getServer()),
            postData={
                "perfil_modelo_ids" : ids,
            }
        )
        if response:
            return response.json()['message']
        return []

    def getRuleProfiles(self):
        response = self.httpGet(
            url="{0}/projeto/configuracao/perfil_regras".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return []

    def createRuleProfiles(self, data):
        response = self.httpPostJson(
            url="{0}/projeto/configuracao/perfil_regras".format(self.getServer()),
            postData={
                'perfis_regras': data
            }   
        )
        return response.json()['message']

    def updateRuleProfiles(self, data):
        response = self.httpPutJson(
            url="{0}/projeto/configuracao/perfil_regras".format(self.getServer()),
            postData={
                'perfis_regras': data
            }    
        )
        return response.json()['message']

    def deleteRuleProfiles(self, ids):
        response = self.httpDeleteJson(
            url="{0}/projeto/configuracao/perfil_regras".format(self.getServer()),
            postData={
                "perfil_regras_ids" : ids,
            }
        )
        if response:
            return response.json()['message']
        return []

    def getStyleProfiles(self):
        response = self.httpGet(
            url="{0}/projeto/configuracao/perfil_estilos".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return []

    def createStyleProfiles(self, data):
        response = self.httpPostJson(
            url="{0}/projeto/configuracao/perfil_estilos".format(self.getServer()),
            postData={
                'perfis_estilos': data
            }   
        )
        return response.json()['message']

    def updateStyleProfiles(self, data):
        response = self.httpPutJson(
            url="{0}/projeto/configuracao/perfil_estilos".format(self.getServer()),
            postData={
                'perfis_estilos': data
            }    
        )
        return response.json()['message']

    def deleteStyleProfiles(self, ids):
        response = self.httpDeleteJson(
            url="{0}/projeto/configuracao/perfil_estilos".format(self.getServer()),
            postData={
                "perfil_estilos_ids" : ids,
            }
        )
        if response:
            return response.json()['message']
        return []

    def getProjects(self):
        response = self.httpGet(
            url="{0}/projeto/projetos".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return []

    def getStepType(self):
        response = self.httpGet(
            url="{0}/projeto/tipo_etapa".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return []

    def getProfileProductionStep(self):
        response = self.httpGet(
            url="{0}/gerencia/perfil_producao_etapa".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return []

    def createProfileProductionStep(self, data):
        response = self.httpPostJson(
            url="{0}/gerencia/perfil_producao_etapa".format(self.getServer()),
            postData={
                'perfil_producao_etapa': data
            }   
        )
        return response.json()['message']

    def updateProfileProductionStep(self, data):
        response = self.httpPutJson(
            url="{0}/gerencia/perfil_producao_etapa".format(self.getServer()),
            postData={
                'perfil_producao_etapa': data
            }    
        )
        return response.json()['message']

    def deleteProfileProductionStep(self, data):
        response = self.httpDeleteJson(
            url="{0}/gerencia/perfil_producao_etapa".format(self.getServer()),
            postData={
                "perfil_producao_etapa_ids" : data,
            }
        )
        if response:
            return response.json()['message']
        return []

    def getUserProfileProduction(self):
        response = self.httpGet(
            url="{0}/gerencia/perfil_producao_operador".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return []

    def createUserProfileProduction(self, data):
        response = self.httpPostJson(
            url="{0}/gerencia/perfil_producao_operador".format(self.getServer()),
            postData={
                'perfil_producao_operador': data
            }   
        )
        return response.json()['message']

    def updateUserProfileProduction(self, data):
        response = self.httpPutJson(
            url="{0}/gerencia/perfil_producao_operador".format(self.getServer()),
            postData={
                'perfil_producao_operador': data
            }    
        )
        return response.json()['message']

    def deleteUserProfileProduction(self, data):
        response = self.httpDeleteJson(
            url="{0}/gerencia/perfil_producao_operador".format(self.getServer()),
            postData={
                "perfil_producao_operador_ids" : data,
            }
        )
        if response:
            return response.json()['message']
        return []

    def getUserBlocks(self):
        response = self.httpGet(
            url="{0}/gerencia/perfil_bloco_operador".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return []

    def createUserBlockProduction(self, data):
        response = self.httpPostJson(
            url="{0}/gerencia/perfil_bloco_operador".format(self.getServer()),
            postData={
                'perfil_bloco_operador': data
            }   
        )
        return response.json()['message']

    def updateUserBlockProduction(self, data):
        response = self.httpPutJson(
            url="{0}/gerencia/perfil_bloco_operador".format(self.getServer()),
            postData={
                'perfil_bloco_operador': data
            }    
        )
        return response.json()['message']

    def deleteUserBlockProduction(self, data):
        response = self.httpDeleteJson(
            url="{0}/gerencia/perfil_bloco_operador".format(self.getServer()),
            postData={
                "perfil_bloco_operador_ids" : data,
            }
        )
        if response:
            return response.json()['message']
        return []

    def getBlocks(self):
        response = self.httpGet(
            url="{0}/projeto/bloco".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return []

    def createMenus(self, data):
        response = self.httpPostJson(
            url="{0}/projeto/menus".format(self.getServer()),
            postData={
                'menus': data
            }   
        )
        return response.json()['message']

    def updateMenus(self, data):
        response = self.httpPutJson(
            url="{0}/projeto/menus".format(self.getServer()),
            postData={
                'menus': data
            }    
        )
        return response.json()['message']

    def deleteMenus(self, data):
        response = self.httpDeleteJson(
            url="{0}/projeto/menus".format(self.getServer()),
            postData={
                "menus_ids" : data,
            }
        )
        if response:
            return response.json()['message']
        return []

    def getMenus(self):
        response = self.httpGet(
            url="{0}/projeto/menus".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return []

    def getMenuProfiles(self):
        response = self.httpGet(
            url="{0}/projeto/configuracao/perfil_menu".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return []
        
    def createMenuProfiles(self, data):
        response = self.httpPostJson(
             url="{0}/projeto/configuracao/perfil_menu".format(self.getServer()),
            postData={
                'perfis_menu': data
            }   
        )
        return response.json()['message']

    def updateMenuProfiles(self, data):
        response = self.httpPutJson(
            url="{0}/projeto/configuracao/perfil_menu".format(self.getServer()),
            postData={
                'perfis_menu': data
            }    
        )
        return response.json()['message']

    def deleteMenuProfiles(self, data):
        response = self.httpDeleteJson(
             url="{0}/projeto/configuracao/perfil_menu".format(self.getServer()),
            postData={
                "perfil_menu_ids" : data,
            }
        )
        if response:
            return response.json()['message']
        return []

    def createAllActivities(self, loteId):
        response = self.httpPostJson(
            url="{0}/projeto/atividades/todas".format(self.getServer()),
            postData={
                'lote_id': loteId
            },
            timeout=TIMEOUT
        )
        return response.json()['message']

    def createDefaultStep(self, padraoCq, phaseId, lotId):
        response = self.httpPostJson(
            url="{0}/projeto/etapas/padrao".format(self.getServer()),
            postData={
                'padrao_cq': padraoCq,
                'fase_id': phaseId,
                'lote_id': lotId,
            },
            timeout=TIMEOUT
        )
        return response.json()['message']

    def deleteWorkUnitActivities(self, workUnitIds):
        response = self.httpDeleteJson(
            url="{0}/projeto/unidade_trabalho/atividades".format(self.getServer()),
            postData={
                'unidade_trabalho_ids': workUnitIds
            }
        )
        return response.json()['message']

    def updateLayersQgisProject(self):
        response = self.httpPut(
            url="{0}/gerencia/refresh_views".format(self.getServer())
        )
        return response.json()['message']

    def createProjects(self, data):
        response = self.httpPostJson(
            url="{0}/projeto/projetos".format(self.getServer()),
            postData={
                'projetos': data
            },
            timeout=TIMEOUT
        )
        return response.json()['message']

    def deleteProjects(self, data):
        response = self.httpDeleteJson(
            url="{0}/projeto/projetos".format(self.getServer()),
            postData={
                'projeto_ids': data
            }
        )
        return response.json()['message']

    def updateProjects(self, data):
        response = self.httpPutJson(
            url="{0}/projeto/projetos".format(self.getServer()),
            postData={
                'projetos': data
            }    
        )
        return response.json()['message']

    def createLots(self, data):
        response = self.httpPostJson(
            url="{0}/projeto/lote".format(self.getServer()),
            postData={
                'lotes': data
            },
            timeout=TIMEOUT
        )
        return response.json()['message']

    def deleteLots(self, data):
        response = self.httpDeleteJson(
            url="{0}/projeto/lote".format(self.getServer()),
            postData={
                'lote_ids': data
            }
        )
        return response.json()['message']

    def updateLots(self, data):
        response = self.httpPutJson(
            url="{0}/projeto/lote".format(self.getServer()),
            postData={
                'lotes': data
            }    
        )
        return response.json()['message']

    def createBlocks(self, data):
        response = self.httpPostJson(
            url="{0}/projeto/bloco".format(self.getServer()),
            postData={
                'blocos': data
            },
            timeout=TIMEOUT
        )
        return response.json()['message']

    def deleteBlocks(self, data):
        response = self.httpDeleteJson(
            url="{0}/projeto/bloco".format(self.getServer()),
            postData={
                'bloco_ids': data
            }
        )
        return response.json()['message']

    def updateBlocks(self, data):
        response = self.httpPutJson(
            url="{0}/projeto/bloco".format(self.getServer()),
            postData={
                'blocos': data
            }    
        )
        return response.json()['message']

    def createProductionData(self, data):
        response = self.httpPostJson(
            url="{0}/projeto/dado_producao".format(self.getServer()),
            postData={
                'dado_producao': data
            },
            timeout=TIMEOUT
        )
        return response.json()['message']

    def deleteProductionData(self, data):
        response = self.httpDeleteJson(
            url="{0}/projeto/dado_producao".format(self.getServer()),
            postData={
                'dado_producao_ids': data
            }
        )
        return response.json()['message']

    def updateProductionData(self, data):
        response = self.httpPutJson(
            url="{0}/projeto/dado_producao".format(self.getServer()),
            postData={
                'dado_producao': data
            }    
        )
        return response.json()['message']

    def createBlockInputs(self, data):
        response = self.httpPostJson(
            url="{0}/projeto/bloco/insumos".format(self.getServer()),
            postData=data
        )
        return response.json()['message']

    def revokeUserPrivileges(self, data):
        response = self.httpPostJson(
            url="{0}/gerencia/banco_dados/revogar_permissoes_usuario".format(self.getServer()),
            postData=data
        )
        return response.json()['message']

    def getQgisVersion(self):
        response = self.httpGet(
            url="{0}/gerencia/versao_qgis".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return []

    def updateQgisVersion(self, data):
        response = self.httpPutJson(
            url="{0}/gerencia/versao_qgis".format(self.getServer()),
            postData=data
        )
        return response.json()['message']

    def getProfileFinalization(self):
        response = self.httpGet(
            url="{0}/projeto/configuracao/perfil_requisito_finalizacao".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return []

    def updateProfileFinalization(self, data):
        response = self.httpPutJson(
            url="{0}/projeto/configuracao/perfil_requisito_finalizacao".format(self.getServer()),
            postData={
                'perfis_requisito': data
            }
        )
        return response.json()['message']

    def createProfileFinalization(self, data):
        response = self.httpPostJson(
            url="{0}/projeto/configuracao/perfil_requisito_finalizacao".format(self.getServer()),
            postData={
                'perfis_requisito': data
            },
            timeout=TIMEOUT
        )
        return response.json()['message']

    def deleteProfileFinalization(self, data):
        response = self.httpDeleteJson(
            url="{0}/projeto/configuracao/perfil_requisito_finalizacao".format(self.getServer()),
            postData={
                'perfil_requisito_ids': data
            }
        )
        return response.json()['message']

    def getAlias(self):
        response = self.httpGet(
            url="{0}/projeto/alias".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return []

    def updateAlias(self, data):
        response = self.httpPutJson(
            url="{0}/projeto/alias".format(self.getServer()),
            postData={
                'alias': data
            }
        )
        return response.json()['message']

    def createAlias(self, data):
        response = self.httpPostJson(
            url="{0}/projeto/alias".format(self.getServer()),
            postData={
                'alias': data
            },
            timeout=TIMEOUT
        )
        return response.json()['message']

    def deleteAlias(self, data):
        response = self.httpDeleteJson(
            url="{0}/projeto/alias".format(self.getServer()),
            postData={
                'alias_ids': data
            }
        )
        return response.json()['message']

    def getAliasProfile(self):
        response = self.httpGet(
            url="{0}/projeto/configuracao/perfil_alias".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return []

    def updateAliasProfile(self, data):
        response = self.httpPutJson(
            url="{0}/projeto/configuracao/perfil_alias".format(self.getServer()),
            postData={
                'perfis_alias': data
            }
        )
        return response.json()['message']

    def createAliasProfile(self, data):
        response = self.httpPostJson(
            url="{0}/projeto/configuracao/perfil_alias".format(self.getServer()),
            postData={
                'perfis_alias': data
            },
            timeout=TIMEOUT
        )
        return response.json()['message']

    def deleteAliasProfile(self, data):
        response = self.httpDeleteJson(
            url="{0}/projeto/configuracao/perfil_alias".format(self.getServer()),
            postData={
                'perfis_alias_ids': data
            }
        )
        return response.json()['message']

    def getPlugins(self):
        response = self.httpGet(
            url="{0}/gerencia/plugins".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return []

    def updatePlugins(self, data):
        response = self.httpPutJson(
            url="{0}/gerencia/plugins".format(self.getServer()),
            postData={
                'plugins': data
            }
        )
        return response.json()['message']

    def createPlugins(self, data):
        response = self.httpPostJson(
            url="{0}/gerencia/plugins".format(self.getServer()),
            postData={
                'plugins': data
            },
            timeout=TIMEOUT
        )
        return response.json()['message']

    def deletePlugins(self, data):
        response = self.httpDeleteJson(
            url="{0}/gerencia/plugins".format(self.getServer()),
            postData={
                'plugins_ids': data
            }
        )
        return response.json()['message']

    def getShortcuts(self):
        response = self.httpGet(
            url="{0}/gerencia/atalhos".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return []

    def updateShortcuts(self, data):
        response = self.httpPutJson(
            url="{0}/gerencia/atalhos".format(self.getServer()),
            postData={
                'qgis_shortcuts': data
            }
        )
        return response.json()['message']

    def createShortcuts(self, data):
        response = self.httpPostJson(
            url="{0}/gerencia/atalhos".format(self.getServer()),
            postData={
                'qgis_shortcuts': data
            },
            timeout=TIMEOUT
        )
        return response.json()['message']

    def deleteShortcuts(self, data):
        response = self.httpDeleteJson(
            url="{0}/gerencia/atalhos".format(self.getServer()),
            postData={
                'qgis_shortcuts_ids': data
            }
        )
        return response.json()['message']

    def getShowTypes(self):
        response = self.httpGet(
            url="{0}/projeto/tipo_exibicao".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return []

    def getLineages(self):
        response = self.httpGet(
            url="{0}/projeto/configuracao/perfil_linhagem".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return []

    def updateLineages(self, data):
        response = self.httpPutJson(
            url="{0}/projeto/configuracao/perfil_linhagem".format(self.getServer()),
            postData={
                'perfis_linhagem': data
            }
        )
        return response.json()['message']

    def createLineages(self, data):
        response = self.httpPostJson(
            url="{0}/projeto/configuracao/perfil_linhagem".format(self.getServer()),
            postData={
                'perfis_linhagem': data
            },
            timeout=TIMEOUT
        )
        return response.json()['message']

    def deleteLineages(self, data):
        response = self.httpDeleteJson(
            url="{0}/projeto/configuracao/perfil_linhagem".format(self.getServer()),
            postData={
                'perfil_linhagem_ids': data
            }
        )
        return response.json()['message']

    def getProblemActivity(self):
        response = self.httpGet(
            url="{0}/gerencia/problema_atividade".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return []

    def updateProblemActivity(self, data):
        response = self.httpPutJson(
            url="{0}/gerencia/problema_atividade".format(self.getServer()),
            postData={
                'problema_atividade': data
            }
        )
        return response.json()['message']