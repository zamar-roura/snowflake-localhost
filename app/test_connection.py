import json

import requests


def test_connection():
    connection_params = {
        "warehouse": "VWH_DEVELOPMENT",
        "database": "DWH_FEVER",
        "role": "ROLE_GROUP_TEAM_DATA_ENGINEER",
    }

    # Test connection
    print("Testing connection...")
    response = requests.post(
        "http://localhost:4566/v1/connection",
        json=connection_params,
        headers={"Content-Type": "application/json"},
    )
    print("Connection response:", response.json())

    if response.status_code == 200:
        connection_id = response.json().get("connection_id")

        # Test simple query
        print("\nTesting query...")
        query_params = {"connection_id": connection_id, "query": "SELECT 1 as test"}
        response = requests.post(
            "http://localhost:4566/v1/query",
            json=query_params,
            headers={"Content-Type": "application/json"},
        )
        print("Query response:", response.json())

        # Close connection
        print("\nClosing connection...")
        response = requests.delete(
            f"http://localhost:4566/v1/connection/{connection_id}",
            headers={"Content-Type": "application/json"},
        )
        print("Close response:", response.json())


if __name__ == "__main__":
    test_connection()
