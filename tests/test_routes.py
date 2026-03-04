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
TestShopcart API Service Test Suite
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from wsgi import app
from service.common import status
from service.models import db, Shopcart, Item
from .factories import ShopcartFactory, ItemFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)

BASE_URL = "/shopcarts"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestShopcartService(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Item).delete()
        db.session.query(Shopcart).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  H E L P E R   M E T H O D S
    ######################################################################

    def _create_shopcarts(self, count):
        """Factory method to create shopcarts in bulk"""
        shopcarts = []
        for _ in range(count):
            shopcart = ShopcartFactory()
            resp = self.client.post(BASE_URL, json=shopcart.serialize())
            self.assertEqual(
                resp.status_code,
                status.HTTP_201_CREATED,
                "Could not create test Shopcart",
            )
            new_shopcart = resp.get_json()
            shopcart.id = new_shopcart["id"]
            shopcarts.append(shopcart)
        return shopcarts

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_get_shopcart_list(self):
        """It should Get a list of Shopcarts"""
        self._create_shopcarts(5)
        resp = self.client.get(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 5)

    def test_get_item_list(self):
        """It should Get a list of items"""
        # add two items to shopcart
        shopcart = self._create_shopcarts(1)[0]
        item_list = ItemFactory.create_batch(2)

        # Create item 1
        resp = self.client.post(
            f"{BASE_URL}/{shopcart.id}/items", json=item_list[0].serialize()
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Create item 2
        resp = self.client.post(
            f"{BASE_URL}/{shopcart.id}/items", json=item_list[1].serialize()
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # get the list back and make sure there are 2
        resp = self.client.get(f"{BASE_URL}/{shopcart.id}/items")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(len(data), 2)

    def test_create_shopcart(self):
        """It should Create a new Shopcart"""
        shopcart = ShopcartFactory()
        resp = self.client.post(
            BASE_URL, json=shopcart.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_shopcart = resp.get_json()
        self.assertEqual(new_shopcart["name"], shopcart.name, "Names does not match")
        self.assertEqual(new_shopcart["userid"], shopcart.userid, "UserID does not match")
        self.assertEqual(
            new_shopcart["active"], shopcart.active, "Active state does not match"
        )

        # Check that the location header was correct by getting it
        resp = self.client.get(location, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_shopcart = resp.get_json()
        self.assertEqual(new_shopcart["name"], shopcart.name, "Names does not match")
        self.assertEqual(new_shopcart["userid"], shopcart.userid, "UserID does not match")
        self.assertEqual(
            new_shopcart["active"], shopcart.active, "Active state does not match"
        )
        
    def test_get_shopcart(self):
        """It should return a single Shopcart"""
        shopcart = ShopcartFactory()
        shopcart.create()

        resp = self.client.get(f"/shopcarts/{shopcart.id}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(data["id"], shopcart.id)
        self.assertEqual(data["name"], shopcart.name)
        self.assertEqual(data["userid"], shopcart.userid)
        self.assertEqual(data["active"], shopcart.active)
        self.assertEqual(data["items"], [])
        self.assertEqual(data["total_price"], 0)

    def test_get_shopcart_with_items(self):
        """It should return a Shopcart with its items and total_price"""
        shopcart = ShopcartFactory()
        shopcart.create()

        item = ItemFactory(shopcart_id=shopcart.id)
        item.create()

        resp = self.client.get(f"/shopcarts/{shopcart.id}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(len(data["items"]), 1)
        self.assertEqual(data["items"][0]["product_id"], item.product_id)
        self.assertEqual(data["items"][0]["quantity"], item.quantity)
        self.assertAlmostEqual(data["items"][0]["price"], item.price, places=2)
        self.assertAlmostEqual(
            data["total_price"], item.price * item.quantity, places=2
        )

    def test_get_shopcart_not_found(self):
        """It should return 404 when Shopcart is not found"""
        resp = self.client.get("/shopcarts/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        data = resp.get_json()
        self.assertIn("0", data["message"])

    def test_add_item(self):
        """It should Add an item to an shopcart"""
        shopcart = self._create_shopcarts(1)[0]
        item = ItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{shopcart.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)

        data = resp.get_json()
        logging.debug(data)
        self.assertEqual(data["shopcart_id"], shopcart.id)
        self.assertEqual(data["product_id"], item.product_id)
        self.assertEqual(data["name"], item.name)
        self.assertEqual(data["quantity"], item.quantity)
        self.assertAlmostEqual(data["price"], item.price, places=2)

        # Check that the location header was correct by getting it
        resp = self.client.get(location, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_item = resp.get_json()
        self.assertEqual(new_item["name"], item.name, "Item name does not match")

    def test_get_item(self):
        """It should Get an item from an shopcart"""
        # create a known item
        shopcart = self._create_shopcarts(1)[0]
        item = ItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{shopcart.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        data = resp.get_json()
        logging.debug(data)
        item_id = data["id"]

        # retrieve it back
        resp = self.client.get(
            f"{BASE_URL}/{shopcart.id}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        logging.debug(data)
        self.assertEqual(data["shopcart_id"], shopcart.id)
        self.assertEqual(data["product_id"], item.product_id)
        self.assertEqual(data["name"], item.name)
        self.assertEqual(data["quantity"], item.quantity)
        self.assertAlmostEqual(data["price"], item.price, places=2)

    ######################################################################
    # DELETE A SHOPCART
    ######################################################################
    def test_delete_shopcart_success(self):
        """It should Delete an existing Shopcart"""
        cart = ShopcartFactory()
        cart.create()
        cart_id = cart.id

        resp = self.client.delete(f"/shopcarts/{cart_id}")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_shopcart_not_found(self):
        """It should not Delete a Shopcart that does not exist"""
        resp = self.client.delete("/shopcarts/999999")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(resp.is_json)