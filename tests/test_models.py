######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Test cases for Shopcart Model
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest.mock import patch
from unittest import TestCase
from wsgi import app
from service.models import Shopcart, Item, DataValidationError, db
from .factories import ShopcartFactory, ItemFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  SHOPCART   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestShopcart(TestCase):
    """Test Cases for Shopcart Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Item).delete()
        db.session.query(Shopcart).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_shopcart(self):
        """It should create a Shopcart"""
        shopcart = ShopcartFactory()
        shopcart.create()
        self.assertIsNotNone(shopcart.id)
        found = Shopcart.all()
        self.assertEqual(len(found), 1)
        data = Shopcart.find(shopcart.id)
        self.assertEqual(data.name, shopcart.name)
        self.assertEqual(data.userid, shopcart.userid)
        self.assertEqual(data.active, shopcart.active)

    def test_list_all_shopcarts(self):
        """It should List all Shopcarts in the database"""
        shopcarts = Shopcart.all()
        self.assertEqual(shopcarts, [])
        for shopcart in ShopcartFactory.create_batch(5):
            shopcart.create()
        # Assert that there are not 5 shopcarts in the database
        shopcarts = Shopcart.all()
        self.assertEqual(len(shopcarts), 5)

    def test_add_a_shopcart(self):
        """It should Create an shopcart and add it to the database"""
        shopcarts = Shopcart.all()
        self.assertEqual(shopcarts, [])
        shopcart = ShopcartFactory()
        shopcart.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(shopcart.id)
        shopcarts = Shopcart.all()
        self.assertEqual(len(shopcarts), 1)

    @patch("service.models.db.session.commit")
    def test_add_shopcart_failed(self, exception_mock):
        """It should not create an Shopcart on database error"""
        exception_mock.side_effect = Exception()
        shopcart = ShopcartFactory()
        self.assertRaises(DataValidationError, shopcart.create)

    def test_read_shopcart(self):
        """It should read a Shopcart"""
        shopcart = ShopcartFactory()
        shopcart.create()
        found = Shopcart.find(shopcart.id)
        self.assertIsNotNone(found)
        self.assertEqual(found.id, shopcart.id)
        self.assertEqual(found.name, shopcart.name)
        self.assertEqual(found.userid, shopcart.userid)
        self.assertEqual(found.active, shopcart.active)

    def test_update_shopcart(self):
        """It should Update an shopcart"""
        shopcart = ShopcartFactory(userid="johndoe")
        shopcart.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(shopcart.id)
        self.assertEqual(shopcart.userid, "johndoe")

        # Fetch it back
        shopcart = Shopcart.find(shopcart.id)
        shopcart.userid = "janedoe"
        shopcart.update()

        # Fetch it back again
        shopcart = Shopcart.find(shopcart.id)
        self.assertEqual(shopcart.userid, "janedoe")

    @patch("service.models.db.session.commit")
    def test_update_shopcart_failed(self, exception_mock):
        """It should not update an Shopcart on database error"""
        exception_mock.side_effect = Exception()
        shopcart = ShopcartFactory()
        self.assertRaises(DataValidationError, shopcart.update)

    def test_delete_a_shopcart(self):
        """It should Delete an shopcart from the database"""
        shopcarts = Shopcart.all()
        self.assertEqual(shopcarts, [])
        shopcart = ShopcartFactory()
        shopcart.create()
        self.assertIsNotNone(shopcart.id)
        shopcarts = Shopcart.all()
        self.assertEqual(len(shopcarts), 1)
        shopcart = shopcarts[0]
        shopcart.delete()
        shopcarts = Shopcart.all()
        self.assertEqual(len(shopcarts), 0)

    @patch("service.models.db.session.commit")
    def test_delete_shopcart_failed(self, exception_mock):
        """It should not delete an Shopcart on database error"""
        exception_mock.side_effect = Exception()
        shopcart = ShopcartFactory()
        self.assertRaises(DataValidationError, shopcart.delete)

    def test_read_shopcart_not_found(self):
        """It should return None when Shopcart is not found"""
        shopcart = Shopcart.find(0)
        self.assertIsNone(shopcart)

    def test_shopcart_serialize_with_items(self):
        """It should serialize a Shopcart with its items"""
        shopcart = ShopcartFactory()
        shopcart.create()

        item = ItemFactory(shopcart_id=shopcart.id)
        item.create()

        data = shopcart.serialize()
        self.assertEqual(data["id"], shopcart.id)
        self.assertEqual(data["name"], shopcart.name)
        self.assertEqual(len(data["items"]), 1)
        self.assertAlmostEqual(
            data["total_price"], item.price * item.quantity, places=2
        )

    def test_shopcart_total_price_empty(self):
        """It should return 0 total_price for a Shopcart with no items"""
        shopcart = ShopcartFactory()
        shopcart.create()
        self.assertEqual(shopcart.total_price, 0)

    def test_shopcart_total_price_multiple_items(self):
        """It should calculate total_price correctly for multiple items"""
        shopcart = ShopcartFactory()
        shopcart.create()

        item1 = ItemFactory(shopcart_id=shopcart.id)
        item1.create()
        item2 = ItemFactory(shopcart_id=shopcart.id)
        item2.create()

        expected_total = item1.price * item1.quantity + item2.price * item2.quantity
        self.assertAlmostEqual(shopcart.total_price, expected_total, places=2)


######################################################################
#  I T E M   M O D E L   T E S T   C A S E S
######################################################################
class TestItem(TestCase):
    """Test Cases for Item Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Item).delete()
        db.session.query(Shopcart).delete()
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    def test_create_item(self):
        """It should create an Item"""
        shopcart = ShopcartFactory()
        shopcart.create()

        item = ItemFactory(shopcart_id=shopcart.id)
        item.create()
        self.assertIsNotNone(item.id)

        found = Item.find(item.id)
        self.assertEqual(found.product_id, item.product_id)
        self.assertEqual(found.name, item.name)
        self.assertEqual(found.quantity, item.quantity)
        self.assertAlmostEqual(found.price, item.price, places=2)

    def test_item_serialize(self):
        """It should serialize an Item"""
        shopcart = ShopcartFactory()
        shopcart.create()
        item = ItemFactory(shopcart_id=shopcart.id)
        item.create()

        data = item.serialize()
        self.assertEqual(data["id"], item.id)
        self.assertEqual(data["shopcart_id"], shopcart.id)
        self.assertEqual(data["product_id"], item.product_id)
        self.assertEqual(data["name"], item.name)
        self.assertEqual(data["quantity"], item.quantity)
        self.assertAlmostEqual(data["price"], item.price, places=2)

    def test_item_deserialize(self):
        """It should deserialize an Item from a dict"""
        data = {
            "product_id": "abc-123",
            "name": "Widget",
            "quantity": 3,
            "price": 9.99,
        }
        item = Item()
        item.deserialize(data)
        self.assertEqual(item.product_id, "abc-123")
        self.assertEqual(item.name, "Widget")
        self.assertEqual(item.quantity, 3)
        self.assertAlmostEqual(item.price, 9.99, places=2)

    def test_item_deserialize_missing_field(self):
        """It should raise DataValidationError when a required field is missing"""
        data = {"name": "Widget", "quantity": 1}  # missing product_id and price
        item = Item()
        self.assertRaises(DataValidationError, item.deserialize, data)

    def test_item_repr(self):
        """It should return a string representation of an Item"""
        shopcart = ShopcartFactory()
        shopcart.create()
        item = ItemFactory(shopcart_id=shopcart.id)
        item.create()
        self.assertIn(item.name, repr(item))
        self.assertIn(item.product_id, repr(item))

    @patch("service.models.db.session.commit")
    def test_item_create_failed(self, exception_mock):
        """It should raise DataValidationError when item create fails"""
        exception_mock.side_effect = Exception()
        shopcart = ShopcartFactory()
        item = ItemFactory(shopcart_id=shopcart.id)
        self.assertRaises(DataValidationError, item.create)

    @patch("service.models.db.session.commit")
    def test_item_update_failed(self, exception_mock):
        """It should raise DataValidationError when item update fails"""
        exception_mock.side_effect = Exception()
        shopcart = ShopcartFactory()
        item = ItemFactory(shopcart_id=shopcart.id)
        self.assertRaises(DataValidationError, item.update)

    @patch("service.models.db.session.commit")
    def test_item_delete_failed(self, exception_mock):
        """It should raise DataValidationError when item delete fails"""
        exception_mock.side_effect = Exception()
        shopcart = ShopcartFactory()
        item = ItemFactory(shopcart_id=shopcart.id)
        self.assertRaises(DataValidationError, item.delete)

    def test_item_deserialize_attribute_error(self):
        """It should raise DataValidationError on AttributeError during Item deserialization"""

        class NoGetMethod:  # pylint: disable=too-few-public-methods
            """Test helper class that mimics a dict but lacks a get() method."""

            def __getitem__(self, key):
                if key == "product_id":
                    return "abc"
                if key == "name":
                    return "Widget"
                raise KeyError(key)

        item = Item()
        self.assertRaises(DataValidationError, item.deserialize, NoGetMethod())

    def test_item_deserialize_type_error(self):
        """It should raise DataValidationError on TypeError during Item deserialization"""
        item = Item()
        self.assertRaises(DataValidationError, item.deserialize, None)

    def test_item_all(self):
        """It should return all Items in the database"""
        shopcart = ShopcartFactory()
        shopcart.create()
        for item in ItemFactory.create_batch(3, shopcart_id=shopcart.id):
            item.create()
        items = Item.all()
        self.assertEqual(len(items), 3)

    def test_item_find_by_shopcart_id(self):
        """It should return Items for a given shopcart_id"""
        shopcart = ShopcartFactory()
        shopcart.create()
        item = ItemFactory(shopcart_id=shopcart.id)
        item.create()
        found = list(Item.find_by_shopcart_id(shopcart.id))
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0].id, item.id)

    def test_shopcart_deserialize_key_error(self):
        """It should raise DataValidationError when name is missing from Shopcart data"""
        shopcart = Shopcart()
        self.assertRaises(DataValidationError, shopcart.deserialize, {})

    def test_shopcart_deserialize_attribute_error(self):
        """It should raise DataValidationError on AttributeError during Shopcart deserialization"""

        class NoGetMethod:  # pylint: disable=too-few-public-methods
            """Test helper class that mimics a dict but lacks a get() method."""

            def __getitem__(self, key):
                if key == "name":
                    return "TestCart"
                raise KeyError(key)

        shopcart = Shopcart()

        with self.assertRaises(DataValidationError):
            shopcart.deserialize(NoGetMethod())

    def test_shopcart_deserialize_type_error(self):
        """It should raise DataValidationError on TypeError during Shopcart deserialization"""
        shopcart = Shopcart()
        self.assertRaises(DataValidationError, shopcart.deserialize, None)

    def test_shopcart_find_by_name(self):
        """It should return Shopcarts matching a given name"""
        shopcart = ShopcartFactory(name="UniqueTestName")
        shopcart.create()
        found = list(Shopcart.find_by_name("UniqueTestName"))
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0].id, shopcart.id)
