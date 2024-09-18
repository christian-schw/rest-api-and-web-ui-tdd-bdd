# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
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

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)

logger = logging.getLogger("flask.app")


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        new_product = products[0]
        # Check that it matches the original product
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    def test_read_a_product(self):
        """Read a product from the database"""
        product = ProductFactory()
        logger.info("Product via ProductFactory created. Product: %s", vars(product))
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        found_product = Product.find(product.id)
        # Check that it matches the original product
        self.assertEqual(product.id, found_product.id)
        self.assertEqual(product.name, found_product.name)
        self.assertEqual(product.description, found_product.description)
        self.assertEqual(product.price, found_product.price)
        self.assertEqual(product.available, found_product.available)
        self.assertEqual(product.category, found_product.category)

    def test_update_a_product(self):
        """Update a product in database"""
        UPDATED_DESCRIPTION = "New description set"  # pylint: disable=invalid-name
        product = ProductFactory()
        logger.info("Product via ProductFactory created. Product: %s", vars(product))
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        logger.info("Check whether same product after creation: %s", vars(product))
        # Assert that new changes were made
        original_id = product.id
        product.description = UPDATED_DESCRIPTION
        product.update()
        self.assertEqual(product.id, original_id)
        self.assertEqual(product.description, UPDATED_DESCRIPTION)
        # Verify only one product in system
        products = Product.all()
        self.assertEqual(len(products), 1)
        updated_product = products[0]
        # Check whether it matches the original product and has new changes
        self.assertEqual(product.id, updated_product.id)
        self.assertEqual(product.name, updated_product.name)
        self.assertEqual(updated_product.description, UPDATED_DESCRIPTION)
        self.assertEqual(product.price, updated_product.price)
        self.assertEqual(product.available, updated_product.available)
        self.assertEqual(product.category, updated_product.category)

    def test_delete_a_product(self):
        """Delete a product in database"""
        product = ProductFactory()
        logger.info("Product via ProductFactory created. Product: %s", vars(product))
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        # Verify only one product in system
        self.assertEqual(len(Product.all()), 1)
        # Check whether product has been deleted
        product.delete()
        self.assertEqual(len(Product.all()), 0)

    def test_list_all_products(self):
        """List all products in database"""
        products = Product.all()
        # Assert there are no products in database
        self.assertEqual(len(products), 0)
        # Create five products in database
        for _ in range(5):
            product = ProductFactory()
            logger.info("Product via ProductFactory created. Product: %s", vars(product))
            product.id = None
            product.create()
            # Assert that it was assigned an id and shows up in the database
            self.assertIsNotNone(product.id)
        # Check whether five products were created
        products = Product.all()
        self.assertEqual(len(products), 5)

    def test_find_product_by_name(self):
        """Find product by name"""
        # Create five products and add them to database
        for _ in range(5):
            product = ProductFactory()
            logger.info("Product via ProductFactory created. Product: %s", vars(product))
            product.id = None
            product.create()
            # Assert that it was assigned an id and shows up in the database
            self.assertIsNotNone(product.id)
        # Assert number of occurences in database of name of first product
        products = Product.all()
        product = products[0]
        first_product_name = product.name
        expected_occurences = sum(p.name == first_product_name for p in products)
        products_found = Product.find_by_name(first_product_name)
        actual_occurences = products_found.count()
        self.assertEqual(expected_occurences, actual_occurences)
        # Assert that all products found have the desired name
        for product in products_found:
            self.assertEqual(product.name, first_product_name)

    def test_find_product_by_availability(self):
        """Find product by availability"""
        # Create ten products and add them to database
        for _ in range(10):
            product = ProductFactory()
            logger.info("Product via ProductFactory created. Product: %s", vars(product))
            product.id = None
            product.create()
            # Assert that it was assigned an id and shows up in the database
            self.assertIsNotNone(product.id)
        # Assert number of occurences in database of availability of first product
        products = Product.all()
        product = products[0]
        first_product_availability = product.available
        expected_occurences = sum(p.available == first_product_availability for p in products)
        products_found = Product.find_by_availability(first_product_availability)
        actual_occurences = products_found.count()
        self.assertEqual(expected_occurences, actual_occurences)
        # Assert that all products found have the desired availability
        for product in products_found:
            self.assertEqual(product.available, first_product_availability)

    def test_find_product_by_category(self):
        """Find product by category"""
        # Create ten products and add them to database
        for _ in range(10):
            product = ProductFactory()
            logger.info("Product via ProductFactory created. Product: %s", vars(product))
            product.id = None
            product.create()
            # Assert that it was assigned an id and shows up in the database
            self.assertIsNotNone(product.id)
        # Assert number of occurences in database of category of first product
        products = Product.all()
        product = products[0]
        first_product_category = product.category
        expected_occurences = sum(p.category == first_product_category for p in products)
        products_found = Product.find_by_category(first_product_category)
        actual_occurences = products_found.count()
        self.assertEqual(expected_occurences, actual_occurences)
        # Assert that all products found have the desired category
        for product in products_found:
            self.assertEqual(product.category, first_product_category)
