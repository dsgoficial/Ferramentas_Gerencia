from SAP_Gerente.modules.qgis.interfaces.IQgisCtrl import IQgisCtrl
from SAP_Gerente.modules.qgis.factories.qgisApiSingleton import QgisApiSingleton
from SAP_Gerente.modules.qgis.factories.selectFieldOptionSingleton import SelectFieldOptionSingleton
from SAP_Gerente.modules.qgis.factories.widgetsFactory import WidgetsFactory
from SAP_Gerente.modules.qgis.factories.mapToolFactory import MapToolFactory
from SAP_Gerente.modules.qgis.factories.mapFunctionsFactory import MapFunctionsFactory
from SAP_Gerente.modules.qgis.factories.externalPluginsFactoryMethod import ExternalPluginsFactoryMethod

from qgis import gui, core
from qgis.utils import plugins, iface
from qgis.PyQt.QtWidgets import QToolBar

class QgisCtrl(IQgisCtrl):

    def __init__(self, 
            apiQGis=QgisApiSingleton.getInstance(),
            selectFieldView=SelectFieldOptionSingleton.getInstance(),
            widgetsFactory=WidgetsFactory(),
            mapFunctionsFactory=MapFunctionsFactory(),
            mapToolFactory=MapToolFactory()
        ):
        super(QgisCtrl, self).__init__()
        self.apiQGis = apiQGis
        self.widgetsFactory = widgetsFactory
        self.selectFieldView = selectFieldView
        self.mapFunctionsFactory = mapFunctionsFactory
        self.mapToolFactory = mapToolFactory
        self.customToolBar = None

    def isValidEpsg(self, epsgStr):
        try:
            epsgCode = int(epsgStr)
        except ValueError:
            return False
        crs = core.QgsCoordinateReferenceSystem(f"EPSG:{epsgCode}")
        return crs.isValid()

    def getEvents(self):
        return {
            'ReadProject': core.QgsProject.instance().readProject,
            'SaveAllEdits': iface.actionSaveAllEdits().triggered,
            'SaveActiveLayerEdits': iface.actionSaveActiveLayerEdits().triggered,
            'MessageLog': core.QgsApplication.messageLog().messageReceived,
            'LayersAdded': core.QgsProject.instance().layersAdded,
            'NewProject': iface.newProjectCreated,
        }

    def on(self, event, callback):
        self.getEvents()[event].connect(callback)
        return True

    def off(self, event, callback):
        try:
            self.getEvents()[event].disconnect(callback)
            return True
        except:
            return False

    def load(self):
        for toolbar in iface.mainWindow().findChildren(QToolBar):
            if toolbar.objectName() == "SAP":
                self.customToolBar = toolbar
                break

        if not self.customToolBar:
            self.customToolBar = QToolBar('SAP', iface.mainWindow())
            self.customToolBar.setObjectName('SAP')
            iface.addToolBar(self.customToolBar)

    def addActionToolBar(self, action):
        self.customToolBar.addAction(action)

    def removeActionToolBar(self, action):
        self.customToolBar.removeAction(action)

    def removeToolBar(self):
        if not self.customToolBar.actions():
            iface.mainWindow().removeToolBar(self.customToolBar)
            self.customToolBar.deleteLater()

    def createAction(self, name, iconPath, callback, shortcutKeyName='', checkable=False):
        return self.apiQGis.createAction(name, iconPath, callback, shortcutKeyName, checkable)

    def addMenuBar(self, name):
        return self.apiQGis.addMenuBar(name)

    def setProjectVariable(self, key, value):
        self.apiQGis.setProjectVariable(key, value)

    def getProjectVariable(self, key):
        return self.apiQGis.getProjectVariable(key)

    def setSettingsVariable(self, key, value):
        self.apiQGis.setSettingsVariable(key, value)

    def getSettingsVariable(self, key):
        return self.apiQGis.getSettingsVariable(key)

    def getVersion(self):
        return self.apiQGis.getVersion()

    def getMainWindow(self):
        return self.apiQGis.getMainWindow()    
    
    def getPluginsVersions(self):
        return self.apiQGis.getPluginsVersions()

    def addDockWidget(self, dockWidget):
        self.apiQGis.addDockWidget(dockWidget)

    def removeDockWidget(self, dockWidget):
        self.apiQGis.removeDockWidget(dockWidget)

    def getFieldValuesFromLayer(self, layerName, fieldName, allSelection, chooseAttribute):
        if not self.apiQGis.isActiveLayer(layerName):
            return []
        selectedFeatures = self.apiQGis.getActiveLayerSelections()
        if not selectedFeatures:
            return []
        if not(allSelection) and len(selectedFeatures) > 1:
            raise Exception("Seleciona apenas uma feição!")
        if chooseAttribute:
            fieldsNames = self.apiQGis.getFieldsNamesFromSelection(filterText=fieldName)
            fieldName = self.selectFieldView.chooseField(fieldsNames)
        if not fieldName:
            return []
        return self.apiQGis.getFieldValuesFromSelections(fieldName)

    def getQmlStyleFromLayersTreeSelection(self):
        layers = self.apiQGis.getLayersTreeSelection()
        stylesData = self.getQmlStyleFromLayers(layers)
        return stylesData

    def getQmlStyleFromLayers(self, layers):
        return self.apiQGis.getQmlStyleFromLayers(layers)

    def applyStylesOnLayers(self, stylesData):
        for styleData in stylesData:
            layers = self.apiQGis.findVectorLayer(
                    styleData['f_table_schema'],
                    styleData['f_table_name']
                )
            if not layers:
                continue
            for layer in layers:
                self.apiQGis.setQmlStyleToLayer(
                    layer, 
                    styleData['styleqml']
                )

    def getWidgetByName(self, widgetName):
        return self.widgetsFactory.getWidget(widgetName)

    def activeMapToolByToolName(self, toolName):
        self.mapTool = self.mapToolFactory.getMapTool(toolName)
        self.mapTool.start()

    def addLayerGroup(self, groupName, parentGroup=None):
        return self.apiQGis.addLayerGroup(groupName, parentGroup)

    def loadLayer(self, dbName, dbHost, dbPort, dbUser, dbPassword, dbSchema, dbTable, name, groupParent=None):
        return self.apiQGis.loadPostgresLayer(dbName, dbHost, dbPort, dbUser, dbPassword, dbSchema, dbTable, name, groupParent)

    def startSapFP(self, sapCtrl):
        prodTool = ExternalPluginsFactoryMethod().getPlugin('ferramentaProducao')
        prodTool.run(sapCtrl)

    def getActiveLayerAttribute(self, featureId, fieldName):
        return self.apiQGis.getActiveLayerAttribute(featureId, fieldName)

    def generateWorkUnit(
            self, 
            layerName, 
            size, 
            overlay, 
            deplace, 
            onlySelected,
            epsg,
            blockId,
            productionDataId
        ):
        generateUTFunction = self.mapFunctionsFactory.getMapFunction('generateUT')
        generateUTFunction.run(
            layerName,
            size,
            overlay, 
            deplace,
            onlySelected,
            epsg,
            blockId,
            productionDataId
        )


    def generateWorkUnitSimple(
            self, 
            layer,
            epsg,
            blockId,
            productionDataId
        ):
        generateUTFunction = self.mapFunctionsFactory.getMapFunction('generateUTSimple')
        return generateUTFunction.run(
            layer,
            epsg,
            blockId,
            productionDataId
        )

    def getMapCrsId(self):
        self.apiQGis.getMapCrsId()

    def generateMetadataLayer(self):
        generateMetadataLayer = self.mapFunctionsFactory.getMapFunction('generateMetadataLayer')
        return generateMetadataLayer.run()

    def generateProductLayer(self, data):
        generateProductLayer = self.mapFunctionsFactory.getMapFunction('generateProductLayer')
        return generateProductLayer.run(data)

    def dumpFeatures(self, layer, onlySelected):
        dumpFeaturesFunction = self.mapFunctionsFactory.getMapFunction('dumpFeatures')
        return dumpFeaturesFunction.run(layer, onlySelected)

    def geometryToEwkt(self, geometry, crsIdFrom, crsIdTo):
        geometryToEwktFunction = self.mapFunctionsFactory.getMapFunction('geometryToEwkt')
        return geometryToEwktFunction.run(geometry, crsIdFrom, crsIdTo)

    def getSelectedLayersTreeView(self):
        return self.apiQGis.getSelectedLayersTreeView()

    def createScreens(self, primaryLayerNames, secundaryLayerNames):
        createScreens = self.mapFunctionsFactory.getMapFunction('createNewMapView')
        return createScreens.run( primaryLayerNames, secundaryLayerNames )