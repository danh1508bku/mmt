# Example usage
import json

from daemon.weaprous import WeApRous


def create_sampleapp():
    """Create and return a sample WeApRous application."""
    app = WeApRous()

    @app.route("/", methods=["GET"])
    def home(headers=None, body=None, cookies=None, request=None):
        return {"message": "Welcome to the RESTful TCP WebApp"}

    @app.route("/user", methods=["GET"])
    def get_user(headers=None, body=None, cookies=None, request=None):
        return {"id": 1, "name": "Alice", "email": "alice@example.com"}

    @app.route("/echo", methods=["POST"])
    def echo(headers=None, body=None, cookies=None, request=None):
        try:
            data = json.loads(body) if body else {}
            return {"received": data}
        except (json.JSONDecodeError, ValueError):
            return {"error": "Invalid JSON"}

    return app

