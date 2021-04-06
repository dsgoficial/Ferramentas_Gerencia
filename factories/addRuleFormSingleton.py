from Ferramentas_Gerencia.widgets.addRuleForm  import AddRuleForm

class AddRuleFormSingleton:

    addRuleForm = None

    @staticmethod
    def getInstance(widgetExpression, parent):
        if not AddRuleFormSingleton.addRuleForm:
            AddRuleFormSingleton.addRuleForm = AddRuleForm(widgetExpression, parent)
        return AddRuleFormSingleton.addRuleForm