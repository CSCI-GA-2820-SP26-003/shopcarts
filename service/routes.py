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
            paths=url_for("list_shopcarts", _external=True),
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
# LIST ALL SHOPCARTS
######################################################################
@app.route("/shopcarts", methods=["GET"])
def list_shopcarts():
    """
    Retrieve a list of all shopcarts.

    This endpoint returns all of the Shopcarts in the service, optionally filtered
    by the cart's status. If a `status` query parameter is provided, only
    shopcarts matching that status will be returned.

    ---
    tags:
      - Shopcarts
    summary: List all shopcarts
    parameters:
      - in: query
        name: status
        description: Filter shopcarts by status (active, abandoned, or checked_out)
        required: false
        schema:
          type: string
          enum:
            - active
            - abandoned
            - checked_out
    responses:
      200:
        description: Successful response returns a list of shopcart objects
        content:
          application/json:
            schema:
              type: array
              items:
                $ref: '#/definitions/Shopcart'
      400:
        description: Invalid status value provided

    definitions:
      Shopcart:
        type: object
        properties:
          id:
            type: integer
          name:
            type: string
          userid:
            type: string
          active:
            type: boolean
          status:
            type: string
          items:
            type: array
            items:
              $ref: '#/definitions/Item'
          total_price:
            type: number
      Item:
        type: object
        properties:
          id:
            type: integer
          shopcart_id:
            type: integer
          product_id:
            type: string
          name:
            type: string
          quantity:
            type: integer
          price:
            type: number
    """
    app.logger.info("Request for Shopcart list")

    status_param = request.args.get("status")
    if status_param is not None:
        try:
            cart_status = CartStatus(status_param)
        except ValueError:
            abort(
                status.HTTP_400_BAD_REQUEST,
                f"Invalid status '{status_param}'. Valid values are: "
                + ", ".join(s.value for s in CartStatus),
            )
        shopcarts = Shopcart.find_by_status(cart_status)
    else:
        shopcarts = Shopcart.all()

    results = [shopcart.serialize() for shopcart in shopcarts]
    return jsonify(results), status.HTTP_200_OK


######################################################################
# LIST ALL ITEMS IN A SHOPCART
######################################################################
@app.route("/shopcarts/<int:shopcart_id>/items", methods=["GET"])
def list_items(shopcart_id):
    """
    Retrieve all items belonging to a specific shopcart.

    ---
    tags:
      - Items
    summary: List items in a shopcart
    parameters:
      - in: path
        name: shopcart_id
        required: true
        schema:
          type: integer
        description: ID of the shopcart to fetch items for
    responses:
      200:
        description: A list of item objects
        content:
          application/json:
            schema:
              type: array
              items:
                $ref: '#/definitions/Item'
      404:
        description: Shopcart not found
    """
    app.logger.info("Request for all items for Shopcart with id: %s", shopcart_id)

    # See if the shopcart exists and abort if it doesn't
    shopcart = Shopcart.find(shopcart_id)
    if not shopcart:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Shopcart with id '{shopcart_id}' could not be found.",
        )

    # Get the items for the shopcart
    results = [item.serialize() for item in shopcart.items]

    return jsonify(results), status.HTTP_200_OK


######################################################################
# READ A SHOPCART
######################################################################
@app.route("/shopcarts/<int:shopcart_id>", methods=["GET"])
def get_shopcarts(shopcart_id):
    """
    Retrieve a single shopcart by its ID.

    ---
    tags:
      - Shopcarts
    summary: Get a shopcart by ID
    parameters:
      - in: path
        name: shopcart_id
        required: true
        schema:
          type: integer
        description: ID of the shopcart
    responses:
      200:
        description: Shopcart retrieved successfully
        content:
          application/json:
            schema:
              $ref: '#/definitions/Shopcart'
      404:
        description: Shopcart not found
    """
    app.logger.info("Request to Retrieve a shopcart with id [%s]", shopcart_id)

    shopcart = Shopcart.find(shopcart_id)
    if not shopcart:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Shopcart with id '{shopcart_id}' was not found.",
        )

    app.logger.info("Returning shopcart: %s", shopcart.name)
    return jsonify(shopcart.serialize()), status.HTTP_200_OK


