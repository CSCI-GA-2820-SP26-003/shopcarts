# Shopcarts Service

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)

## Overview

The Shopcarts service allows customers to manage a collection of products they want to purchase. Each shopcart is associated with a customer via their customer ID and can contain multiple items. Each item references a product ID, name, quantity, and price at the time it was added.

## Running the Service

**Install dependencies:**
```bash
make install
```

**Start the service** (runs on `http://localhost:8080`):
```bash
make run
```

## Running Tests

```bash
make test
```

Tests require 95% minimum code coverage. To also run linting:
```bash
make lint
```

## Data Models

### Shopcart
| Field    | Type    | Required | Description                      |
|----------|---------|----------|----------------------------------|
| id       | Integer | auto     | Primary key                      |
| name     | String  | yes      | Shopcart name                    |
| userid   | String  | no       | Customer ID (associates cart to customer) |
| active   | Boolean | no       | Whether the cart is active (default: true) |
| items    | List    | auto     | Collection of items in the cart  |

### Item
| Field       | Type    | Required | Description                   |
|-------------|---------|----------|-------------------------------|
| id          | Integer | auto     | Primary key                   |
| shopcart_id | Integer | auto     | Foreign key to parent shopcart |
| product_id  | String  | yes      | Product identifier            |
| name        | String  | yes      | Product name                  |
| quantity    | Integer | no       | Quantity to purchase (default: 1) |
| price       | Float   | yes      | Price at time of adding to cart |

## API Reference

### Service Info

#### GET /

Returns service metadata.

```
Response 200:
{
  "name": "Shopcart REST API Service",
  "version": "1.0",
  "paths": "..."
}
```

---

### Shopcarts

#### GET /shopcarts

List all shopcarts. Optionally filter by name using `?name=<name>`.

```
Response 200: [ { shopcart objects... } ]
```

#### POST /shopcarts

Create a new shopcart.

```
Content-Type: application/json

Body:
{
  "name": "My Cart",
  "userid": "customer-123",
  "active": true
}

Response 201: { created shopcart }
Header: Location: /shopcarts/<id>
```

#### GET /shopcarts/\<shopcart_id\>

Retrieve a shopcart by ID, including its items.

```
Response 200: { shopcart with items }
Response 404: shopcart not found
```

#### PUT /shopcarts/\<shopcart_id\>

Update an existing shopcart.

```
Content-Type: application/json

Body:
{
  "name": "Updated Name",
  "userid": "customer-123",
  "active": false
}

Response 200: { updated shopcart }
Response 404: shopcart not found
```

#### DELETE /shopcarts/\<shopcart_id\>

Delete a shopcart and all its items.

```
Response 204: (no content)
Response 404: shopcart not found
```

---

### Items (subordinate resource)

#### GET /shopcarts/\<shopcart_id\>/items

List all items in a shopcart.

```
Response 200: [ { item objects... } ]
Response 404: shopcart not found
```

#### POST /shopcarts/\<shopcart_id\>/items

Add an item to a shopcart.

```
Content-Type: application/json

Body:
{
  "product_id": "prod-456",
  "name": "Wireless Mouse",
  "quantity": 2,
  "price": 29.99
}

Response 201: { created item }
Header: Location: /shopcarts/<shopcart_id>/items/<item_id>
Response 404: shopcart not found
```

#### GET /shopcarts/\<shopcart_id\>/items/\<item_id\>

Retrieve a specific item from a shopcart.

```
Response 200: { item object }
Response 404: shopcart or item not found
```

#### PUT /shopcarts/\<shopcart_id\>/items/\<item_id\>

Update an item in a shopcart.

```
Content-Type: application/json

Body:
{
  "product_id": "prod-456",
  "name": "Wireless Mouse",
  "quantity": 3,
  "price": 29.99
}

Response 200: { updated item }
Response 404: shopcart or item not found
```

#### DELETE /shopcarts/\<shopcart_id\>/items/\<item_id\>

Remove an item from a shopcart.

```
Response 204: (no content)
Response 404: shopcart or item not found
```

---

## Project Structure

```
service/
├── models.py       - Shopcart and Item models (SQLAlchemy)
├── routes.py       - REST API route handlers
└── common/
    ├── error_handlers.py  - HTTP error responses
    ├── log_handlers.py    - Logging setup
    └── status.py          - HTTP status constants

tests/
├── factories.py        - Factory Boy factories for test data
├── test_models.py      - Model unit tests
└── test_routes.py      - API route tests
```

## License

Copyright (c) 2016, 2025 [John Rofrano](https://www.linkedin.com/in/JohnRofrano/). All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the NYU masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies**.
