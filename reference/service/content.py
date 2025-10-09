class Chapter:
    def __init__(self,name = None,description =None,functions = None,structure=None,feature=None):
        self.name = name
        self.description = description
        self.functions = functions
        self.structure = structure
        self.feature = feature

    def __str__(self):
        return f"Chapter: {self.name}, Description: {self.description}, Functions: {self.functions}, Structure: {self.structure}, Feature: {self.feature}"
