import pytest

BASE_URL = "http://127.0.0.1:8787"

# 管理员访问商品
def test_admin_get_products(admin_session):
    response = admin_session.get(
        f"{BASE_URL}/api/admin/products"
    )

    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert "meta" in data
    assert isinstance(data["data"], list)
    assert data["meta"]["total"] == len(data["data"])

# 管理员能看到全部商品包括下架的
def test_admin_can_see_inactive_products(admin_session):
    response = admin_session.get(
        f"{BASE_URL}/api/admin/products"
    )

    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True

    products = data["data"]

    # 至少存在一个下架商品
    assert any(product["isActive"] is False for product in products)

# 普通用户不能访问管理员商品接口
def test_standard_user_cannot_get_admin_products(auth_session):
    response = auth_session.get(
        f"{BASE_URL}/api/admin/products"
    )

    assert response.status_code == 403

    data = response.json()
    assert data["success"] is False
    assert "error" in data

# 未登录用户不能访问
def test_unauthenticated_cannot_get_admin_products(api_session):
    response = api_session.get(
        f"{BASE_URL}/api/admin/products"
    )

    assert response.status_code == 401

    data = response.json()
    assert data["success"] is False
    assert "error" in data

# 未登录不能修改
def test_unauthenticated_cannot_update_stock(api_session):
    response = api_session.patch(
        f"{BASE_URL}/api/admin/products/1/stock",
        json={
            "stock": 10
        },
    )

    assert response.status_code == 401

    data = response.json()
    assert data["success"] is False
    assert "error" in data

