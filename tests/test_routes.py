"""
<your resource name> API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from decimal import Decimal
from tests.factories import SupplierFactory, ItemFactory
from service.common import status  # HTTP Status Codes
from service.models import db, Supplier, init_db
from service.routes import app

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:pgs3cr3t@localhost:5432/postgres"
)

BASE_URL = "/suppliers"


######################################################################
#  T E S T   C A S E S
######################################################################
class TestSupplierService(TestCase):
    """Supplier Service Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        """Runs once before test suite"""

    def setUp(self):
        """Runs before each test"""
        db.session.query(Supplier).delete()  # clean up the last tests
        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        """Runs once after each test case"""
        db.session.remove()

    ######################################################################
    #  H E L P E R   M E T H O D S
    ######################################################################

    def _create_suppliers(self, count):
        """Factory method to create suppliers in bulk"""
        suppliers = []
        for _ in range(count):
            supplier = SupplierFactory()
            resp = self.client.post(BASE_URL, json=supplier.serialize())
            self.assertEqual(
                resp.status_code,
                status.HTTP_201_CREATED,
                "Could not create test Supplier",
            )
            new_supplier = resp.get_json()
            supplier.id = new_supplier["id"]
            suppliers.append(supplier)
        return suppliers

    ######################################################################
    #  S U P P L I E R   T E S T   C A S E S
    ######################################################################

    def test_index(self):
        """It should call the Home Page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_create_supplier(self):
        """It should Create a new Supplier"""
        supplier = SupplierFactory()
        resp = self.client.post(
            BASE_URL, json=supplier.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_supplier = resp.get_json()
        logging.debug(new_supplier)
        self.assertEqual(new_supplier["name"], supplier.name, "Names does not match")
        self.assertEqual(
            new_supplier["items"], supplier.items, "Item does not match"
        )
        self.assertEqual(new_supplier["email"], supplier.email, "Email does not match")
        self.assertEqual(
            new_supplier["phone_number"], supplier.phone_number, "Phone does not match"
        )
        self.assertEqual(
            new_supplier["date_joined"],
            str(supplier.date_joined),
            "Date Joined does not match",
        )

        # Check that the location header was correct by getting it
        resp = self.client.get(location, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_supplier = resp.get_json()
        self.assertEqual(new_supplier["name"], supplier.name, "Names does not match")
        self.assertEqual(
            new_supplier["items"], supplier.items, "Item does not match"
        )
        self.assertEqual(new_supplier["email"], supplier.email, "Email does not match")
        self.assertEqual(
            new_supplier["phone_number"], supplier.phone_number, "Phone does not match"
        )
        self.assertEqual(
            new_supplier["date_joined"],
            str(supplier.date_joined),
            "Date Joined does not match",
        )

    def test_get_supplier(self):
        """It should Read a single Supplier"""
        # get the id of an supplier
        supplier = self._create_suppliers(1)[0]
        resp = self.client.get(
            f"{BASE_URL}/{supplier.id}", content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        logging.debug(data)
        self.assertEqual(data["name"], supplier.name)

    def test_get_supplier_not_found(self):
        """It should not Read an Supplier that is not found"""
        resp = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    ######################################################################
    #  I T E M   T E S T   C A S E S
    ######################################################################

    def test_add_item(self):
        """It should Add an item to an supplier"""
        supplier = self._create_suppliers(1)[0]
        item = ItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{supplier.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        logging.debug(data)
        self.assertEqual(data["supplier_id"], supplier.id)
        self.assertEqual(data["sku"], item.sku)
        self.assertEqual(data["name"], item.name)
        self.assertEqual(data["quantity"], item.quantity)
        self.assertEqual(Decimal(data["price"]), item.price)

    def test_get_item(self):
        """It should Get an item from an supplier"""
        # create a known item
        supplier = self._create_suppliers(1)[0]
        item = ItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{supplier.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        data = resp.get_json()
        logging.debug(data)
        item_id = data["id"]

        # retrieve it back
        resp = self.client.get(
            f"{BASE_URL}/{supplier.id}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        logging.debug(data)
        self.assertEqual(data["supplier_id"], supplier.id)
        self.assertEqual(data["sku"], item.sku)
        self.assertEqual(data["name"], item.name)
        self.assertEqual(data["quantity"], item.quantity)
        self.assertEqual(Decimal(data["price"]), item.price)
