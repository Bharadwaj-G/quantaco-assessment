"""Export the FastAPI app's OpenAPI spec to a file.

Run after any change to schemas.py/routers: python export_openapi.py
"""

import json

from main import app


def main() -> None:
    spec = app.openapi()
    with open("openapi.json", "w") as f:
        json.dump(spec, f, indent=2)
    print(f"Wrote openapi.json (OpenAPI {spec['openapi']})")


if __name__ == "__main__":
    main()
