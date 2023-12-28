"""
Models for Supplier

All of the models are stored in this module
"""
import logging
from datetime import date
from abc import abstractmethod
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


def init_db(app):
    """Initialize the SQLAlchemy app"""
    Supplier.init_db(app)


######################################################################
#  P E R S I S T E N T   B A S E   M O D E L
######################################################################
class PersistentBase:
    """Base class added persistent methods"""

    def __init__(self):
        self.id = None  # pylint: disable=invalid-name

    @abstractmethod
    def serialize(self) -> dict:
        """Convert an object into a dictionary"""

    @abstractmethod
    def deserialize(self, data: dict) -> None:
        """Convert a dictionary into an object"""

    def create(self):
        """
        Creates a Supplier to the database
        """
        logger.info("Creating %s", self.name)
        self.id = None  # id must be none to generate next primary key
        db.session.add(self)
        db.session.commit()

    def update(self):
        """
        Updates a Supplier to the database
        """
        logger.info("Updating %s", self.name)
        db.session.commit()

    def delete(self):
        """Removes a Supplier from the data store"""
        logger.info("Deleting %s", self.name)
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def init_db(cls, app):
        """Initializes the database session"""
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """Returns all of the records in the database"""
        logger.info("Processing all records")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a record by it's ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)


######################################################################
#  I T E M   M O D E L
######################################################################
class Item(db.Model, PersistentBase):
    """
    Class that represents an Item
    """

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey("supplier.id", ondelete="CASCADE"), nullable=False)
    sku = db.Column(db.String(12), nullable=False)        # Stock Keeping Unit
    name = db.Column(db.String(64), nullable=False)       # The name of the item
    quantity = db.Column(db.Integer, nullable=False)      # The minimum quantity that must be ordered
    price = db.Column(db.Numeric(10, 2), nullable=False)  # Price with 2 decimal places

    def __repr__(self):
        return f"<Item {self.id}>"

    def __str__(self):
        return f"{self.name}"

    def serialize(self) -> dict:
        """Converts an Item into a dictionary"""
        return {
            "id": self.id,
            "supplier_id": self.supplier_id,
            "sku": self.sku,
            "name": self.name,
            "quantity": self.quantity,
            "price": self.price
        }

    def deserialize(self, data: dict) -> None:
        """
        Populates an Item from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.supplier_id = data["supplier_id"]
            self.sku = data["sku"]
            self.name = data["name"]
            self.quantity = data["quantity"]
            self.price = data["price"]
        except KeyError as error:
            raise DataValidationError("Invalid Item: missing " + error.args[0]) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Item: body of request contained bad or no data "
                + error.args[0]
            ) from error
        return self


######################################################################
#  S U P P L I E R   M O D E L
######################################################################
class Supplier(db.Model, PersistentBase):
    """
    Class that represents a Supplier
    """

    app = None

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    email = db.Column(db.String(64))
    phone_number = db.Column(db.String(32), nullable=True)  # phone number is optional
    date_joined = db.Column(db.Date(), nullable=False, default=date.today())
    items = db.relationship("Item", backref="supplier", passive_deletes=True)

    def __repr__(self):
        return f"<Supplier {self.name} id=[{self.id}]>"

    def serialize(self):
        """Converts a Supplier into a dictionary"""
        supplier = {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone_number": self.phone_number,
            "date_joined": self.date_joined.isoformat(),
            "items": [],
        }
        for item in self.items:
            supplier["items"].append(item.serialize())
        return supplier

    def deserialize(self, data):
        """
        Populates a Supplier from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.name = data["name"]
            self.email = data["email"]
            self.phone_number = data.get("phone_number")
            self.date_joined = date.fromisoformat(data["date_joined"])
            # handle inner list of items
            item_list = data.get("items")
            for json_item in item_list:
                item = Item()
                item.deserialize(json_item)
                self.items.append(item)
        except KeyError as error:
            raise DataValidationError("Invalid Supplier: missing " + error.args[0]) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Supplier: body of request contained "
                "bad or no data - " + error.args[0]
            ) from error
        return self

    @classmethod
    def find_by_name(cls, name):
        """Returns all Suppliers with the given name

        Args:
            name (string): the name of the Suppliers you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)
