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

Scenario: Search for shopcarts by status
    Given I am on the "Shopcart Admin" page
    When I select "Active" in the "Shopcart Status" dropdown
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Weekend Cart" in the results
    And I should see "Holiday Cart" in the results
    And I should not see "Old Cart" in the results
    And I should not see "Completed Cart" in the results

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
