class Feature:
    def __init__(self,scenario =None,flow_chart =None,process =None,input=None,output=None,role = None):
        self.scenario = scenario
        self.flow_chart = flow_chart
        self.process = process
        self.input = input
        self.output = output
        self.role = role

    def __str__(self):
        return f"Scenario: {self.scenario}, Flow Chart: {self.flow_chart}, Process: {self.process}, Input: {self.input}, Output: {self.output}, Role: {self.role}"