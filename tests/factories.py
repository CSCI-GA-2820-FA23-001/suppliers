# Copyright 2016, 2019 John J. Rofrano. All Rights Reserved.
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
Test Factory to make fake objects for testing
"""
from datetime import date
import factory
from factory import Factory, Faker, Sequence, SubFactory
from factory.fuzzy import FuzzyChoice, FuzzyDate, FuzzyDecimal
from service.models import Supplier, Item

item_names = [
    "Shirt", "Pants", "Shoes", "Hat", "Gloves", "Coat", "Socks", "Ties"
]


class SupplierFactory(Factory):
    """Creates fake Suppliers"""

    # pylint: disable=too-few-public-methods
    class Meta:
        """Persistent class"""
        model = Supplier

    id = Sequence(lambda n: n)
    name = Faker("name")
    email = Faker("email")
    phone_number = Faker("phone_number")
    date_joined = FuzzyDate(date(2008, 1, 1))
    # the many side of relationships can be a little wonky in factory boy:
    # https://factoryboy.readthedocs.io/en/latest/recipes.html#simple-many-to-many-relationship

    @factory.post_generation
    def items(self, create, extracted, **kwargs):   # pylint: disable=method-hidden, unused-argument
        """Creates the items list"""
        if not create:
            return

        if extracted:
            self.items = extracted


class ItemFactory(Factory):
    """Creates fake Items"""

    # pylint: disable=too-few-public-methods
    class Meta:
        """Persistent class"""
        model = Item

    id = Sequence(lambda n: n)
    supplier_id = None
    sku = Sequence(lambda n: f"ABC{n:04d}")
    name = FuzzyChoice(choices=item_names)
    quantity = FuzzyChoice(choices=[10, 100, 500, 1000])
    price = FuzzyDecimal(0.50, 1000.00)
    supplier = SubFactory(SupplierFactory)