######################################################################
# CREATE A NEW SHOPCART
######################################################################
@app.route("/shopcarts", methods=["POST"])
def create_shopcart():
    """
    Create a new shopcart.

    This endpoint accepts a JSON body representing a new shopcart and adds it
    to the data store.  The required fields are `name`, and optional fields
    include `userid`, `active`, and `status`.

    ---
    tags:
      - Shopcarts
    summary: Create a shopcart
    parameters:
      - in: body
        name: body
        required: true
        description: Shopcart object that needs to be created
        schema:
          $ref: '#/definitions/Shopcart'
    responses:
      201:
        description: Shopcart created successfully
        headers:
          Location:
            description: URL of the newly created shopcart
            schema:
              type: string
        content:
          application/json:
            schema:
              $ref: '#/definitions/Shopcart'
      400:
        description: Invalid shopcart data provided
      415:
        description: Unsupported Media Type – Content-Type must be application/json
    """
    app.logger.info("Request to create a Shopcart")
    check_content_type("application/json")

    # Create the shopcart
    shopcart = Shopcart()
    shopcart.deserialize(request.get_json())
    shopcart.create()

    # Create a message to return
    message = shopcart.serialize()
    location_url = url_for("get_shopcarts", shopcart_id=shopcart.id, _external=True)

    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
# UPDATE AN EXISTING ACCOUNT
######################################################################
@app.route("/shopcarts/<int:shopcart_id>", methods=["PUT"])
def update_shopcarts(shopcart_id):
    """
    Update an existing shopcart.

    This endpoint updates the shopcart identified by `shopcart_id` with the
    JSON payload provided in the request body.

    ---
    tags:
      - Shopcarts
    summary: Update a shopcart
    parameters:
      - in: path
        name: shopcart_id
        required: true
        schema:
          type: integer
        description: ID of the shopcart to update
      - in: body
        name: body
        required: true
        description: Shopcart object with updated values
        schema:
          $ref: '#/definitions/Shopcart'
    responses:
      200:
        description: Shopcart updated successfully
        content:
          application/json:
            schema:
              $ref: '#/definitions/Shopcart'
      404:
        description: Shopcart not found
      415:
        description: Unsupported Media Type – Content-Type must be application/json
    """
    app.logger.info("Request to update shopcart with id: %s", shopcart_id)
    check_content_type("application/json")

    # See if the shopcart exists and abort if it doesn't
    shopcart = Shopcart.find(shopcart_id)
    if not shopcart:
        abort(
            status.HTTP_404_NOT_FOUND, f"Account with id '{shopcart_id}' was not found."
        )

    # Update from the json in the body of the request
    shopcart.deserialize(request.get_json())
    shopcart.id = shopcart_id
    shopcart.update()

    return jsonify(shopcart.serialize()), status.HTTP_200_OK


######################################################################
# CHECKOUT ACTION
######################################################################
@app.route("/shopcarts/<int:shopcart_id>/checkout", methods=["PUT"])
def checkout_shopcart(shopcart_id):
    """
    Checkout a shopcart.

    Transitions the status of the shopcart to `checked_out`.  If the cart
    is already checked out, this endpoint returns a 409 Conflict.

    ---
    tags:
      - Shopcarts
    summary: Checkout a shopcart
    parameters:
      - in: path
        name: shopcart_id
        required: true
        schema:
          type: integer
        description: ID of the shopcart to checkout
    responses:
      200:
        description: Shopcart checked out successfully
        content:
          application/json:
            schema:
              $ref: '#/definitions/Shopcart'
      404:
        description: Shopcart not found
      409:
        description: Shopcart is already checked out
    """
    app.logger.info("Request to checkout shopcart with id: %s", shopcart_id)

    shopcart = Shopcart.find(shopcart_id)
    if not shopcart:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Shopcart with id '{shopcart_id}' was not found.",
        )

    if shopcart.status == CartStatus.CHECKED_OUT:
        abort(
            status.HTTP_409_CONFLICT,
            f"Shopcart with id '{shopcart_id}' is already checked out.",
        )

    shopcart.status = CartStatus.CHECKED_OUT
    shopcart.update()

    return jsonify(shopcart.serialize()), status.HTTP_200_OK


######################################################################
# DELETE A SHOPCART
#######################################################################
@app.route("/shopcarts/<int:shopcart_id>", methods=["DELETE"])
def delete_shopcart(shopcart_id):
    """
    Delete a shopcart.

    ---
    tags:
      - Shopcarts
    summary: Delete a shopcart
    parameters:
      - in: path
        name: shopcart_id
        required: true
        schema:
          type: integer
        description: ID of the shopcart to delete
    responses:
      204:
        description: Shopcart deleted successfully
      404:
        description: Shopcart not found
    """
    app.logger.info("Request to delete shopcart with id=%s", shopcart_id)

    cart = Shopcart.find(shopcart_id)
    if not cart:
        return (
            jsonify(
                error="Not Found",
                message=f"Shopcart with id '{shopcart_id}' was not found",
            ),
            status.HTTP_404_NOT_FOUND,
        )

    cart.delete()
    return ("", status.HTTP_204_NO_CONTENT)


