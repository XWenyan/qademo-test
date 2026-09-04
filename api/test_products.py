import pytest
import requests

BASE_URL = "http://127.0.0.1:8787"

# 商品总信息查询
def test_get_products():
    response = requests.get(f"{BASE_URL}/api/products")

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert "data" in data
    assert "meta" in data

    assert isinstance(data["data"], list)
    assert data["meta"]["total"] == len(data["data"])

    assert len(data["data"]) > 0

@pytest.mark.parametrize(
    "slug, expected_name",
    [
        ("classic-t-shirt", "Classic T-Shirt"),
        ("wireless-headphones", "Wireless Headphones"),
        ("coffee-mug", "Coffee Mug"),
        ("laptop-stand", "Laptop Stand"),
    ],
)

def test_get_product_by_slug(slug, expected_name):
    response = requests.get(
        f"{BASE_URL}/api/products/{slug}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["data"]["slug"] == slug
    assert data["data"]["name"] == expected_name


# 测试不存在的商品
@pytest.mark.parametrize(
    "slug",
    [
        "not-exist",
        "abc123",
        "product-not-found",
    ],
)
def test_get_nonexistent_product(slug):
    response = requests.get(
        f"{BASE_URL}/api/products/{slug}"
    )

    assert response.status_code == 404

# 测试商品id
def test_get_product_by_id():
    response = requests.get(
        f"{BASE_URL}/api/products/id/1"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["data"]["id"] == 1
    assert data["data"]["name"] == "Classic T-Shirt"

# 不合法id id必须是大于0的整数
@pytest.mark.parametrize(
    "product_id",
    [
        0,
        -1,
        -100,
        "abc",
        "hello",
    ],
)
def test_get_product_by_invalid_id(product_id):
    response = requests.get(
        f"{BASE_URL}/api/products/id/{product_id}"
    )

    assert response.status_code == 400

# 合法但不存在id
def test_get_product_by_nonexistent_id():
    response = requests.get(
        f"{BASE_URL}/api/products/id/99999"
    )

    assert response.status_code == 404

# 边界测试
@pytest.mark.parametrize(
    "slug",
    [
        "-1",
        "0",
        "1",
    ],
)
def test_get_product_by_invalid_slug(slug):
    response = requests.get(
        f"{BASE_URL}/api/products/{slug}"
    )

    assert response.status_code == 404

# 上架中的商品有库存，缺货商品"old-backpack"不在商品列表中
def test_inactive_product_not_in_list():
    response = requests.get(f"{BASE_URL}/api/products")

    assert response.ok

    data = response.json()

    assert data["success"] is True

    products = data["data"]

    assert all(product["isActive"] is True for product in products)
    assert not any(product["slug"] == "old-backpack" for product in products)

# 下架商品无法访问
def test_inactive_product_not_accessible_by_slug():
    response = requests.get(f"{BASE_URL}/api/products/old-backpack")

    assert response.status_code == 404