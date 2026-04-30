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
Shopcart Service

This service implements a REST API that allows you to Create, Read, Update
and Delete Shopcart
"""

from flask import jsonify, request, url_for, abort
from flask import current_app as app  # Import Flask application
from flask_restx import Namespace, Resource, fields
from service import api
from service.models import Shopcart, Item, CartStatus
from service.common import status  # HTTP Status Codes

######################################################################
# RESTX Swagger
######################################################################
# RESTX namespace and models
shopcart_ns = Namespace("shopcarts", description="Shopcart operations")
api.add_namespace(shopcart_ns, path="/shopcarts")

# Item data model
item_model = shopcart_ns.model(
    "Item",
    {
        "id": fields.Integer(readOnly=True, description="Item ID"),
        "shopcart_id": fields.Integer(readOnly=True, description="Parent Shopcart ID"),
        "product_id": fields.String(required=True, description="Product ID"),
        "name": fields.String(required=True, description="Item name"),
        "quantity": fields.Integer(required=False, description="Quantity"),
        "price": fields.Float(required=True, description="Item price"),
    },
)

# Shopcart model(including items）
shopcart_model = shopcart_ns.model(
    "Shopcart",
    {
        "id": fields.Integer(readOnly=True, description="Shopcart ID"),
        "name": fields.String(required=True, description="Shopcart name"),
        "userid": fields.String(required=False, description="User ID"),
        "active": fields.Boolean(required=False, description="Active flag"),
        "status": fields.String(required=False, description="Status"),
        "items": fields.List(fields.Nested(item_model), readOnly=True),
        "total_price": fields.Float(readOnly=True, description="Total price"),
    },
)

# Shopcart model when initialing(no id and items
shopcart_create_model = shopcart_ns.model(
    "ShopcartCreate",
    {
        "name": fields.String(required=True, description="Name of the shopcart"),
        "userid": fields.String(required=False, description="User ID"),
        "active": fields.Boolean(required=False, description="Active flag"),
        "status": fields.String(required=False, description="Status"),
    },
)

# Item model when initialing and updating
item_create_model = shopcart_ns.model(
    "ItemCreate",
    {
        "product_id": fields.String(required=True, description="Product ID"),
        "name": fields.String(required=True, description="Item name"),
        "quantity": fields.Integer(required=False, description="Quantity"),
        "price": fields.Float(required=True, description="Price"),
    },
)

######################################################################
# ADMIN UI
######################################################################


@app.route("/admin")
def admin():
    """Admin UI for managing shopcarts"""
    return app.send_static_file("index.html")


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        jsonify(
            name="Shopcarts REST API Service",
            version="1.0",
            paths=url_for("shopcarts_shopcart_collection", _external=True),
        ),
        status.HTTP_200_OK,
    )


######################################################################
# HEALTH ENDPOINT
######################################################################
@app.route("/health")
def health():
    """Health Status"""
    return jsonify({"status": "OK"}), status.HTTP_200_OK


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def check_content_type(content_type):
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, f"Content-Type must be {content_type}"
    )

######################################################################
#  RESTX Resource
######################################################################


# /shopcarts GET and POST
@shopcart_ns.route("")
class ShopcartCollection(Resource):
    """RESTX resource for shopcart collection"""

    @shopcart_ns.marshal_list_with(shopcart_model)
    @shopcart_ns.param("status", "Filter by cart status")
    def get(self):
        """List all shopcarts (optionally filtered by status)"""
        app.logger.info("Request for Shopcart list")
        status_param = request.args.get("status")
        if status_param:
            try:
                cart_status = CartStatus(status_param)
            except ValueError:
                abort(
                    status.HTTP_400_BAD_REQUEST,
                    f"Invalid status '{status_param}'. Valid values are: " + ", ".join(s.value for s in CartStatus),
                )
            shopcarts = Shopcart.find_by_status(cart_status)
        else:
            shopcarts = Shopcart.all()
        return [cart.serialize() for cart in shopcarts], status.HTTP_200_OK

    @shopcart_ns.expect(shopcart_create_model, validate=True)
    @shopcart_ns.marshal_with(shopcart_model, code=status.HTTP_201_CREATED)
    def post(self):
        """Create a new shopcart"""
        app.logger.info("Request to create a Shopcart")
        cart = Shopcart()
        cart.deserialize(request.get_json())
        cart.create()
        location_url = url_for("shopcarts_shopcart_resource", shopcart_id=cart.id, _external=True)
        return cart.serialize(), status.HTTP_201_CREATED, {"Location": location_url}


# /shopcarts/<int:shopcart_id>  GET/PUT/DELETE
@shopcart_ns.route("/<int:shopcart_id>")
@shopcart_ns.response(404, "Shopcart not found")
@shopcart_ns.param("shopcart_id", "The shopcart identifier")
class ShopcartResource(Resource):
    """RESTX resource for a single shopcart"""

    @shopcart_ns.marshal_with(shopcart_model)
    def get(self, shopcart_id):
        """Retrieve a shopcart by ID"""
        app.logger.info("Request to Retrieve a shopcart with id [%s]", shopcart_id)
        cart = Shopcart.find(shopcart_id)
        if not cart:
            abort(status.HTTP_404_NOT_FOUND, f"Shopcart with id '{shopcart_id}' was not found.")
        return cart.serialize(), status.HTTP_200_OK

    @shopcart_ns.expect(shopcart_create_model, validate=True)
    @shopcart_ns.marshal_with(shopcart_model)
    def put(self, shopcart_id):
        """Update a shopcart"""
        app.logger.info("Request to update shopcart with id: %s", shopcart_id)
        cart = Shopcart.find(shopcart_id)
        if not cart:
            abort(status.HTTP_404_NOT_FOUND, f"Shopcart with id '{shopcart_id}' was not found.")
        cart.deserialize(request.get_json())
        cart.id = shopcart_id
        cart.update()
        return cart.serialize(), status.HTTP_200_OK

    def delete(self, shopcart_id):
        """Delete a shopcart"""
        app.logger.info("Request to delete shopcart with id=%s", shopcart_id)
        cart = Shopcart.find(shopcart_id)
        if cart:
            cart.delete()
        return "", status.HTTP_204_NO_CONTENT


# /shopcarts/<shopcart_id>/checkout
@shopcart_ns.route("/<int:shopcart_id>/checkout")
@shopcart_ns.response(404, "Shopcart not found")
@shopcart_ns.response(409, "Shopcart already checked out")
class CheckoutResource(Resource):
    """RESTX resource for checking out a shopcart"""

    @shopcart_ns.marshal_with(shopcart_model)
    def put(self, shopcart_id):
        """Check out a shopcart"""
        app.logger.info("Request to checkout shopcart with id: %s", shopcart_id)
        shopcart = Shopcart.find(shopcart_id)
        if not shopcart:
            abort(status.HTTP_404_NOT_FOUND, f"Shopcart with id '{shopcart_id}' was not found.")
        if shopcart.status == CartStatus.CHECKED_OUT:
            abort(status.HTTP_409_CONFLICT, f"Shopcart with id '{shopcart_id}' is already checked out.")
        shopcart.status = CartStatus.CHECKED_OUT
        shopcart.update()
        return shopcart.serialize(), status.HTTP_200_OK


# /shopcarts/<shopcart_id>/items
@shopcart_ns.route("/<int:shopcart_id>/items")
@shopcart_ns.param("shopcart_id", "The shopcart identifier")
class ItemCollection(Resource):
    """RESTX resource for item collection within a shopcart"""

    @shopcart_ns.marshal_list_with(item_model)
    def get(self, shopcart_id):
        """List all items of a shopcart"""
        app.logger.info("Request for all items for Shopcart with id: %s", shopcart_id)
        shopcart = Shopcart.find(shopcart_id)
        if not shopcart:
            abort(status.HTTP_404_NOT_FOUND, f"Shopcart with id '{shopcart_id}' could not be found.")
        results = [item.serialize() for item in shopcart.items]
        return results, status.HTTP_200_OK

    @shopcart_ns.expect(item_create_model, validate=True)
    @shopcart_ns.marshal_with(item_model, code=status.HTTP_201_CREATED)
    def post(self, shopcart_id):
        """Create an item in a shopcart"""
        app.logger.info("Request to create an Item for Shopcart with id: %s", shopcart_id)
        shopcart = Shopcart.find(shopcart_id)
        if not shopcart:
            abort(status.HTTP_404_NOT_FOUND, f"Shopcart with id '{shopcart_id}' could not be found.")
        item = Item()
        item.deserialize(request.get_json())
        shopcart.items.append(item)
        shopcart.update()
        location_url = url_for(
            "shopcarts_item_resource", shopcart_id=shopcart.id, item_id=item.id, _external=True
        )
        return item.serialize(), status.HTTP_201_CREATED, {"Location": location_url}


# /shopcarts/<shopcart_id>/items/<item_id>
@shopcart_ns.route("/<int:shopcart_id>/items/<int:item_id>")
@shopcart_ns.param("shopcart_id", "The shopcart identifier")
@shopcart_ns.param("item_id", "The item identifier")
class ItemResource(Resource):
    """RESTX resource for a single item within a shopcart"""

    @shopcart_ns.marshal_with(item_model)
    def get(self, shopcart_id, item_id):
        """Retrieve an item from a shopcart"""
        app.logger.info(
            "Request to retrieve Item %s for Shopcart id: %s", item_id, shopcart_id
        )
        shopcart = Shopcart.find(shopcart_id)
        if not shopcart:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Shopcart with id '{shopcart_id}' could not be found.",
            )
        item = Item.find(item_id)
        if not item or item.shopcart_id != shopcart.id:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Item with id '{item_id}' was not found in shopcart '{shopcart_id}'.",
            )
        return item.serialize(), status.HTTP_200_OK

    @shopcart_ns.expect(item_create_model, validate=True)
    @shopcart_ns.marshal_with(item_model)
    def put(self, shopcart_id, item_id):
        """Update an item in a shopcart"""
        app.logger.info(
            "Request to update Item %s for Shopcart id: %s", item_id, shopcart_id
        )
        shopcart = Shopcart.find(shopcart_id)
        if not shopcart:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Shopcart with id '{shopcart_id}' could not be found.",
            )
        item = Item.find(item_id)
        if not item or item.shopcart_id != shopcart.id:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Item with id '{item_id}' was not found in shopcart '{shopcart_id}'.",
            )
        item.deserialize(request.get_json())
        item.id = item_id
        item.update()
        return item.serialize(), status.HTTP_200_OK

    def delete(self, shopcart_id, item_id):
        """Delete an item from a shopcart"""
        app.logger.info(
            "Request to delete Item %s for Shopcart id: %s", item_id, shopcart_id
        )
        shopcart = Shopcart.find(shopcart_id)
        if shopcart:
            item = Item.find(item_id)
            if item and item.shopcart_id == shopcart_id:
                item.delete()
        return "", status.HTTP_204_NO_CONTENT
