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
from service.models import Shopcart, Item
from service.common import status  # HTTP Status Codes


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
# LIST ALL SHOPCARTS
######################################################################
@app.route("/shopcarts", methods=["GET"])
def list_shopcarts():
    """Returns all of the Shopcarts"""
    app.logger.info("Request for Shopcart list")
    shopcarts = []


######################################################################
# READ A SHOPCART
######################################################################
@app.route("/shopcarts/<int:shopcart_id>", methods=["GET"])
def get_shopcarts(shopcart_id):
    """
    Retrieve a single Shopcart

    This endpoint will return a Shopcart based on its id
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
    Creates an Shopcart
    This endpoint will create an Shopcart based the data in the body that is posted
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
    Update an shopcart

    This endpoint will update an Account based the body that is posted
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
# DELETE A SHOPCART
######################################################################
@app.route("/shopcarts/<int:shopcart_id>", methods=["DELETE"])
def delete_shopcart(shopcart_id):
    """Deletes a Shopcart"""
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
    Create an Address on an Shopcart

    This endpoint will add an item to an shopcart
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
        "get_items",
        shopcart_id=shopcart.id,
        item_id=item.id,
        _external=True
    )
    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}


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
