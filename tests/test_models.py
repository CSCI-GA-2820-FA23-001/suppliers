"""
Test cases for Supplier Model

"""
import logging
import unittest
import os
from service import app
from service.models import Supplier, Item, DataValidationError, db
from tests.factories import SupplierFactory, ItemFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  S U P P L I E R   M O D E L   T E S T   C A S E S
######################################################################
class TestSupplier(unittest.TestCase):
    """Test Cases for Supplier Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Supplier.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""

    def setUp(self):
        """This runs before each test"""
        db.session.query(Supplier).delete()  # clean up the last tests
        db.session.query(Item).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_an_supplier(self):
        """It should Create an Supplier and assert that it exists"""
        fake_supplier = SupplierFactory()
        # pylint: disable=unexpected-keyword-arg
        supplier = Supplier(
            name=fake_supplier.name,
            email=fake_supplier.email,
            phone_number=fake_supplier.phone_number,
            date_joined=fake_supplier.date_joined,
        )
        self.assertIsNotNone(supplier)
        self.assertEqual(supplier.id, None)
        self.assertEqual(supplier.name, fake_supplier.name)
        self.assertEqual(supplier.email, fake_supplier.email)
        self.assertEqual(supplier.phone_number, fake_supplier.phone_number)
        self.assertEqual(supplier.date_joined, fake_supplier.date_joined)

    def test_add_a_supplier(self):
        """It should Create an supplier and add it to the database"""
        suppliers = Supplier.all()
        self.assertEqual(suppliers, [])
        supplier = SupplierFactory()
        supplier.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(supplier.id)
        suppliers = Supplier.all()
        self.assertEqual(len(suppliers), 1)

    def test_read_supplier(self):
        """It should Read an supplier"""
        supplier = SupplierFactory()
        supplier.create()

        # Read it back
        found_supplier = Supplier.find(supplier.id)
        self.assertEqual(found_supplier.id, supplier.id)
        self.assertEqual(found_supplier.name, supplier.name)
        self.assertEqual(found_supplier.email, supplier.email)
        self.assertEqual(found_supplier.phone_number, supplier.phone_number)
        self.assertEqual(found_supplier.date_joined, supplier.date_joined)
        self.assertEqual(found_supplier.items, [])

    def test_update_supplier(self):
        """It should Update an supplier"""
        supplier = SupplierFactory(email="advent@change.me")
        supplier.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(supplier.id)
        self.assertEqual(supplier.email, "advent@change.me")

        # Fetch it back
        supplier = Supplier.find(supplier.id)
        supplier.email = "XYZZY@plugh.com"
        supplier.update()

        # Fetch it back again
        supplier = Supplier.find(supplier.id)
        self.assertEqual(supplier.email, "XYZZY@plugh.com")

    def test_delete_an_supplier(self):
        """It should Delete an supplier from the database"""
        suppliers = Supplier.all()
        self.assertEqual(suppliers, [])
        supplier = SupplierFactory()
        supplier.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(supplier.id)
        suppliers = Supplier.all()
        self.assertEqual(len(suppliers), 1)
        supplier = suppliers[0]
        supplier.delete()
        suppliers = Supplier.all()
        self.assertEqual(len(suppliers), 0)

    def test_list_all_suppliers(self):
        """It should List all Suppliers in the database"""
        suppliers = Supplier.all()
        self.assertEqual(suppliers, [])
        for supplier in SupplierFactory.create_batch(5):
            supplier.create()
        # Assert that there are not 5 suppliers in the database
        suppliers = Supplier.all()
        self.assertEqual(len(suppliers), 5)

    def test_find_by_name(self):
        """It should Find an Supplier by name"""
        supplier = SupplierFactory()
        supplier.create()

        # Fetch it back by name
        same_supplier = Supplier.find_by_name(supplier.name)[0]
        self.assertEqual(same_supplier.id, supplier.id)
        self.assertEqual(same_supplier.name, supplier.name)

    def test_serialize_an_supplier(self):
        """It should Serialize an supplier"""
        supplier = SupplierFactory()
        item = ItemFactory()
        supplier.items.append(item)
        serial_supplier = supplier.serialize()
        self.assertEqual(serial_supplier["id"], supplier.id)
        self.assertEqual(serial_supplier["name"], supplier.name)
        self.assertEqual(serial_supplier["email"], supplier.email)
        self.assertEqual(serial_supplier["phone_number"], supplier.phone_number)
        self.assertEqual(serial_supplier["date_joined"], str(supplier.date_joined))
        self.assertEqual(len(serial_supplier["items"]), 1)
        items = serial_supplier["items"]
        self.assertEqual(items[0]["id"], item.id)
        self.assertEqual(items[0]["supplier_id"], item.supplier_id)
        self.assertEqual(items[0]["sku"], item.sku)
        self.assertEqual(items[0]["name"], item.name)
        self.assertEqual(items[0]["quantity"], item.quantity)
        self.assertEqual(items[0]["price"], item.price)

    def test_deserialize_an_supplier(self):
        """It should Deserialize an supplier"""
        supplier = SupplierFactory()
        supplier.items.append(ItemFactory())
        supplier.create()
        serial_supplier = supplier.serialize()
        new_supplier = Supplier()
        new_supplier.deserialize(serial_supplier)
        self.assertEqual(new_supplier.name, supplier.name)
        self.assertEqual(new_supplier.email, supplier.email)
        self.assertEqual(new_supplier.phone_number, supplier.phone_number)
        self.assertEqual(new_supplier.date_joined, supplier.date_joined)

    def test_deserialize_with_key_error(self):
        """It should not Deserialize an supplier with a KeyError"""
        supplier = Supplier()
        self.assertRaises(DataValidationError, supplier.deserialize, {})

    def test_deserialize_with_type_error(self):
        """It should not Deserialize an supplier with a TypeError"""
        supplier = Supplier()
        self.assertRaises(DataValidationError, supplier.deserialize, [])

######################################################################
#  I T E M   M O D E L   T E S T   C A S E S
######################################################################

    def test_deserialize_item_key_error(self):
        """It should not Deserialize an item with a KeyError"""
        item = Item()
        self.assertRaises(DataValidationError, item.deserialize, {})

    def test_deserialize_item_type_error(self):
        """It should not Deserialize an item with a TypeError"""
        item = Item()
        self.assertRaises(DataValidationError, item.deserialize, [])

    def test_add_supplier_item(self):
        """It should Create an supplier with an item and add it to the database"""
        suppliers = Supplier.all()
        self.assertEqual(suppliers, [])
        supplier = SupplierFactory()
        item = ItemFactory(supplier=supplier)
        supplier.items.append(item)
        supplier.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(supplier.id)
        suppliers = Supplier.all()
        self.assertEqual(len(suppliers), 1)

        new_supplier = Supplier.find(supplier.id)
        self.assertEqual(new_supplier.items[0].name, item.name)

        item2 = ItemFactory(supplier=supplier)
        supplier.items.append(item2)
        supplier.update()

        new_supplier = Supplier.find(supplier.id)
        self.assertEqual(len(new_supplier.items), 2)
        self.assertEqual(new_supplier.items[1].name, item2.name)

    def test_update_supplier_item(self):
        """It should Update an suppliers item"""
        suppliers = Supplier.all()
        self.assertEqual(suppliers, [])

        supplier = SupplierFactory()
        item = ItemFactory(supplier=supplier)
        supplier.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(supplier.id)
        suppliers = Supplier.all()
        self.assertEqual(len(suppliers), 1)

        # Fetch it back
        supplier = Supplier.find(supplier.id)
        old_item = supplier.items[0]
        print("%r", old_item)
        self.assertEqual(old_item.sku, item.sku)
        # Change the sku
        old_item.sku = "XXX1234"
        supplier.update()

        # Fetch it back again
        supplier = Supplier.find(supplier.id)
        item = supplier.items[0]
        self.assertEqual(item.sku, "XXX1234")

    def test_delete_supplier_item(self):
        """It should Delete an suppliers item"""
        suppliers = Supplier.all()
        self.assertEqual(suppliers, [])

        supplier = SupplierFactory()
        item = ItemFactory(supplier=supplier)
        supplier.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(supplier.id)
        suppliers = Supplier.all()
        self.assertEqual(len(suppliers), 1)

        # Fetch it back
        supplier = Supplier.find(supplier.id)
        item = supplier.items[0]
        item.delete()
        supplier.update()

        # Fetch it back again
        supplier = Supplier.find(supplier.id)
        self.assertEqual(len(supplier.items), 0)
