from qgis.utils import iface
from qgis import gui, core
from PyQt5 import QtGui, QtCore
from qgis.core import QgsGeometry
from qgis.PyQt.QtCore import QVariant
import math

from Ferramentas_Gerencia.qgis.interfaces.IMapFunctions import IMapFunctions

class GeometryToEwkt(IMapFunctions):

    def __init__(self, transformGeometryCrsFunction):
        super(GeometryToEwkt, self).__init__()
        self.transformGeometryCrsFunction = transformGeometryCrsFunction

    def run(self, geometry, crsIdFrom, crsIdTo):
        geom = self.transformGeometryCrsFunction.run(geometry, crsIdFrom, crsIdTo)
        return 'SRID={0};{1}'.format(crsIdTo.split(':')[1], geom.asWkt())