# 修改商品库存
def test_admin_update_product_stock(admin_session):
    # 先获取商品当前库存
    response = admin_session.get(
        f"{BASE_URL}/api/admin/products"
    )
    assert response.status_code == 200

    products = response.json()["data"]
    product = next(
        product for product in products
        if product["id"] == 1
    )

    old_stock = product["stock"]
    new_stock = old_stock + 10

    # 修改库存
    response = admin_session.patch(
        f"{BASE_URL}/api/admin/products/1/stock",
        json={
            "stock": new_stock
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert data["data"]["id"] == 1
    assert data["data"]["stock"] == new_stock

# 查询修改生效
def test_admin_stock_update_persists(admin_session):
    product_id = 1
    test_stock = 500

    # 修改库存
    response = admin_session.patch(
        f"{BASE_URL}/api/admin/products/{product_id}/stock",
        json={
            "stock": test_stock
        },
    )
    assert response.status_code == 200

    # 再次查询商品
    response = admin_session.get(
        f"{BASE_URL}/api/admin/products"
    )
    assert response.status_code == 200

    products = response.json()["data"]

    updated_product = next(
        product for product in products
        if product["id"] == product_id
    )

    assert updated_product["stock"] == test_stock

def test_admin_update_stock_with_negative_value(admin_session):
    response = admin_session.patch(
        f"{BASE_URL}/api/admin/products/1/stock",
        json={
            "stock": -1
        },
    )

    assert response.status_code == 400

    data = response.json()
    assert data["success"] is False
    assert "error" in data

# 不存在的商品
def test_admin_update_stock_for_nonexistent_product(admin_session):
    response = admin_session.patch(
        f"{BASE_URL}/api/admin/products/999999/stock",
        json={
            "stock": 10
        },
    )

    assert response.status_code == 404

    data = response.json()
    assert data["success"] is False
    assert "error" in data

# 非法商品id
def test_admin_update_stock_with_invalid_product_id(admin_session):
    response = admin_session.patch(
        f"{BASE_URL}/api/admin/products/abc/stock",
        json={
            "stock": 10
        },
    )

    assert response.status_code == 400

    data = response.json()
    assert data["success"] is False
    assert "error" in data

# 格式非法订单id
def test_admin_get_order_with_invalid_id(admin_session):
    response = admin_session.get(
        f"{BASE_URL}/api/admin/orders/abc"
    )

    assert response.status_code == 400

    data = response.json()
    assert data["success"] is False
    assert "error" in data

# 管理员访问订单
def test_admin_get_orders(admin_session):
    response = admin_session.get(
        f"{BASE_URL}/api/admin/orders"
    )

    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert "meta" in data
    assert isinstance(data["data"], list)
    assert data["meta"]["total"] == len(data["data"])

# 订单列表包含用户名
def test_admin_orders_contain_username(admin_session):
    response = admin_session.get(
        f"{BASE_URL}/api/admin/orders"
    )

    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True

    orders = data["data"]

    if orders:
        for order in orders:
            assert "username" in order
            assert order["username"]

# 返回商品详细信息
def test_admin_get_order_detail(admin_session):
    response = admin_session.get(
        f"{BASE_URL}/api/admin/orders"
    )

    assert response.status_code == 200

    orders = response.json()["data"]
    assert orders

    order_id = orders[0]["id"]

    response = admin_session.get(
        f"{BASE_URL}/api/admin/orders/{order_id}"
    )

    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert "data" in data

    order = data["data"]

    assert order["id"] == order_id
    assert "username" in order
    assert "items" in order
    assert isinstance(order["items"], list)

# 查询不存在订单的id
def test_admin_get_nonexistent_order(admin_session):
    response = admin_session.get(
        f"{BASE_URL}/api/admin/orders/999999"
    )

    assert response.status_code == 404

    data = response.json()
    assert data["success"] is False
    assert "error" in data

# 管理员修改订单状态
def test_admin_update_order_status(admin_session):
    response = admin_session.get(
        f"{BASE_URL}/api/admin/orders"
    )

    assert response.status_code == 200

    orders = response.json()["data"]
    assert orders

    order_id = orders[0]["id"]

    response = admin_session.patch(
        f"{BASE_URL}/api/admin/orders/{order_id}/status",
        json={
            "status": "processing"
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert data["data"]["id"] == order_id
    assert data["data"]["status"] == "processing"

# 非法订单状态
def test_admin_update_order_status_with_invalid_status(admin_session):
    response = admin_session.get(
        f"{BASE_URL}/api/admin/orders"
    )

    assert response.status_code == 200

    orders = response.json()["data"]
    assert orders

    order_id = orders[0]["id"]

    response = admin_session.patch(
        f"{BASE_URL}/api/admin/orders/{order_id}/status",
        json={
            "status": "confirmed"
        },
    )

    assert response.status_code == 400

    data = response.json()
    assert data["success"] is False
    assert "error" in data

# 修改不存在的订单
def test_admin_update_nonexistent_order_status(admin_session):
    response = admin_session.patch(
        f"{BASE_URL}/api/admin/orders/999999/status",
        json={
            "status": "processing"
        },
    )

    assert response.status_code == 404

    data = response.json()
    assert data["success"] is False
    assert "error" in data

# 获取后台统计数据
def test_admin_get_stats(admin_session):
    response = admin_session.get(
        f"{BASE_URL}/api/admin/stats"
    )

    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert "data" in data

    stats = data["data"]

    assert "counts" in stats
    assert "recentOrders" in stats
    assert "lowStockProducts" in stats

    assert isinstance(stats["counts"], dict)
    assert isinstance(stats["recentOrders"], list)
    assert isinstance(stats["lowStockProducts"], list)

# 统计字段合理
def test_admin_stats_counts_are_valid(admin_session):
    response = admin_session.get(
        f"{BASE_URL}/api/admin/stats"
    )

    assert response.status_code == 200

    counts = response.json()["data"]["counts"]

    assert isinstance(counts["products"], int)
    assert isinstance(counts["orders"], int)
    assert isinstance(counts["users"], int)
    assert isinstance(counts["pendingOrders"], int)

    assert counts["products"] >= 0
    assert counts["orders"] >= 0
    assert counts["users"] >= 0
    assert counts["pendingOrders"] >= 0

# 返回最近订单
def test_admin_stats_recent_orders(admin_session):
    response = admin_session.get(
        f"{BASE_URL}/api/admin/stats"
    )

    assert response.status_code == 200

    recent_orders = response.json()["data"]["recentOrders"]

    assert isinstance(recent_orders, list)
    assert len(recent_orders) <= 5

    for order in recent_orders:
        assert "id" in order
        assert "totalAmount" in order
        assert "status" in order
        assert "createdAt" in order
        assert "username" in order

# 低库存商品
def test_admin_stats_low_stock_products(admin_session):
    response = admin_session.get(
        f"{BASE_URL}/api/admin/stats"
    )

    assert response.status_code == 200

    low_stock_products = response.json()["data"]["lowStockProducts"]

    assert isinstance(low_stock_products, list)

    for product in low_stock_products:
        assert "id" in product
        assert "name" in product
        assert "stock" in product
        assert product["stock"] < 10
