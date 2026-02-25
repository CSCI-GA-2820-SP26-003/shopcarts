"""
Test Factory to make fake objects for testing
"""

import factory
from service.models import Shopcart, Item


class ItemFactory(factory.Factory):
    """Creates fake Items for testing"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Item

    id = factory.Sequence(lambda n: n)
    shopcart_id = factory.Sequence(lambda n: n)
    product_id = factory.Faker("uuid4")
    name = factory.Faker("word")
    quantity = factory.Faker("random_int", min=1, max=10)
    price = factory.Faker("pyfloat", left_digits=2, right_digits=2, positive=True)


class ShopcartFactory(factory.Factory):
    """Creates fake Shopcarts for testing"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Shopcart

    id = factory.Sequence(lambda n: n)
    name = factory.Faker("first_name")
    userid = factory.Faker("user_name")
    email = factory.Faker("email")
    address = factory.Faker("address")
    active = factory.Faker("pybool")
