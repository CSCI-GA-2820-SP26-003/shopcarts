"""
Models for Shopcart

All of the models are stored in this module
"""

import logging
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


class Item(db.Model):
    """
    Class that represents an Item in a Shopcart
    """

    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)
    shopcart_id = db.Column(db.Integer, db.ForeignKey("shopcart.id"), nullable=False)
    product_id = db.Column(db.String(63), nullable=False)
    name = db.Column(db.String(63), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<Item {self.name} product_id=[{self.product_id}] shopcart_id=[{self.shopcart_id}]>"

    def create(self):
        """Creates an Item in the database"""
        logger.info("Creating item %s", self.name)
        self.id = None  # pylint: disable=invalid-name
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error creating record: %s", self)
            raise DataValidationError(e) from e

    def update(self):
        """Updates an Item in the database"""
        logger.info("Saving item %s", self.name)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating record: %s", self)
            raise DataValidationError(e) from e

    def delete(self):
        """Removes an Item from the database"""
        logger.info("Deleting item %s", self.name)
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error deleting record: %s", self)
            raise DataValidationError(e) from e

    def serialize(self):
        """Serializes an Item into a dictionary"""
        return {
            "id": self.id,
            "shopcart_id": self.shopcart_id,
            "product_id": self.product_id,
            "name": self.name,
            "quantity": self.quantity,
            "price": self.price,
        }

    def deserialize(self, data):
        """
        Deserializes an Item from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.product_id = data["product_id"]
            self.name = data["name"]
            self.quantity = data.get("quantity", 1)
            self.price = data["price"]
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid Item: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Item: body of request contained bad or no data " + str(error)
            ) from error
        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def all(cls):
        """Returns all Items in the database"""
        logger.info("Processing all Items")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds an Item by its ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.session.get(cls, by_id)

    @classmethod
    def find_by_shopcart_id(cls, shopcart_id):
        """Returns all Items for a given shopcart_id"""
        logger.info("Processing item query for shopcart_id %s ...", shopcart_id)
        return cls.query.filter(cls.shopcart_id == shopcart_id)


class Shopcart(db.Model):
    """
    Class that represents a Shopcart
    """

    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63))
    userid = db.Column(db.String(73))
    active = db.Column(db.Boolean, default=True)
    items = db.relationship(
        "Item", backref="shopcart", lazy=True, cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Shopcart {self.name} id=[{self.id}]>"

    def create(self):
        """
        Creates a Shopcart to the database
        """
        logger.info("Creating %s", self.name)
        self.id = None  # pylint: disable=invalid-name
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error creating record: %s", self)
            raise DataValidationError(e) from e

    def update(self):
        """
        Updates a Shopcart to the database
        """
        logger.info("Saving %s", self.name)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating record: %s", self)
            raise DataValidationError(e) from e

    def delete(self):
        """Removes a Shopcart from the data store"""
        logger.info("Deleting %s", self.name)
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error deleting record: %s", self)
            raise DataValidationError(e) from e

    @property
    def total_price(self):
        """Calculates the total price of all items in the shopcart"""
        return sum(item.price * item.quantity for item in self.items)

    def serialize(self):
        """Serializes a Shopcart into a dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "userid": self.userid,
            "active": self.active,
            "items": [item.serialize() for item in self.items],
            "total_price": self.total_price,
        }

    def deserialize(self, data):
        """
        Deserializes a Shopcart from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.name = data["name"]
            self.userid = data.get("userid")
            self.active = data.get("active", True)
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid Shopcart: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Shopcart: body of request contained bad or no data "
                + str(error)
            ) from error
        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def all(cls):
        """Returns all of the Shopcarts in the database"""
        logger.info("Processing all Shopcarts")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a Shopcart by it's ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.session.get(cls, by_id)

    @classmethod
    def find_by_name(cls, name):
        """Returns all Shopcarts with the given name

        Args:
            name (string): the name of the Shopcarts you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)
