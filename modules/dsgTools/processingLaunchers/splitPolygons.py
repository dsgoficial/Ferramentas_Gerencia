from SAP_Gerente.modules.dsgTools.processingLaunchers.processing import Processing
from qgis import core, gui
import processing
import json

class SplitPolygons(Processing):
    
    def __init__(self):
        super(SplitPolygons, self).__init__()
        self.processingId = 'dsgtools:splitpolygons'
        
    def getParameters(self, parameters):
        return {
            'PARAM': parameters['param'],
            'OVERLAP': parameters['overlap'],
            'INPUT' : parameters['layer'],
            'OUTPUT': 'TEMPORARY_OUTPUT'
        }