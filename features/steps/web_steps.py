"""
Web Steps - step implementations for Selenium BDD tests
"""

import requests
from behave import given, when, then  # noqa: F811
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions


@given('the following shopcarts')
def step_impl(context):
    """Delete all shopcarts and load new ones"""
    # List all shopcarts
    rest_endpoint = f"{context.base_url}/shopcarts"
    context.resp = requests.get(rest_endpoint, timeout=context.wait_seconds)
    assert context.resp.status_code == 200

    # Delete all existing shopcarts
    for shopcart in context.resp.json():
        context.resp = requests.delete(
            f"{rest_endpoint}/{shopcart['id']}",
            timeout=context.wait_seconds
        )
        assert context.resp.status_code == 204

    # Create new shopcarts from the table
    for row in context.table:
        data = {
            "name": row["name"],
            "userid": row["userid"],
            "status": row["status"],
        }
        context.resp = requests.post(
            rest_endpoint,
            json=data,
            timeout=context.wait_seconds
        )
        assert context.resp.status_code == 201


@given('the following items in shopcart "{shopcart_name}"')
def step_impl(context, shopcart_name):
    """Load items into a named shopcart"""
    # Find the shopcart by name
    rest_endpoint = f"{context.base_url}/shopcarts"
    context.resp = requests.get(rest_endpoint, timeout=context.wait_seconds)
    assert context.resp.status_code == 200

    shopcart_id = None
    for shopcart in context.resp.json():
        if shopcart["name"] == shopcart_name:
            shopcart_id = shopcart["id"]
            break
    assert shopcart_id is not None, f"Shopcart '{shopcart_name}' not found"

    # Create items from the table
    for row in context.table:
        data = {
            "product_id": row["product_id"],
            "name": row["name"],
            "quantity": int(row["quantity"]),
            "price": float(row["price"]),
        }
        context.resp = requests.post(
            f"{rest_endpoint}/{shopcart_id}/items",
            json=data,
            timeout=context.wait_seconds
        )
        assert context.resp.status_code == 201


@given('I am on the "Shopcart Admin" page')
@when('I am on the "Shopcart Admin" page')
def step_impl(context):
    """Navigate to the admin page"""
    context.driver.get(f"{context.base_url}/admin")
    WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.title_contains("Shopcart Admin")
    )


@when('I set the "{element_name}" to "{text_string}"')
def step_impl(context, element_name, text_string):
    """Set a form field value"""
    element_id = element_name.lower().replace(" ", "_")
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(text_string)


@when('I select "{text}" in the "{element_name}" dropdown')
def step_impl(context, text, element_name):
    """Select a dropdown option by visible text"""
    element_id = element_name.lower().replace(" ", "_")
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    select = Select(element)
    select.select_by_visible_text(text)


@when('I press the "{button}" button')
def step_impl(context, button):
    """Click a button by its ID"""
    button_id = button.lower().replace(" ", "-") + "-btn"
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.element_to_be_clickable((By.ID, button_id))
    )
    element.click()


@then('I should see the message "{message}"')
def step_impl(context, message):
    """Check the flash message"""
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, "flash_message"), message
        )
    )
    assert found


@then('I should see "{text}" in the results')
def step_impl(context, text):
    """Check that text appears in the search results"""
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, "search_results"), text
        )
    )
    assert found


@then('I should not see "{text}" in the results')
def step_impl(context, text):
    """Check that text does NOT appear in the search results"""
    element = context.driver.find_element(By.ID, "search_results")
    assert text not in element.text


@then('I should see "{text}" in the item results')
def step_impl(context, text):
    """Check that text appears in the item results"""
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, "item_results"), text
        )
    )
    assert found


@then('I should not see "{text}" in the item results')
def step_impl(context, text):
    """Check that text does NOT appear in the item results"""
    element = context.driver.find_element(By.ID, "item_results")
    assert text not in element.text


@then('I should see "{value}" in the "{element_name}" field')
def step_impl(context, value, element_name):
    """Check the value of a form field"""
    element_id = element_name.lower().replace(" ", "_")
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    found = element.get_attribute("value")
    assert value == found, f"Expected '{value}' but got '{found}'"


@then('I should see "{text}" in the title')
def step_impl(context, text):
    """Check the page title"""
    assert text in context.driver.title


@when('I set the "{element_name}" to the ID of "{shopcart_name}"')
def step_impl(context, element_name, shopcart_name):
    """Find a shopcart ID from the results table and set it in a form field"""
    element_id = element_name.lower().replace(" ", "_")
    # Find the row containing the shopcart name and get the ID from the first column
    rows = context.driver.find_elements(By.CSS_SELECTOR, "#search_results_body tr")
    shopcart_id = None
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        if len(cells) >= 2 and cells[1].text == shopcart_name:
            shopcart_id = cells[0].text
            break
    assert shopcart_id is not None, f"Shopcart '{shopcart_name}' not found in results"

    element = context.driver.find_element(By.ID, element_id)
    element.clear()
    element.send_keys(shopcart_id)


@when('I set the "{element_name}" to the item ID of "{item_name}"')
def step_impl(context, element_name, item_name):
    """Find an item ID from the item results table and set it in a form field"""
    element_id = element_name.lower().replace(" ", "_")
    rows = context.driver.find_elements(By.CSS_SELECTOR, "#item_results_body tr")
    item_id = None
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        if len(cells) >= 4 and cells[3].text == item_name:
            item_id = cells[0].text
            break
    assert item_id is not None, f"Item '{item_name}' not found in item results"

    element = context.driver.find_element(By.ID, element_id)
    element.clear()
    element.send_keys(item_id)
