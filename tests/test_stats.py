def test_stats_endpoint_exists(client):
    response = client.get('/api/stats')
    assert response.status_code == 200
    data = response.get_json()
    assert 'total_loans' in data
    assert 'total_amount' in data
    assert 'avg_amount' in data
    assert 'by_status' in data
    assert 'by_currency' in data