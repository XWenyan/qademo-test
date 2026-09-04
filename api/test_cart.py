import requests
import pytest

BASE_URL = "http://127.0.0.1:8787"


def test_get_empty_cart(api_session):
    response = api_session.get(
        "http://127.0.0.1:8787/api/cart"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert "data" in data

    cart = data["data"]

    assert cart["items"] == []
    assert cart["totalItems"] == 0
    assert cart["totalAmount"] == 0

    # 添加商品到购物车
def test_add_product_to_cart(api_session):
    response = api_session.post(
        f"{BASE_URL}/api/cart/items",
        json={
            "productId": 1,
            "quantity": 2,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["data"]["productId"] == 1
    assert data["data"]["quantity"] == 2
    assert data["data"]["totalItems"] == 2

# 重复添加同一商品，数量应该累加
def test_add_same_product_twice(api_session):
    # 第一次添加2件
    response = api_session.post(
        f"{BASE_URL}/api/cart/items",
        json={
            "productId": 1,
            "quantity": 2,
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["data"]["quantity"] == 2

    # 第二次添加3件
    response = api_session.post(
        f"{BASE_URL}/api/cart/items",
        json={
            "productId": 1,
            "quantity": 3,
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["data"]["productId"] == 1
    assert data["data"]["quantity"] == 5
    assert data["data"]["totalItems"] == 5

# 测试添加超过库存数量的商品
def test_add_product_exceed_stock(api_session):
    response = api_session.post(
        f"{BASE_URL}/api/cart/items",
        json={
            "productId": 3,
            "quantity": 6,
        },
    )

    assert response.status_code == 400

    data = response.json()

    assert data["success"] is False
    assert "error" in data

# 边界值测试 购买数量刚好等于库存
def test_add_product_exact_stock(api_session):
    response = api_session.post(
        f"{BASE_URL}/api/cart/items",
        json={
            "productId": 3,
            "quantity": 5,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["data"]["productId"] == 3
    assert data["data"]["quantity"] == 5
    assert data["data"]["totalItems"] == 5

# 测试添加商品后，购物车能够正确查询
def test_get_cart_after_adding_product(api_session):
    # 添加商品
    response = api_session.post(
        f"{BASE_URL}/api/cart/items",
        json={
            "productId": 1,
            "quantity": 2,
        },
    )

    assert response.status_code == 200

    # 查询购物车
    response = api_session.get(
        f"{BASE_URL}/api/cart"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    cart = data["data"]

    assert cart["totalItems"] == 2
    assert cart["totalAmount"] == 59.98
    assert len(cart["items"]) == 1

    item = cart["items"][0]

    assert item["productId"] == 1
    assert item["quantity"] == 2
    assert item["product"]["name"] == "Classic T-Shirt"

# 不存在的商品
def test_add_nonexistent_product(api_session):
    response = api_session.post(
        f"{BASE_URL}/api/cart/items",
        json={
            "productId": 99999,
            "quantity": 1,
        },
    )

    assert response.status_code == 404

    data = response.json()
    assert data["success"] is False

# 库存不足的商品
def test_add_out_of_stock_product(api_session):
    response = api_session.post(
        f"{BASE_URL}/api/cart/items",
        json={
            "productId": 4,
            "quantity": 1,
        },
    )

    assert response.status_code == 400

    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "OUT_OF_STOCK"

def test_add_quantity_exceeds_stock(api_session):
    response = api_session.post(
        f"{BASE_URL}/api/cart/items",
        json={
            "productId": 2,
            "quantity": 21,
        },
    )
    print(response.text)
    assert response.status_code == 400

    data = response.json()

    assert data["success"] is False
    assert data["error"]["code"] == "OUT_OF_STOCK"


def test_add_quantity_exceeds_stock_without_changing_cart(api_session):
    # 先加入 1 个商品
    response1 = api_session.post(
        f"{BASE_URL}/api/cart/items",
        json={
            "productId": 2,
            "quantity": 1,
        },
    )

    assert response1.status_code == 200

    # 再尝试加入 99 个，总数量一定超过当前库存
    response2 = api_session.post(
        f"{BASE_URL}/api/cart/items",
        json={
            "productId": 2,
            "quantity": 20,
        },
    )

    assert response2.status_code == 400

    data2 = response2.json()

    assert data2["success"] is False
    assert data2["error"]["code"] == "OUT_OF_STOCK"

    # 确认失败操作没有改变原来的购物车数量
    response3 = api_session.get(
        f"{BASE_URL}/api/cart"
    )

    assert response3.status_code == 200

    data3 = response3.json()

    assert data3["success"] is True
    assert data3["data"]["totalItems"] == 1
    assert data3["data"]["items"][0]["quantity"] == 1

@pytest.mark.parametrize(
    "quantity",
    [
        -1,
        -10,
        100,
        999,
    ],
)
def test_update_cart_with_invalid_quantity(api_session, quantity):
    # 先加入一个商品，确保购物车中存在该商品
    add_response = api_session.post(
        f"{BASE_URL}/api/cart/items",
        json={
            "productId": 1,
            "quantity": 1,
        },
    )

    assert add_response.status_code == 200

    # 使用非法数量修改商品
    response = api_session.patch(
        f"{BASE_URL}/api/cart/items/1",
        json={
            "quantity": quantity,
        },
    )

    assert response.status_code == 400

    data = response.json()
    assert data["success"] is False

def test_update_cart_quantity_to_zero_removes_item(api_session):
    # 先加入商品
    add_response = api_session.post(
        f"{BASE_URL}/api/cart/items",
        json={
            "productId": 1,
            "quantity": 2,
        },
    )

    assert add_response.status_code == 200

    # 将数量修改为 0
    response = api_session.patch(
        f"{BASE_URL}/api/cart/items/1",
        json={
            "quantity": 0,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["data"]["productId"] == 1
    assert data["data"]["quantity"] == 0
    assert data["data"]["totalItems"] == 0

    # 再次查询购物车，确认商品确实被删除
    cart_response = api_session.get(
        f"{BASE_URL}/api/cart"
    )

    assert cart_response.status_code == 200

    cart_data = cart_response.json()

    assert cart_data["data"]["totalItems"] == 0
    assert cart_data["data"]["items"] == []