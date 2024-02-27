import pandas as pd


class Collection:

    def __init__(self, collection):
        self.collection = collection

    def get(self):
        return self.collection

    @classmethod
    def of(cls, collection):
        return cls(collection)

    def filter(self, **kwargs):
        result = []
        for item in self.collection:
            for kwarg in kwargs:
                if getattr(item, kwarg) == kwargs[kwarg]:
                    result.append(item)
        self.collection = result
        return self

    def order_by(self, *args):
        data = self.collection
        for arg in args:
            data = sorted(self.collection, key=lambda x: getattr(x, arg))
        self.collection = data
        return self
