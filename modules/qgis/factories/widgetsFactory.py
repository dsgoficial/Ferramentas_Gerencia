from SAP_Gerente.modules.qgis.widgets.lineEditExpression  import LineEditExpression
from SAP_Gerente.modules.qgis.widgets.comboBoxMapLayer  import ComboBoxMapLayer
from SAP_Gerente.modules.qgis.widgets.comboBoxPolygonLayer  import ComboBoxPolygonLayer
from SAP_Gerente.modules.qgis.factories.mapFunctionsFactory import MapFunctionsFactory
from SAP_Gerente.modules.qgis.widgets.comboBoxProjection import ComboBoxProjection

class WidgetsFactory:

    def __init__(self,
            mapFunctionsFactory=MapFunctionsFactory()
        ):
        self.mapFunctionsFactory = mapFunctionsFactory

    def createComboBoxMapLayer(self):
        return ComboBoxMapLayer(
            transformGeometryCrsFunction=self.mapFunctionsFactory.getMapFunction('transformGeometryCrs')
        )

    def createComboBoxPolygonLayer(self):
        return ComboBoxPolygonLayer(
            transformGeometryCrsFunction=self.mapFunctionsFactory.getMapFunction('transformGeometryCrs')
        )

    def getWidget(self, widgetName):
        widgetNames = {
            'lineEditExpression' : LineEditExpression,
            'comboBoxMapLayer' : self.createComboBoxMapLayer,
            'comboBoxPolygonLayer' : self.createComboBoxPolygonLayer,
            'comboBoxProjection': ComboBoxProjection
        }
        return widgetNames[widgetName]()
       