######################################################################
# CREATE A NEW ITEM
######################################################################
@app.route("/shopcarts/<int:shopcart_id>/items", methods=["POST"])
def create_items(shopcart_id):
    """
    Create a new item in a specific shopcart.

    Adds an item to the shopcart identified by `shopcart_id` using the
    JSON payload provided in the request body.

    ---
    tags:
      - Items
    summary: Create an item
    parameters:
      - in: path
        name: shopcart_id
        required: true
        schema:
          type: integer
        description: ID of the shopcart to add the item to
      - in: body
        name: body
        required: true
        description: Item object to add to the shopcart
        schema:
          $ref: '#/definitions/Item'
    responses:
      201:
        description: Item created successfully
        headers:
          Location:
            description: URL of the newly created item
            schema:
              type: string
        content:
          application/json:
            schema:
              $ref: '#/definitions/Item'
      404:
        description: Shopcart not found
      415:
        description: Unsupported Media Type – Content-Type must be application/json
    """
    app.logger.info("Request to create an Item for Shopcart with id: %s", shopcart_id)
    check_content_type("application/json")

    # See if the shopcart exists and abort if it doesn't
    shopcart = Shopcart.find(shopcart_id)
    if not shopcart:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Shopcart with id '{shopcart_id}' could not be found.",
        )

    # Create an item from the json data
    item = Item()
    item.deserialize(request.get_json())

    # Append the item to the shopcart
    shopcart.items.append(item)
    shopcart.update()

    # Prepare a message to return
    message = item.serialize()

    # Send the location to GET the new item
    location_url = url_for(
        "get_items", shopcart_id=shopcart.id, item_id=item.id, _external=True
    )
    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
# RETRIEVE AN ITEM FROM SHOPCART
######################################################################
@app.route("/shopcarts/<int:shopcart_id>/items/<int:item_id>", methods=["GET"])
def get_items(shopcart_id, item_id):
    """
    Retrieve a single item from a shopcart.

    ---
    tags:
      - Items
    summary: Get an item by ID
    parameters:
      - in: path
        name: shopcart_id
        required: true
        schema:
          type: integer
        description: ID of the shopcart
      - in: path
        name: item_id
        required: true
        schema:
          type: integer
        description: ID of the item to retrieve
    responses:
      200:
        description: Item retrieved successfully
        content:
          application/json:
            schema:
              $ref: '#/definitions/Item'
      404:
        description: Item or shopcart not found
    """
    app.logger.info(
        "Request to retrieve Item %s for Shopcart id: %s", (item_id, shopcart_id)
    )

    # See if the item exists and abort if it doesn't
    item = Item.find(item_id)
    if not item:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Shopcart with id '{item_id}' could not be found.",
        )

    return jsonify(item.serialize()), status.HTTP_200_OK


######################################################################
# UPDATE AN ITEM
######################################################################
@app.route("/shopcarts/<int:shopcart_id>/items/<int:item_id>", methods=["PUT"])
def update_items(shopcart_id, item_id):
    """
    Update an existing item.

    This endpoint updates the item identified by `item_id` within the given
    shopcart using the JSON payload provided in the request body.

    ---
    tags:
      - Items
    summary: Update an item
    parameters:
      - in: path
        name: shopcart_id
        required: true
        schema:
          type: integer
        description: ID of the shopcart
      - in: path
        name: item_id
        required: true
        schema:
          type: integer
        description: ID of the item to update
      - in: body
        name: body
        required: true
        description: Item object with updated values
        schema:
          $ref: '#/definitions/Item'
    responses:
      200:
        description: Item updated successfully
        content:
          application/json:
            schema:
              $ref: '#/definitions/Item'
      404:
        description: Item not found
      415:
        description: Unsupported Media Type – Content-Type must be application/json
    """
    app.logger.info(
        "Request to update Item %s for Shopcart id: %s", (item_id, shopcart_id)
    )
    check_content_type("application/json")

    # See if the item exists and abort if it doesn't
    item = Item.find(item_id)
    if not item:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Shopcart with id '{item_id}' could not be found.",
        )

    # Update from the json in the body of the request
    item.deserialize(request.get_json())
    item.id = item_id
    item.update()

    return jsonify(item.serialize()), status.HTTP_200_OK


