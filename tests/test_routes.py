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
from service.models import db, Shopcart, Item, CartStatus
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
        self.assertEqual(
            new_shopcart["userid"], shopcart.userid, "UserID does not match"
        )
        self.assertEqual(
            new_shopcart["active"], shopcart.active, "Active state does not match"
        )

        # Check that the location header was correct by getting it
        resp = self.client.get(location, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_shopcart = resp.get_json()
        self.assertEqual(new_shopcart["name"], shopcart.name, "Names does not match")
        self.assertEqual(
            new_shopcart["userid"], shopcart.userid, "UserID does not match"
        )
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

    def test_update_item(self):
        """It should Update an item on an shopcart"""
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
        data["name"] = "XXXX"

        # send the update back
        resp = self.client.put(
            f"{BASE_URL}/{shopcart.id}/items/{item_id}",
            json=data,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # retrieve it back
        resp = self.client.get(
            f"{BASE_URL}/{shopcart.id}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        logging.debug(data)
        self.assertEqual(data["id"], item_id)
        self.assertEqual(data["shopcart_id"], shopcart.id)
        self.assertEqual(data["name"], "XXXX")

    ######################################################################
    # DELETE A SHOPCART ITEM
    ######################################################################
    def test_delete_shopcart_item_success(self):
        """It should Delete an existing Shopcart Item"""
        shopcart = self._create_shopcarts(1)[0]

        item = ItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{shopcart.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        item_id = resp.get_json()["id"]

        resp = self.client.delete(f"{BASE_URL}/{shopcart.id}/items/{item_id}")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_shopcart_item_not_found(self):
        """It should return 404 if item does not exist"""
        shopcart = self._create_shopcarts(1)[0]

        resp = self.client.delete(f"{BASE_URL}/{shopcart.id}/items/999999")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(resp.is_json)

    def test_delete_shopcart_item_cart_not_found(self):
        """It should return 404 if shopcart does not exist"""
        resp = self.client.delete(f"{BASE_URL}/999999/items/1")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(resp.is_json)

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

    def test_index(self):
        """It should return the index page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["name"], "Shopcarts REST API Service")

    def test_admin(self):
        """It should return the admin UI page"""
        resp = self.client.get("/admin")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_list_items_shopcart_not_found(self):
        """It should return 404 when listing items for a non-existent shopcart"""
        resp = self.client.get(f"{BASE_URL}/999999/items")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_shopcart(self):
        """It should Update an existing Shopcart"""
        shopcart = self._create_shopcarts(1)[0]
        updated_data = {
            "name": "UpdatedName",
            "userid": shopcart.userid,
            "active": shopcart.active,
        }
        resp = self.client.put(
            f"{BASE_URL}/{shopcart.id}",
            json=updated_data,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["name"], "UpdatedName")

    def test_update_shopcart_not_found(self):
        """It should return 404 when updating a non-existent Shopcart"""
        resp = self.client.put(
            f"{BASE_URL}/999999",
            json={"name": "Test", "userid": "user1", "active": True},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_item_shopcart_not_found(self):
        """It should return 404 when adding an item to a non-existent shopcart"""
        item = ItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/999999/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_item_not_found(self):
        """It should return 404 when getting a non-existent item"""
        shopcart = self._create_shopcarts(1)[0]
        resp = self.client.get(
            f"{BASE_URL}/{shopcart.id}/items/999999",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_item_not_found(self):
        """It should return 404 when updating a non-existent item"""
        shopcart = self._create_shopcarts(1)[0]
        resp = self.client.put(
            f"{BASE_URL}/{shopcart.id}/items/999999",
            json={"product_id": "p1", "name": "Item", "quantity": 1, "price": 9.99},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_shopcart_no_content_type(self):
        """It should return 415 when Content-Type header is missing"""
        resp = self.client.post(BASE_URL, data='{"name": "test"}')
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_shopcart_wrong_content_type(self):
        """It should return 415 when Content-Type is wrong"""
        resp = self.client.post(
            BASE_URL, data='{"name": "test"}', content_type="text/plain"
        )
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_method_not_allowed(self):
        """It should return 405 when method is not allowed"""
        resp = self.client.patch(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_bad_request_from_invalid_data(self):
        """It should return 400 when request data is invalid"""
        resp = self.client.post(BASE_URL, json={}, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    ######################################################################
    #  F I L T E R   B Y   S T A T U S   T E S T S
    ######################################################################

    def test_list_shopcarts_filter_by_status(self):
        """It should return only carts matching the requested status"""
        # Create carts with known statuses directly via model
        active_cart = ShopcartFactory(status=CartStatus.ACTIVE)
        active_cart.create()
        abandoned_cart = ShopcartFactory(status=CartStatus.ABANDONED)
        abandoned_cart.create()
        checked_out_cart = ShopcartFactory(status=CartStatus.CHECKED_OUT)
        checked_out_cart.create()

        resp = self.client.get(f"{BASE_URL}?status=active")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["status"], "active")
        self.assertEqual(data[0]["id"], active_cart.id)

    def test_list_shopcarts_filter_abandoned(self):
        """It should return only abandoned carts"""
        ShopcartFactory(status=CartStatus.ACTIVE).create()
        abandoned1 = ShopcartFactory(status=CartStatus.ABANDONED)
        abandoned1.create()
        abandoned2 = ShopcartFactory(status=CartStatus.ABANDONED)
        abandoned2.create()

        resp = self.client.get(f"{BASE_URL}?status=abandoned")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 2)
        for cart in data:
            self.assertEqual(cart["status"], "abandoned")

    def test_list_shopcarts_filter_checked_out(self):
        """It should return only checked_out carts"""
        ShopcartFactory(status=CartStatus.ACTIVE).create()
        checked_out = ShopcartFactory(status=CartStatus.CHECKED_OUT)
        checked_out.create()

        resp = self.client.get(f"{BASE_URL}?status=checked_out")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["status"], "checked_out")

    def test_list_shopcarts_filter_returns_empty_when_none_match(self):
        """It should return an empty list when no carts match the filter"""
        ShopcartFactory(status=CartStatus.ACTIVE).create()

        resp = self.client.get(f"{BASE_URL}?status=abandoned")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data, [])

    def test_list_shopcarts_filter_invalid_status_returns_400(self):
        """It should return 400 for an invalid status value"""
        resp = self.client.get(f"{BASE_URL}?status=nonexistent")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    ######################################################################
    #  C H E C K O U T   A C T I O N   T E S T S
    ######################################################################

    def test_checkout_active_cart(self):
        """It should checkout an active cart and return 200 with status checked_out"""
        cart = ShopcartFactory(status=CartStatus.ACTIVE)
        cart.create()

        resp = self.client.put(f"{BASE_URL}/{cart.id}/checkout")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["status"], "checked_out")
        self.assertEqual(data["id"], cart.id)

    def test_checkout_already_checked_out_cart(self):
        """It should return 409 when cart is already checked out"""
        cart = ShopcartFactory(status=CartStatus.CHECKED_OUT)
        cart.create()

        resp = self.client.put(f"{BASE_URL}/{cart.id}/checkout")
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)

    def test_checkout_cart_not_found(self):
        """It should return 404 when checking out a non-existent cart"""
        resp = self.client.put(f"{BASE_URL}/999999/checkout")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_shopcarts_no_filter_returns_all(self):
        """It should return all carts when no status filter is provided"""
        ShopcartFactory(status=CartStatus.ACTIVE).create()
        ShopcartFactory(status=CartStatus.ABANDONED).create()
        ShopcartFactory(status=CartStatus.CHECKED_OUT).create()

        resp = self.client.get(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 3)
