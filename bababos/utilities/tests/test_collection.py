from django.test import TestCase

from bababos.utilities.utils import Collection


class Item:
    name: str
    age: int

    def __init__(self, name, age):
        self.name = name
        self.age = age


class CollectionTest(TestCase):
    def test_simple_filter(self):
        data = [
            Item("a", 1),
            Item("b", 2),
            Item("c", 3),
        ]

        result = Collection.of(data).filter(age=2).get()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], data[1])

    def test_simple_order(self):
        data = [
            Item("c", 3),
            Item("1", 1),
            Item("b", 2),
        ]
        result = Collection.of(data).order_by("age").get()
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], data[1])
        self.assertEqual(result[1], data[2])
        self.assertEqual(result[2], data[0])
