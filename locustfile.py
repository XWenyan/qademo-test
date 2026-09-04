import random
import uuid

from locust import HttpUser, task, between

from api.test_data.performance_data import (
    STANDARD_USER,
    ADD_TO_CART_QUANTITY,
)


class ProductUser(HttpUser):
    wait_time = between(1, 2)

    def on_start(self):
        """每个虚拟用户启动时执行一次登录。"""
        self.session_id = str(uuid.uuid4())

        response = self.client.post(
            "/api/auth/login",
            json=STANDARD_USER,
            headers={
                "X-Session-ID": self.session_id,
            },
            name="用户登录",
        )

        if response.status_code != 200:
            response.failure(
                f"登录失败: HTTP {response.status_code}"
            )
            return

        data = response.json()

        if not data.get("success"):
            response.failure("登录接口返回 success=false")
            return

        access_token = data["data"]["accessToken"]

        self.auth_headers = {
            "X-Session-ID": self.session_id,
            "Authorization": f"Bearer {access_token}",
        }

    @task
    def shopping_flow(self):
        """模拟用户完整购物浏览流程。"""

        # 1. 浏览商品列表
        products_response = self.client.get(
            "/api/products",
            headers=self.auth_headers,
            name="浏览商品列表",
        )

        if products_response.status_code != 200:
            return

        products_data = products_response.json()

        if not products_data.get("success"):
            products_response.failure(
                "商品列表接口返回 success=false"
            )
            return

        products = products_data.get("data", [])

        available_products = [
            product
            for product in products
            if product.get("stock", 0) > 0
        ]
        
        if not available_products:
            products_response.failure("没有可购买的商品")
            return
        product = random.choice(available_products)

        print(
            "选择商品:",
            product["id"],
            product["slug"],
            "stock:",
            product.get("stock")
        )

        product_id = product["id"]
        product_slug = product["slug"]

        # 3. 查看刚刚选择的商品详情
        detail_response = self.client.get(
            f"/api/products/{product_slug}",
            headers=self.auth_headers,
            name="查看商品详情",
        )

        if detail_response.status_code != 200:
            return

        # 4. 将同一个商品加入购物车
        add_cart_response = self.client.post(
            "/api/cart/items",
            json={
                "productId": product_id,
                "quantity": ADD_TO_CART_QUANTITY,
            },
            headers=self.auth_headers,
            name="加入购物车",
        )

        if add_cart_response.status_code != 200:
            print(
                "加入购物车失败:",
                add_cart_response.status_code,
                add_cart_response.text,
                "product_id:",
                product_id,
                "product_slug:",
                product_slug,
            )
            return

        # 5. 查看购物车
        self.client.get(
            "/api/cart",
            headers=self.auth_headers,
            name="查看购物车",
        )