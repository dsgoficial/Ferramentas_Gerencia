from Ferramentas_Gerencia.modules.qgis.externalPlugins.ferramentaProducao  import FerramentaProducao

class ExternalPluginsFactoryMethod:

    def getPlugin(self, pluginName):
        pluginNames = {
            'ferramentaProducao': FerramentaProducao
        }
        return pluginNames[pluginName]()
       