######################################################################
# DELETE AN ITEM
######################################################################
@app.route("/shopcarts/<int:shopcart_id>/items/<int:item_id>", methods=["DELETE"])
def delete_items(shopcart_id, item_id):
    """
    Delete an item from a shopcart.

    ---
    tags:
      - Items
    summary: Delete an item
    parameters:
      - in: path
        name: shopcart_id
        required: true
        schema:
          type: integer
        description: ID of the shopcart
      - in: path
        name: item_id
        required: true
        schema:
          type: integer
        description: ID of the item to delete
    responses:
      204:
        description: Item deleted successfully
      404:
        description: Item or shopcart not found
    """
    app.logger.info(
        "Request to delete Item %s for Shopcart id: %s", item_id, shopcart_id
    )

    # See if the shopcart exists and abort if it doesn't
    shopcart = Shopcart.find(shopcart_id)
    if not shopcart:
        return (
            jsonify(
                error="Not Found",
                message=f"Shopcart with id '{shopcart_id}' was not found",
            ),
            status.HTTP_404_NOT_FOUND,
        )

    # See if the item exists and belongs to this shopcart
    item = Item.find(item_id)
    if (not item) or (item.shopcart_id != shopcart_id):
        return (
            jsonify(
                error="Not Found",
                message=f"Item with id '{item_id}' was not found in shopcart '{shopcart_id}'",
            ),
            status.HTTP_404_NOT_FOUND,
        )

    item.delete()
    return ("", status.HTTP_204_NO_CONTENT)


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
        cart = Shopcart()
        cart.deserialize(request.get_json())
        cart.create()
        location_url = url_for("shopcarts_shopcartresource", shopcart_id=cart.id, _external=True)
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
        cart = Shopcart.find(shopcart_id)
        if not cart:
            abort(status.HTTP_404_NOT_FOUND, f"Shopcart with id '{shopcart_id}' was not found.")
        return cart.serialize(), status.HTTP_200_OK

    @shopcart_ns.expect(shopcart_create_model, validate=True)
    @shopcart_ns.marshal_with(shopcart_model)
    def put(self, shopcart_id):
        """Update a shopcart"""
        cart = Shopcart.find(shopcart_id)
        if not cart:
            abort(status.HTTP_404_NOT_FOUND, f"Shopcart with id '{shopcart_id}' was not found.")
        cart.deserialize(request.get_json())
        cart.id = shopcart_id
        cart.update()
        return cart.serialize(), status.HTTP_200_OK

    def delete(self, shopcart_id):
        """Delete a shopcart"""
        cart = Shopcart.find(shopcart_id)
        if not cart:
            return {
                "error": "Not Found", "message": f"Shopcart with id '{shopcart_id}' was not found"
                }, status.HTTP_404_NOT_FOUND
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
        shopcart = Shopcart.find(shopcart_id)
        if not shopcart:
            abort(status.HTTP_404_NOT_FOUND, f"Shopcart with id '{shopcart_id}' could not be found.")
        results = [item.serialize() for item in shopcart.items]
        return results, status.HTTP_200_OK

    @shopcart_ns.expect(item_create_model, validate=True)
    @shopcart_ns.marshal_with(item_model, code=status.HTTP_201_CREATED)
    def post(self, shopcart_id):
        """Create an item in a shopcart"""
        shopcart = Shopcart.find(shopcart_id)
        if not shopcart:
            abort(status.HTTP_404_NOT_FOUND, f"Shopcart with id '{shopcart_id}' could not be found.")
        item = Item()
        item.deserialize(request.get_json())
        shopcart.items.append(item)
        shopcart.update()
        # keep
        location_url = url_for("get_items", shopcart_id=shopcart.id, item_id=item.id, _external=True)
        return item.serialize(), status.HTTP_201_CREATED, {"Location": location_url}


# /shopcarts/<shopcart_id>/items/<item_id>
@shopcart_ns.route("/<int:shopcart_id>/items/<int:item_id>")
@shopcart_ns.param("shopcart_id", "The shopcart identifier")
@shopcart_ns.param("item_id", "The item identifier")
class ItemResource(Resource):
    """RESTX resource for a single item within a shopcart"""

    @shopcart_ns.marshal_with(item_model)
    def get(self, _shopcart_id, item_id):
        """Retrieve an item from a shopcart"""
        item = Item.find(item_id)
        if not item:
            abort(status.HTTP_404_NOT_FOUND, f"Item with id '{item_id}' could not be found.")
        return item.serialize(), status.HTTP_200_OK

    @shopcart_ns.expect(item_create_model, validate=True)
    @shopcart_ns.marshal_with(item_model)
    def put(self, _shopcart_id, item_id):
        """Update an item in a shopcart"""
        item = Item.find(item_id)
        if not item:
            abort(status.HTTP_404_NOT_FOUND, f"Item with id '{item_id}' could not be found.")
        item.deserialize(request.get_json())
        item.id = item_id
        item.update()
        return item.serialize(), status.HTTP_200_OK

    def delete(self, shopcart_id, item_id):
        """Delete an item from a shopcart"""
        shopcart = Shopcart.find(shopcart_id)
        if not shopcart:
            return {
                "error": "Not Found", "message": f"Shopcart with id '{shopcart_id}' was not found"
                }, status.HTTP_404_NOT_FOUND
        item = Item.find(item_id)
        if (not item) or (item.shopcart_id != shopcart_id):
            return {
                "error": "Not Found", "message": f"Item with id '{item_id}' was not found in shopcart '{shopcart_id}'"
                }, status.HTTP_404_NOT_FOUND

        item.delete()
        return "", status.HTTP_204_NO_CONTENT
