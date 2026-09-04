import sqlite3


DB_PATH = r"D:\简历相关\ecommerce-main\.wrangler\state\v3\d1\miniflare-D1DatabaseObject\bfe3a90655e0541c8d38ae14bb1b2c9f2a148b8757332513053cf18af80b9760.sqlite"


def test_database_connection():
    connection = sqlite3.connect(DB_PATH)

    cursor = connection.cursor()

    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    )

    tables = [row[0] for row in cursor.fetchall()]

    connection.close()

    assert "users" in tables
    assert "products" in tables
    assert "orders" in tables
    assert "order_items" in tables

def test_create_order_persists_to_database(auth_session):
    # 1. 查询下单前库存
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT stock
        FROM products
        WHERE id = ?
        """,
        (1,),
    )

    stock_before = cursor.fetchone()[0]

    connection.close()

    # 2. 添加商品到购物车
    add_response = auth_session.post(
        "http://127.0.0.1:8787/api/cart/items",
        json={
            "productId": 1,
            "quantity": 2,
        },
    )

    assert add_response.status_code == 200

    # 3. 创建订单
    order_response = auth_session.post(
        "http://127.0.0.1:8787/api/orders",
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

    data = order_response.json()

    assert data["success"] is True

    order_id = data["data"]["id"]

    # 4. 验证 orders
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, user_id, total_amount, status
        FROM orders
        WHERE id = ?
        """,
        (order_id,),
    )

    order = cursor.fetchone()

    assert order is not None
    assert order[0] == order_id
    assert order[1] > 0
    assert order[2] == 59.98
    assert order[3] == "pending"

    # 5. 验证 order_items
    cursor.execute(
        """
        SELECT product_id, quantity, unit_price
        FROM order_items
        WHERE order_id = ?
        """,
        (order_id,),
    )

    order_item = cursor.fetchone()

    assert order_item is not None
    assert order_item[0] == 1
    assert order_item[1] == 2
    assert order_item[2] == 29.99

    # 6. 查询下单后库存
    cursor.execute(
        """
        SELECT stock
        FROM products
        WHERE id = ?
        """,
        (1,),
    )

    stock_after = cursor.fetchone()[0]

    connection.close()

    # 7. 验证库存减少了购买数量
    assert stock_after == stock_before - 2

# 加入超过库存的商品失败后，数据库中商品蒽对数量应该保持不变
def test_insufficient_stock_does_not_create_order(auth_session):
    product_id = 3

    # 1. 查询操作前的库存和订单数量
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT stock
        FROM products
        WHERE id = ?
        """,
        (product_id,),
    )
    stock_before = cursor.fetchone()[0]
    quantity = stock_before + 1

    cursor.execute(
        "SELECT COUNT(*) FROM orders"
    )
    order_count_before = cursor.fetchone()[0]

    connection.close()

    # 2. 尝试加入超过库存的商品
    response = auth_session.post(
        "http://127.0.0.1:8787/api/cart/items",
        json={
            "productId": product_id,
            "quantity": quantity,
        },
    )
    print(response.text)
    assert response.status_code == 400

    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "OUT_OF_STOCK"

    # 3. 验证数据库没有产生错误变化
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT stock
        FROM products
        WHERE id = ?
        """,
        (product_id,),
    )
    stock_after = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM orders"
    )
    order_count_after = cursor.fetchone()[0]

    connection.close()

    assert stock_after == stock_before
    assert order_count_after == order_count_before
