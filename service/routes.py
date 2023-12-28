"""
My Service

Describe what your service does here
"""

from flask import jsonify, request, url_for, abort
from service.common import status  # HTTP Status Codes
from service.models import Supplier, Item

# Import Flask application
from . import app


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        jsonify(
            name="Supplier REST API Service",
            version="1.0",
            # paths=url_for("list_suppliers", _external=True),
        ),
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################

# ---------------------------------------------------------------------
#                S U P P L I E R   E N D P O I N T S
# ---------------------------------------------------------------------

######################################################################
# CREATE A NEW SUPPLIER
######################################################################
@app.route("/suppliers", methods=["POST"])
def create_suppliers():
    """
    Creates a Supplier
    This endpoint will create a Supplier based the data in the body that is posted
    """
    app.logger.info("Request to create a Supplier")
    check_content_type("application/json")

    # Create the supplier
    supplier = Supplier()
    supplier.deserialize(request.get_json())
    supplier.create()

    # Create a message to return
    message = supplier.serialize()
    location_url = url_for("get_suppliers", supplier_id=supplier.id, _external=True)

    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
# READ A SUPPLIER
######################################################################
@app.route("/suppliers/<int:supplier_id>", methods=["GET"])
def get_suppliers(supplier_id):
    """
    Retrieve a single Supplier

    This endpoint will return a Supplier based on it's id
    """
    app.logger.info("Request for Supplier with id: %s", supplier_id)

    # See if the supplier exists and abort if it doesn't
    supplier = Supplier.find(supplier_id)
    if not supplier:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Supplier with id '{supplier_id}' could not be found.",
        )

    return jsonify(supplier.serialize()), status.HTTP_200_OK


# ---------------------------------------------------------------------
#                  I T E M   E N D P O I N T S
# ---------------------------------------------------------------------

######################################################################
# ADD AN ITEM TO A SUPPLIER
######################################################################
@app.route("/suppliers/<int:supplier_id>/items", methods=["POST"])
def create_items(supplier_id):
    """
    Create an Item on a Supplier

    This endpoint will add an item to a supplier
    """
    app.logger.info("Request to create an Item for Supplier with id: %s", supplier_id)
    check_content_type("application/json")

    # See if the supplier exists and abort if it doesn't
    supplier = Supplier.find(supplier_id)
    if not supplier:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Supplier with id '{supplier_id}' could not be found.",
        )

    # Create an item from the json data
    item = Item()
    item.deserialize(request.get_json())

    # Append the item to the supplier
    supplier.items.append(item)
    supplier.update()

    # Prepare a message to return
    message = item.serialize()

    return jsonify(message), status.HTTP_201_CREATED


######################################################################
# READ AN ITEM FROM A SUPPLIER
######################################################################
@app.route("/suppliers/<int:supplier_id>/items/<int:item_id>", methods=["GET"])
def get_items(supplier_id, item_id):
    """
    Get an Item

    This endpoint returns just an item
    """
    app.logger.info(
        "Request to retrieve Item %s for Supplier id: %s", item_id, supplier_id
    )

    # See if the item exists and abort if it doesn't
    item = Item.find(item_id)
    if not item:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Supplier with id '{item_id}' could not be found.",
        )

    return jsonify(item.serialize()), status.HTTP_200_OK


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def check_content_type(media_type):
    """Checks that the media type is correct"""
    content_type = request.headers.get("Content-Type")
    if content_type and content_type == media_type:
        return
    app.logger.error("Invalid Content-Type: %s", content_type)
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {media_type}",
    )
