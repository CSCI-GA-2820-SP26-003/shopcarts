"""
Test Factory to make fake objects for testing
"""

import factory
from service.models import Shopcart, Item

class ShopcartFactory(factory.Factory):
    """Creates fake Shopcarts for testing"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Shopcart

    id = factory.Sequence(lambda n: n)
    name = factory.Faker("first_name")
    userid = factory.Faker("user_name")
    active = factory.Faker("pybool")
    total_price = 0.0

    @factory.post_generation
    def items(self, create, extracted, **kwargs): #pylint: disable=method-hidden, unused-argument
        """Create the items list"""
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            self.items = extracted

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

    


