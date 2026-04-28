import requests

response = requests.get('http://localhost:8050/')
def test_dashboard():
    assert response.status_code == 200