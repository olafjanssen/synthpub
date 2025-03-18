"""
Integration tests for health endpoints.
"""


def test_health_check(client):
    """Test that the health check endpoint returns a healthy status."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
