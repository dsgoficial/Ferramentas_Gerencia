from Ferramentas_Gerencia.widgets.managementModels  import ManagementModels

class ManagementModelsSingleton:

    managementModels = None

    @staticmethod
    def getInstance(controller):
        if not ManagementModelsSingleton.managementModels:
            ManagementModelsSingleton.managementModels = ManagementModels(controller)
        return ManagementModelsSingleton.managementModels