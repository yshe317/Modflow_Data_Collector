import torch

class DeepLearningSourceIdentity:
    def __init__(self, model):
        self.model = model
    
    def train(self, data, target):
        self.model.train(data, target)

    def predict(self, data):
        return self.model(data)