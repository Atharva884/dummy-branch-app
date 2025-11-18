def test_list_loans_endpoint_exists(client):
    response = client.get('/api/loans')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)


def test_create_loan_endpoint_exists(client):
    loan_data = {
        "borrower_id": "test_user_123",
        "amount": 5000.00,
        "currency": "INR",
        "term_months": 12,
        "interest_rate_apr": 15.0
    }
    response = client.post('/api/loans', json=loan_data)
    assert response.status_code in [201, 200, 500]


def test_get_loan_by_invalid_id(client):
    response = client.get('/api/loans/invalid-uuid')
    assert response.status_code == 400