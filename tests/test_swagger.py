
"""
Test cases for verifying Swagger/OpenAPI integration

This test module ensures that the Swagger UI is properly configured and
available in the running application. It supplements the coverage for
the newly added Swagger integration in `service/__init__.py`.
"""

import unittest
from wsgi import app


class TestSwagger(unittest.TestCase):
    """Tests for Swagger/OpenAPI support"""

    @classmethod
    def setUpClass(cls):
        """
        Initialize once for all tests in this class.

        We enable testing mode on the Flask application so that exceptions are
        propagated to the test client and we can make test requests without
        running a server.
        """
        app.config["TESTING"] = True

    def test_swagger_config_present(self):
        """It should load the SWAGGER configuration on the app"""
        # The 'SWAGGER' key should be set in the application's config
        self.assertIn("SWAGGER", app.config)
        self.assertIn("title", app.config["SWAGGER"])

    def test_swagger_ui_available(self):
        """It should return HTTP 200 for the Swagger UI endpoint"""
        # Create a test client and request the Swagger UI page
        with app.test_client() as client:
            # `/apidocs/` is the default URI for flasgger's UI
            response = client.get("/apidocs/")
            self.assertEqual(
                response.status_code,
                200,
                "Expected 200 OK response for /apidocs/ but received %s" % response.status_code,
            )


if __name__ == "__main__":
    unittest.main()