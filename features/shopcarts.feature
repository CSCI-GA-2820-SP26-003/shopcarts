Feature: The shopcart admin service back-end
    As an eCommerce Manager
    I need a RESTful admin service
    So that I can manage shopping carts for all customers

Background:
    Given the following shopcarts
        | name            | userid  | status      |
        | Weekend Cart    | user001 | active      |
        | Holiday Cart    | user002 | active      |
        | Old Cart        | user003 | abandoned   |
        | Completed Cart  | user004 | checked_out |
    And the following items in shopcart "Weekend Cart"
        | product_id | name         | quantity | price |
        | PROD-001   | Blue T-Shirt | 2        | 19.99 |
        | PROD-002   | Red Hat      | 1        | 14.50 |
    And the following items in shopcart "Holiday Cart"
        | product_id | name         | quantity | price |
        | PROD-003   | Green Scarf  | 3        | 9.99  |

Scenario: The server is running
    When I am on the "Shopcart Admin" page
    Then I should see "Shopcart Admin" in the title

Scenario: Create a shopcart
    Given I am on the "Shopcart Admin" page
    When I set the "Shopcart Name" to "Birthday Cart"
    And I set the "Shopcart Userid" to "user099"
    And I select "Active" in the "Shopcart Status" dropdown
    And I press the "Create" button
    Then I should see the message "Success"
    And I should see "Birthday Cart" in the "Shopcart Name" field
    And I should see "user099" in the "Shopcart Userid" field
    When I press the "List" button
    Then I should see the message "Success"
    And I should see "Birthday Cart" in the results

Scenario: List all shopcarts
    Given I am on the "Shopcart Admin" page
    When I press the "List" button
    Then I should see the message "Success"
    And I should see "Weekend Cart" in the results
    And I should see "Holiday Cart" in the results
    And I should see "Old Cart" in the results
    And I should see "Completed Cart" in the results

Scenario: Query shopcarts by status
    Given I am on the "Shopcart Admin" page
    When I select "Active" in the "Shopcart Status" dropdown
    And I press the "Query" button
    Then I should see the message "Success"
    And I should see "Weekend Cart" in the results
    And I should see "Holiday Cart" in the results
    And I should not see "Old Cart" in the results
    And I should not see "Completed Cart" in the results

Scenario: Update a shopcart
    Given I am on the "Shopcart Admin" page
    When I press the "List" button
    Then I should see the message "Success"
    When I set the "Shopcart ID" to the ID of "Weekend Cart"
    And I set the "Shopcart Name" to "Updated Cart"
    And I set the "Shopcart Userid" to "user999"
    And I select "Abandoned" in the "Shopcart Status" dropdown
    And I press the "Update" button
    Then I should see the message "Success"
    And I should see "Updated Cart" in the "Shopcart Name" field
    And I should see "user999" in the "Shopcart Userid" field
    When I press the "List" button
    Then I should see the message "Success"
    And I should see "Updated Cart" in the results
    And I should not see "Weekend Cart" in the results

Scenario: Create an item in a shopcart
    Given I am on the "Shopcart Admin" page
    When I press the "List" button
    Then I should see the message "Success"
    When I set the "Item Shopcart ID" to the ID of "Weekend Cart"
    And I set the "Item Product ID" to "PROD-099"
    And I set the "Item Name" to "Yellow Jacket"
    And I set the "Item Quantity" to "5"
    And I set the "Item Price" to "49.99"
    And I press the "Create Item" button
    Then I should see the message "Success"
    And I should see "PROD-099" in the "Item Product ID" field
    And I should see "Yellow Jacket" in the "Item Name" field
    And I should see "5" in the "Item Quantity" field
    When I press the "Clear Item" button
    And I set the "Item Shopcart ID" to the ID of "Weekend Cart"
    And I press the "List Item" button
    Then I should see the message "Success"
    And I should see "Yellow Jacket" in the item results
    And I should see "Blue T-Shirt" in the item results

Scenario: Update an item in a shopcart
    Given I am on the "Shopcart Admin" page
    When I press the "List" button
    Then I should see the message "Success"
    When I set the "Item Shopcart ID" to the ID of "Weekend Cart"
    And I press the "List Item" button
    Then I should see the message "Success"
    When I set the "Item ID" to the item ID of "Blue T-Shirt"
    And I set the "Item Shopcart ID" to the ID of "Weekend Cart"
    And I set the "Item Product ID" to "PROD-001"
    And I set the "Item Name" to "Green T-Shirt"
    And I set the "Item Quantity" to "10"
    And I set the "Item Price" to "24.99"
    And I press the "Update Item" button
    Then I should see the message "Success"
    And I should see "Green T-Shirt" in the "Item Name" field
    And I should see "10" in the "Item Quantity" field
    When I press the "Clear Item" button
    And I set the "Item Shopcart ID" to the ID of "Weekend Cart"
    And I press the "List Item" button
    Then I should see the message "Success"
    And I should see "Green T-Shirt" in the item results
    And I should not see "Blue T-Shirt" in the item results

Scenario: Checkout a shopcart
    Given I am on the "Shopcart Admin" page
    When I press the "List" button
    Then I should see the message "Success"
    When I set the "Shopcart ID" to the ID of "Weekend Cart"
    And I press the "Checkout" button
    Then I should see the message "Success"
    And I should see "checked_out" in the "Shopcart Status" field
    When I press the "List" button
    Then I should see the message "Success"
    And I should see "Weekend Cart" in the results

Scenario: Delete a shopcart
    Given I am on the "Shopcart Admin" page
    When I press the "List" button
    Then I should see the message "Success"
    And I should see "Old Cart" in the results
    When I set the "Shopcart ID" to the ID of "Old Cart"
    And I press the "Delete" button
    Then I should see the message "Shopcart has been Deleted!"
    When I press the "List" button
    Then I should see the message "Success"
    And I should not see "Old Cart" in the results
    And I should see "Weekend Cart" in the results

Scenario: Delete an item from a shopcart
    Given I am on the "Shopcart Admin" page
    When I press the "List" button
    Then I should see the message "Success"
    When I set the "Item Shopcart ID" to the ID of "Weekend Cart"
    And I press the "List Item" button
    Then I should see the message "Success"
    And I should see "Blue T-Shirt" in the item results
    And I should see "Red Hat" in the item results
    When I set the "Item ID" to the item ID of "Red Hat"
    And I set the "Item Shopcart ID" to the ID of "Weekend Cart"
    And I press the "Delete Item" button
    Then I should see the message "Item has been Deleted!"
    When I set the "Item Shopcart ID" to the ID of "Weekend Cart"
    And I press the "List Item" button
    Then I should see the message "Success"
    And I should see "Blue T-Shirt" in the item results
    And I should not see "Red Hat" in the item results

Scenario: List items in a shopcart
    Given I am on the "Shopcart Admin" page
    When I press the "List" button
    Then I should see the message "Success"
    When I set the "Item Shopcart ID" to the ID of "Weekend Cart"
    And I press the "List Item" button
    Then I should see the message "Success"
    And I should see "Blue T-Shirt" in the item results
    And I should see "Red Hat" in the item results
    And I should not see "Green Scarf" in the item results
