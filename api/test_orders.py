import requests
import pytest

BASE_URL = "http://127.0.0.1:8787"

def test_get_orders(auth_session):
    response = auth_session.get(
        f"{BASE_URL}/api/orders"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert "data" in data
    assert "meta" in data

    assert isinstance(data["data"], list)
    assert data["meta"]["total"] == len(data["data"])

def test_get_orders_without_auth(api_session):
    response = api_session.get(
        f"{BASE_URL}/api/orders"
    )

    assert response.status_code == 401

def test_create_order(auth_session):
    # 1. 添加商品到购物车
    add_response = auth_session.post(
        f"{BASE_URL}/api/cart/items",
        json={
            "productId": 1,
            "quantity": 2,
        },
    )

    assert add_response.status_code == 200

    # 2. 创建订单
    order_response = auth_session.post(
        f"{BASE_URL}/api/orders",
        json={
            "shipping": {
                "firstName": "Test",
                "lastName": "User",
                "address": "123 Test Street",
            },
            "payment": {
                "cardNumber": "4242424242424242",
                "expiryDate": "12/30",
                "cvv": "123",
                "cardholderName": "Test User",
            },
        },
    )
    print(order_response.text)
    assert order_response.status_code == 201

    data = order_response.json()

    assert data["success"] is True
    assert "data" in data

    order = data["data"]

    assert order["id"] > 0
    assert order["totalAmount"] == 59.98
    assert order["status"] == "pending"

# 验证下单后的购物车和库存
def test_create_order_updates_cart_and_stock(auth_session):
    # 1. 获取下单前的商品库存
    product_response = auth_session.get(
        f"{BASE_URL}/api/products/id/2"
    )

    assert product_response.status_code == 200

    before_stock = product_response.json()["data"]["stock"]

    # 2. 加入购物车
    quantity = 2

    add_response = auth_session.post(
        f"{BASE_URL}/api/cart/items",
        json={
            "productId": 2,
            "quantity": quantity,
        },
    )

    assert add_response.status_code == 200

    # 3. 创建订单
    order_response = auth_session.post(
        f"{BASE_URL}/api/orders",
        json={
            "shipping": {
                "firstName": "Test",
                "lastName": "User",
                "address": "123 Test Street",
            },
            "payment": {
                "cardNumber": "4242424242424242",
                "expiryDate": "12/30",
                "cvv": "123",
                "cardholderName": "Test User",
            },
        },
    )

    assert order_response.status_code == 201

    # 4. 验证库存减少
    product_response = auth_session.get(
        f"{BASE_URL}/api/products/id/2"
    )

    assert product_response.status_code == 200

    after_stock = product_response.json()["data"]["stock"]

    assert after_stock == before_stock - quantity

    # 5. 验证购物车已经清空
    cart_response = auth_session.get(
        f"{BASE_URL}/api/cart"
    )

    assert cart_response.status_code == 200

    cart_data = cart_response.json()["data"]

    assert cart_data["items"] == []
    assert cart_data["totalItems"] == 0
    assert cart_data["totalAmount"] == 0

# 空购物车下单
def test_create_order_with_empty_cart(auth_session):
    response = auth_session.post(
        f"{BASE_URL}/api/orders",
        json={
            "shipping": {
                "firstName": "Test",
                "lastName": "User",
                "address": "123 Test Street",
            },
            "payment": {
                "cardNumber": "4242424242424242",
                "expiryDate": "12/30",
                "cvv": "123",
                "cardholderName": "Test User",
            },
        },
    )

    assert response.status_code == 400

    data = response.json()

    assert data["success"] is False
    assert data["error"]["code"] == "CART_EMPTY"


@pytest.mark.parametrize(
    "card_number",
    [
        "1234567890123456",
        "1111111111111111",
        "1234",
        "abc",
    ],
)
def test_create_order_with_invalid_card(auth_session, card_number):
    # 先加入商品
    add_response = auth_session.post(
        f"{BASE_URL}/api/cart/items",
        json={
            "productId": 1,
            "quantity": 1,
        },
    )

    assert add_response.status_code == 200

    # 使用非法银行卡号创建订单
    response = auth_session.post(
        f"{BASE_URL}/api/orders",
        json={
            "shipping": {
                "firstName": "Test",
                "lastName": "User",
                "address": "123 Test Street",
            },
            "payment": {
                "cardNumber": card_number,
                "expiryDate": "12/30",
                "cvv": "123",
                "cardholderName": "Test User",
            },
        },
    )

    assert response.status_code == 400

    data = response.json()

    assert data["success"] is False

def test_get_order_detail(auth_session):
    # 1. 加入商品
    add_response = auth_session.post(
        f"{BASE_URL}/api/cart/items",
        json={
            "productId": 1,
            "quantity": 1,
        },
    )

    assert add_response.status_code == 200

    # 2. 创建订单
    create_response = auth_session.post(
        f"{BASE_URL}/api/orders",
        json={
            "shipping": {
                "firstName": "Test",
                "lastName": "User",
                "address": "123 Test Street",
            },
            "payment": {
                "cardNumber": "4242424242424242",
                "expiryDate": "12/30",
                "cvv": "123",
                "cardholderName": "Test User",
            },
        },
    )

    assert create_response.status_code == 201

    order_id = create_response.json()["data"]["id"]

    # 3. 查询订单详情
    response = auth_session.get(
        f"{BASE_URL}/api/orders/{order_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["data"]["id"] == order_id
    assert "items" in data["data"]
    assert len(data["data"]["items"]) > 0

# 非法订单id
def test_get_nonexistent_order(auth_session):
    response = auth_session.get(
        f"{BASE_URL}/api/orders/99999"
    )

    assert response.status_code == 404

    data = response.json()

    assert data["success"] is False

@pytest.mark.parametrize(
    "order_id",
    [
        "abc",
        "hello",
        "0",
        "-1",
    ],
)
def test_get_order_with_invalid_id(auth_session, order_id):
    response = auth_session.get(
        f"{BASE_URL}/api/orders/{order_id}"
    )

    assert response.status_code == 400
