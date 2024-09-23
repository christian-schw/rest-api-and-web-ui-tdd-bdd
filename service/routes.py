######################################################################
# Copyright 2016, 2022 John J. Rofrano. All Rights Reserved.
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

# spell: ignore Rofrano jsonify restx dbname
"""
Product Store Service with UI
"""
from flask import jsonify, request, abort
from flask import url_for  # noqa: F401 pylint: disable=unused-import
from service.models import Product, Category
from service.common import status  # HTTP Status Codes
from . import app


######################################################################
# H E A L T H   C H E C K
######################################################################
@app.route("/health")
def healthcheck():
    """Let them know our heart is still beating"""
    return jsonify(status=200, message="OK"), status.HTTP_200_OK


######################################################################
# H O M E   P A G E
######################################################################
@app.route("/")
def index():
    """Base URL for our service"""
    return app.send_static_file("index.html")


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
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )


######################################################################
# C R E A T E   A   N E W   P R O D U C T
######################################################################
@app.route("/products", methods=["POST"])
def create_products():
    """
    Creates a Product
    This endpoint will create a Product based the data in the body that is posted
    """
    app.logger.info("Request to Create a Product...")
    check_content_type("application/json")

    data = request.get_json()
    app.logger.info("Processing: %s", data)
    product = Product()
    product.deserialize(data)
    product.create()
    app.logger.info("Product with new id [%s] saved!", product.id)

    message = product.serialize()

    #
    # Uncomment this line of code once you implement READ A PRODUCT
    #
    # location_url = url_for("get_products", product_id=product.id, _external=True)
    location_url = "/"  # delete once READ is implemented
    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
# L I S T   P R O D U C T S
######################################################################
@app.route("/products", methods=["GET"])
def list_products():
    """
    List products in database.
    Filters can be used (e. g. name, availability, ...).
    According to the task, it should not be implicitly possible to use several filters at once.
    And no filter with multiple values (e. g. name = Christian or Janice)
    I have to use the various available methods of the Product class.
    """
    app.logger.info("Request to List Products...")
    product_list = []
    filter_name = request.args.get("name")
    filter_category = request.args.get("category")
    filter_available = request.args.get("available")

    if filter_name:
        app.logger.info("Fetch products with name %s from database.", filter_name)
        product_list = Product.find_by_name(filter_name).all()
    elif filter_category:
        app.logger.info("Fetch products with category %s from database.", filter_category)
        # Category is an Enum. Hence, it's necessary to use getattr()
        filter_category_value = getattr(Category, filter_category.upper())
        product_list = Product.find_by_category(filter_category_value).all()
    elif filter_available:
        app.logger.info("Fetch products with availability %s from database.", filter_available)
        product_list = Product.find_by_availability(filter_available).all()
    else:
        app.logger.info("Fetch all products from database")
        product_list = Product.all()

    # Create response object
    if len(product_list) == 0:
        app.logger.info("**No** products found.")
        response_status = status.HTTP_204_NO_CONTENT
        message = product_list
    else:
        app.logger.info("Products found.")
        response_status = status.HTTP_200_OK
        message = [product.serialize() for product in product_list]

    return jsonify(message), response_status


######################################################################
# R E A D   A   P R O D U C T
######################################################################
@app.route("/products/<int:product_id>", methods=["GET"])
def read_product(product_id: int):
    """
    Read a product depending on the supplied product ID.
    """
    app.logger.info("Request to Read a Product...")
    product = Product.find(product_id)

    if product is None:
        app.logger.info("**No** product with ID %s found.", product_id)
        response_status = status.HTTP_404_NOT_FOUND
        message = f"Status Code: {status.HTTP_404_NOT_FOUND}"
    else:
        app.logger.info("Product with ID %s found.", product_id)
        response_status = status.HTTP_200_OK
        message = product.serialize()

    return jsonify(message), response_status


######################################################################
# U P D A T E   A   P R O D U C T
######################################################################
@app.route("/products/<int:product_id>", methods=["PUT"])
def update_product(product_id: int):
    """
    Update a product depending on the supplied product ID.
    """
    app.logger.info("Request to Update a Product with id %s...", product_id)
    check_content_type("application/json")

    # Only update product if it exists on database!
    product = Product.find(product_id)

    if product is None:
        app.logger.info("**No** product with ID %s found.", product_id)
        response_status = status.HTTP_404_NOT_FOUND
        message = f"Status Code: {status.HTTP_404_NOT_FOUND}"
    else:
        app.logger.info("Product with ID %s found.", product_id)
        response_status = status.HTTP_200_OK
        product.deserialize(request.get_json())
        product.id = product_id
        product.update()
        app.logger.info("Product with id [%s] updated!", product.id)
        message = product.serialize()

    return jsonify(message), response_status


######################################################################
# D E L E T E   A   P R O D U C T
######################################################################
@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id: int):
    """
    Delete a product depending on the supplied product ID.
    """
    app.logger.info("Request to Delete a Product with id %s...", product_id)
    check_content_type("application/json")

    # Only delete product if it exists on database!
    product = Product.find(product_id)

    if product is None:
        app.logger.info("**No** product with ID %s found.", product_id)
        response_status = status.HTTP_404_NOT_FOUND
        message = f"Status Code: {status.HTTP_404_NOT_FOUND}"
    else:
        app.logger.info("Product with ID %s found.", product_id)
        response_status = status.HTTP_204_NO_CONTENT
        product.deserialize(request.get_json())
        product.id = product_id
        product.delete()
        app.logger.info("Product with id [%s] deleted!", product.id)
        message = ""

    return jsonify(message), response_status
