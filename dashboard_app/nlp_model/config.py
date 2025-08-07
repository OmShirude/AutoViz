# This file centralizes configuration constants for the nlp_model.

# Mapping of table names to their Superset Datasource IDs.
# This is crucial for the final step of chart creation.
SUPERSET_DATASOURCE_IDS = {
    "actors": 24,
    "store": 41,
    "address": 25,
    "category": 26,
    "city": 29,
    "country": 30,
    "customer": 31,
    "film_actor": 33,
    "film_category": 34,
    "inventory": 35,
    "language": 36,
    "rental": 39,
    "staff": 40,
    "payment": 38,
    "film": 32,
}

# You can add other shared configurations here, such as primary key mappings
# if they are needed for rule-based fallbacks.
PRIMARY_KEYS = {
    "actors": "actor_id",
    "film": "film_id",
    "category": "category_id",
    "payment": "payment_id",
    "rental": "rental_id",
    "customer": "customer_id",
    "inventory": "inventory_id",
    "store": "store_id",
    "staff": "staff_id",
}
