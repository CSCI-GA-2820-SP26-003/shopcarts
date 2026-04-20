# pylint: disable=cyclic-import
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
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
Package: service
Package for the application models and service routes
This module creates and configures the Flask app and sets up the logging
and SQL database
"""
import sys
from flask import Flask
from flask_restx import Api
# Enable Swagger/OpenAPI support using Flasgger
try:
    # Import Swagger lazily; this lets the service run even if the optional dependency
    # isn't installed in certain environments. When flasgger is available, it will
    # automatically register a Swagger UI at `/apidocs`.
    from flasgger import Swagger  # type: ignore
except ImportError:
    Swagger = None  # type: ignore
from service import config
from service.common import log_handlers

# Create Flask-RESTX API，for initializing Swagger documents
api = Api(
    title="Shopcarts REST API Service",
    version="1.0",
    description="API for managing shopcarts and items",
    doc="/apidocs",  # document path
)

############################################################
# Initialize the Flask instance
############################################################


def create_app():
    """Initialize the core application."""
    # Create Flask application
    app = Flask(__name__)
    app.config.from_object(config)

    # Configure Swagger UI if the flasgger dependency is available.  The SWAGGER
    # configuration defines the page title and UI version.  If Swagger is not
    # installed, the service will still run normally without exposing an API
    # documentation endpoint.
    app.config.setdefault(
        "SWAGGER",
        {
            "title": "Shopcarts REST API",
            "uiversion": 3,
        },
    )
    if Swagger:
        Swagger(app)

    # Initialize Plugins
    # pylint: disable=import-outside-toplevel
    from service.models import db

    db.init_app(app)

    api.init_app(app)
    # Integrating Flask-RESTX with a Flask application

    with app.app_context():
        # Dependencies require we import the routes AFTER the Flask app is created
        # pylint: disable=wrong-import-position, wrong-import-order, unused-import
        from service import routes, models  # noqa: F401 E402
        from service.common import error_handlers, cli_commands  # noqa: F401, E402

        try:
            db.create_all()
        except Exception as error:  # pylint: disable=broad-except
            app.logger.critical("%s: Cannot continue", error)
            # gunicorn requires exit code 4 to stop spawning workers when they die
            sys.exit(4)

        # Set up logging for production
        log_handlers.init_logging(app, "gunicorn.error")

        app.logger.info(70 * "*")
        app.logger.info("  S E R V I C E   R U N N I N G  ".center(70, "*"))
        app.logger.info(70 * "*")

        app.logger.info("Service initialized!")

        return app
