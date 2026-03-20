def test_dashboard_endpoint(client):
    response = client.get("/api/v1/dashboard")
    assert response.status_code == 200
    payload = response.json()
    assert payload["topThemes"]
    assert payload["latestNews"]
    assert payload["featuredRanking"]


def test_stock_detail_endpoint(client):
    response = client.get("/api/v1/stocks/000660")
    assert response.status_code == 200
    payload = response.json()
    assert payload["forecast"]["disclaimer"]
    assert payload["priceSeries"]
    assert payload["timeline"]
    assert payload["priceTimeframe"]
    assert payload["priceSource"]


def test_theme_and_article_flow(client):
    theme_response = client.get("/api/v1/themes/ai-infrastructure")
    assert theme_response.status_code == 200
    theme_payload = theme_response.json()
    assert theme_payload["ranking"]

    article_id = theme_payload["articles"][0]["id"]
    article_response = client.get(f"/api/v1/articles/{article_id}")
    assert article_response.status_code == 200
    article_payload = article_response.json()
    assert article_payload["linkedStocks"]
