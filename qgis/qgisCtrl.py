from Ferramentas_Gerencia.qgis.interfaces.IQgisCtrl import IQgisCtrl

from Ferramentas_Gerencia.qgis.factory.qgisApiBuilder import QgisApiBuilder
from Ferramentas_Gerencia.qgis.factory.qgisApiDirector import QgisApiDirector

from Ferramentas_Gerencia.qgis.factory.pluginsViewManagerSingleton import PluginsViewManagerSingleton
from Ferramentas_Gerencia.qgis.factory.selectFieldOptionSingleton import SelectFieldOptionSingleton
from Ferramentas_Gerencia.qgis.factory.widgetsFactoryMethod import WidgetsFactoryMethod
from Ferramentas_Gerencia.qgis.factory.mapToolsFactoryMethod import MapToolsFactoryMethod
from Ferramentas_Gerencia.qgis.factory.mapFunctionsFactoryMethod import MapFunctionsFactoryMethod
from Ferramentas_Gerencia.qgis.factory.externalPluginsFactoryMethod import ExternalPluginsFactoryMethod

class QgisCtrl(IQgisCtrl):

    def __init__(self, iface):
        super(QgisCtrl, self).__init__()
        self.iface = iface
        self.apiQGis = self.loadApiQgis()
        self.selectFieldView = SelectFieldOptionSingleton.getInstance()
        self.pluginViewQgis = PluginsViewManagerSingleton.getInstance()

    def loadApiQgis(self):
        apiGisDirector = QgisApiDirector()
        apiQgisBuilder = QgisApiBuilder()
        apiGisDirector.constructQgisApi(apiQgisBuilder)
        return apiQgisBuilder.getResult()

    def setProjectVariable(self, key, value):
        self.apiQGis.getStorages().setProjectVariable(key, value)

    def getProjectVariable(self, key):
        return self.apiQGis.getStorages().getProjectVariable(key)

    def setSettingsVariable(self, key, value):
        self.apiQGis.getStorages().setSettingsVariable(key, value)

    def getSettingsVariable(self, key):
        return self.apiQGis.getStorages().getSettingsVariable(key)

    def getVersion(self):
        return self.apiQGis.getVersion()
    
    def getPluginsVersions(self):
        return self.apiQGis.getPluginsVersions()

    def addDockWidget(self, dockWidget):
        self.pluginViewQgis.addDockWidget(dockWidget)

    def removeDockWidget(self, dockWidget):
        self.pluginViewQgis.removeDockWidget(dockWidget)

    def getFieldValuesFromLayer(self, layerName, fieldName, allSelection, chooseAttribute):
        layers = self.apiQGis.getLayers()
        if not layers.isActiveLayer(layerName):
            return []
        selectedFeatures = layers.getActiveLayerSelections()
        if not selectedFeatures:
            return []
        if not(allSelection) and len(selectedFeatures) > 1:
            raise Exception("Seleciona apenas uma feição!")
        if chooseAttribute:
            fieldsNames = layers.getFieldsNamesFromSelection(filterText=fieldName)
            fieldName = self.selectFieldView.chooseField(fieldsNames)
        if not fieldName:
            return []
        return layers.getFieldValuesFromSelections(fieldName)

    def getQmlStyleFromLayersTreeSelection(self):
        layers = self.apiQGis.getLayers().getLayersTreeSelection()
        stylesData = self.apiQGis.getStyles().getQmlStyleFromLayers(layers)
        return stylesData

    def applyStylesOnLayers(self, stylesData):
        for styleData in stylesData:
            layers = self.apiQGis.getLayers().findVectorLayer(
                    styleData['f_table_schema'],
                    styleData['f_table_name']
                )
            if not layers:
                continue
            for layer in layers:
                self.apiQGis.getStyles().setQmlStyleToLayer(
                    layer, 
                    styleData['styleqml']
                )

    def getWidgetExpression(self):
        return WidgetsFactoryMethod().getWidget('lineEditExpression')

    def activeMapToolByToolName(self, toolName):
        self.mapTool = MapToolsFactoryMethod.getMapTool(toolName)
        self.mapTool.start()

    def addLayerGroup(self, groupName, parentGroup=None):
        return self.apiQGis.getLayers().addLayerGroup(groupName, parentGroup)

    def loadLayer(self, dbName, dbHost, dbPort, dbUser, dbPassword, dbSchema, dbTable, groupParent=None):
        self.apiQGis.getLayers().loadPostgresLayer(dbName, dbHost, dbPort, dbUser, dbPassword, dbSchema, dbTable, groupParent)

    def startSapFP(self, activityData):
        prodTool = ExternalPluginsFactoryMethod().getPlugin('ferramentaProducao')
        prodTool.run(activityData)

    def getActiveLayerAttribute(self, featureId, fieldName):
        return self.apiQGis.getLayers().getActiveLayerAttribute(featureId, fieldName)

    def generateWorkUnit(self, layerName, size, overlay, deplace, prefixName, onlySelected):
        layersApi = self.apiQGis.getLayers()
        createTemporaryLayerFunction = MapFunctionsFactoryMethod.getMapFunctions('createTemporaryLayer')
        transformGeometryCrsFunction = MapFunctionsFactoryMethod.getMapFunctions('transformGeometryCrs')
        unionGeometriesFunction = MapFunctionsFactoryMethod.getMapFunctions('unionGeometries')
        deagregatorFunction = MapFunctionsFactoryMethod.getMapFunctions('deagregator')
        buildGridFunction = MapFunctionsFactoryMethod.getMapFunctions('buildGrid')
        generateUTFunction = MapFunctionsFactoryMethod.getMapFunctions('generateUT')
        generateUTFunction.run(
            layerName,
            size,
            prefixName,
            overlay, 
            deplace,
            onlySelected,
            layersApi,
            createTemporaryLayerFunction,
            transformGeometryCrsFunction,
            unionGeometriesFunction,
            deagregatorFunction,
            buildGridFunction
        )