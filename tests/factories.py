"""
Test Factory to make fake objects for testing
"""

import factory
from service.models import Shopcart


class ShopcartFactory(factory.Factory):
    """Creates fake pets that you don't have to feed"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Shopcart

    id = factory.Sequence(lambda n: n)
    name = factory.Faker("first_name")
    userid = factory.Faker("user_name")
    email = factory.Faker("email")
    address = factory.Faker("address")
    active = factory.Faker("pybool")

    # Todo: Add your other attributes here...
