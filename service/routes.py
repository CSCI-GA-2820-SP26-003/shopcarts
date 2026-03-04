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

# Todo: Place your REST API code here ...
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
    # Process the query string if any
    name = request.args.get("name")
    if name:
        shopcarts = Shopcart.find_by_name(name)
    else:
        shopcarts = Shopcart.all()

    # Return as an array of dictionaries
    results = [shopcart.serialize() for shopcart in shopcarts]

    return jsonify(results), status.HTTP_200_OK

######################################################################
# CREATE A NEW SHOPCART
######################################################################
@app.route("/Shopcart", methods=["POST"])
def create_shopcart():
    """
    Creates an Shopcart
    This endpoint will create an Shopcart based the data in the body that is posted
    """
    app.logger.info("Request to create a Shopcart")
    check_content_type("application/json")

    # Create the account
    shopcart = Shopcart()
    shopcart.deserialize(request.get_json())
    shopcart.create()

    # Create a message to return
    message = shopcart.serialize()
    location_url = url_for("get_shopcart", shopcart_id=shopcart.id, _external=True)

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

    app.logger.info("Returning shopcart: %s", shopcart.name)
    return jsonify(shopcart.serialize()), status.HTTP_200_OK

######################################################################
# CREATE A NEW ACCOUNT
######################################################################
@app.route("/shopcarts/<int:shopcart_id>/items", methods=["POST"])
def create_item():
    """
    Creates an Item
    This endpoint will create an Item based the data in the body that is posted
    """
    app.logger.info("Request to create an Item")
    check_content_type("application/json")

    # Create the account
    item = Item()
    item.deserialize(request.get_json())
    item.create()

    # Create a message to return
    message = item.serialize()
    location_url = url_for("get_accounts", account_id=item.id, _external=True)

    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}

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
