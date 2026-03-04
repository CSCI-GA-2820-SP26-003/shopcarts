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
        self.assertEqual(data.address, shopcart.address)
        self.assertEqual(data.email, shopcart.email)
        self.assertEqual(data.userid, shopcart.userid)
        self.assertEqual(data.active, shopcart.active)

    def test_read_shopcart(self):
        """It should read a Shopcart"""
        shopcart = ShopcartFactory()
        shopcart.create()
        found = Shopcart.find(shopcart.id)
        self.assertIsNotNone(found)
        self.assertEqual(found.id, shopcart.id)
        self.assertEqual(found.name, shopcart.name)
        self.assertEqual(found.userid, shopcart.userid)
        self.assertEqual(found.email, shopcart.email)
        self.assertEqual(found.address, shopcart.address)
        self.assertEqual(found.active, shopcart.active)

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
