from playwright.sync_api import Page, expect

# 登录成功
def test_login_success(page: Page):
    page.goto("http://127.0.0.1:8787/login")

    page.get_by_placeholder("Enter your username").fill("standard_user")
    page.get_by_placeholder("Enter your password").fill("standard123")

    page.get_by_test_id("login-submit-button").click()

    expect(page).not_to_have_url("http://127.0.0.1:8787/login")

# 登录失败
def test_login_wrong_password(page: Page):
    page.goto("http://127.0.0.1:8787/login")

    page.get_by_placeholder("Enter your username").fill("standard_user")
    page.get_by_placeholder("Enter your password").fill("wrong_password")

    page.get_by_test_id("login-submit-button").click()

    expect(page).to_have_url("http://127.0.0.1:8787/login")

# 登录页面元素校验
def test_login_page_elements(page: Page):
    page.goto("http://127.0.0.1:8787/login")

    expect(
        page.get_by_placeholder("Enter your username")
    ).to_be_visible()

    expect(
        page.get_by_placeholder("Enter your password")
    ).to_be_visible()

    expect(
        page.get_by_test_id("login-submit-button")
    ).to_be_visible()

# 验证商品列表
def test_product_catalog(page: Page):
    page.goto("http://127.0.0.1:8787/catalog")

    expect(
        page.get_by_role("heading", name="Product Catalog")
    ).to_be_visible()

    expect(
        page.get_by_text("Browse our complete selection of 4 products")
    ).to_be_visible()

    expect(page.get_by_text("Classic T-Shirt", exact=True)).to_be_visible()
    expect(page.get_by_text("Coffee Mug", exact=True)).to_be_visible()
    expect(page.get_by_text("Laptop Stand", exact=True)).to_be_visible()
    expect(page.get_by_text("Wireless Headphones", exact=True)).to_be_visible()

# 加入购物车
def test_add_product_to_cart(page: Page):
    page.goto("http://127.0.0.1:8787/catalog")

    product = page.get_by_text("Classic T-Shirt", exact=True).locator("..")

    product.get_by_role("button", name="Add").click()

    page.get_by_role("link", name="Shopping cart").click()

    expect(
        page.get_by_text("Classic T-Shirt", exact=True)
    ).to_be_visible()

# 验证购物车数量
def test_cart_quantity_after_adding_product(page: Page):
    page.goto("http://127.0.0.1:8787/catalog")

    product = page.get_by_text("Classic T-Shirt", exact=True).locator("..")
    product.get_by_role("button", name="Add").click()

    page.get_by_role("link", name="Shopping cart").click()

    expect(
        page.get_by_test_id("cart-item-quantity-1")
    ).to_have_text("1")

# 增加购物车数量
def test_increase_cart_quantity(page: Page):
    page.goto("http://127.0.0.1:8787/catalog")

    product = page.get_by_text("Classic T-Shirt", exact=True).locator("..")
    product.get_by_role("button", name="Add").click()

    page.get_by_role("link", name="Shopping cart").click()

    expect(
        page.get_by_test_id("cart-item-quantity-1")
    ).to_have_text("1")

    page.get_by_test_id("cart-item-increase-1").click()

    expect(
        page.get_by_test_id("cart-item-quantity-1")
    ).to_have_text("2")

# 减少购物车数量
def test_decrease_cart_quantity(page: Page):
    page.goto("http://127.0.0.1:8787/catalog")

    product = page.get_by_text("Classic T-Shirt", exact=True).locator("..")
    product.get_by_role("button", name="Add").click()

    page.get_by_role("link", name="Shopping cart").click()

    page.get_by_test_id("cart-item-increase-1").click()

    expect(
        page.get_by_test_id("cart-item-quantity-1")
    ).to_have_text("2")

    page.get_by_test_id("cart-item-decrease-1").click()

    expect(
        page.get_by_test_id("cart-item-quantity-1")
    ).to_have_text("1")

# 删除购物车商品
def test_remove_product_from_cart(page: Page):
    page.goto("http://127.0.0.1:8787/catalog")

    product = page.get_by_text("Classic T-Shirt", exact=True).locator("..")
    product.get_by_role("button", name="Add").click()

    page.get_by_role("link", name="Shopping cart").click()

    expect(
        page.get_by_text("Classic T-Shirt", exact=True)
    ).to_be_visible()

    page.get_by_test_id("cart-item-remove-1").click()

    expect(
        page.get_by_text("Classic T-Shirt", exact=True)
    ).not_to_be_visible()

# 空购物车状态
def test_empty_cart_state(page: Page):
    page.goto("http://127.0.0.1:8787/catalog")

    product = page.get_by_text("Classic T-Shirt", exact=True).locator("..")
    product.get_by_role("button", name="Add").click()

    page.get_by_role("link", name="Shopping cart").click()

    page.get_by_test_id("cart-item-remove-1").click()

    expect(
        page.get_by_text("Your cart is empty", exact=True)
    ).to_be_visible()

    expect(
        page.get_by_text("Add some products to get started.", exact=True)
    ).to_be_visible()

# 验证Checkout页面上的核心元素是否正确展示
def test_checkout_page_elements(page: Page):
    # 1. 登录
    page.goto("http://127.0.0.1:8787/login")

    page.get_by_placeholder("Enter your username").fill("standard_user")
    page.get_by_placeholder("Enter your password").fill("standard123")
    page.get_by_test_id("login-submit-button").click()

    # 等待登录完成
    page.wait_for_timeout(2000)

    # 2. 进入商品目录
    page.goto("http://127.0.0.1:8787/catalog")

    # 3. 加入 Classic T-Shirt
    product = page.get_by_text("Classic T-Shirt", exact=True).locator("..")
    product.get_by_role("button", name="Add").click()

    # 4. 进入购物车
    page.get_by_role("link", name="Shopping cart").click()

    # 等待购物车加载完成
    expect(page.get_by_text("Loading...", exact=True)).not_to_be_visible()

    # 5. 从购物车进入 Checkout
    page.get_by_test_id("proceed-to-checkout-button").click()

    # 6. 验证已经进入 Checkout
    expect(page.get_by_text("Checkout", exact=True)).to_be_visible()

    # 7. 验证收货信息
    expect(page.get_by_text("First Name", exact=True)).to_be_visible()
    expect(page.get_by_text("Last Name", exact=True)).to_be_visible()
    expect(page.get_by_text("Shipping Address", exact=True)).to_be_visible()

    # 8. 验证支付信息
    expect(page.get_by_text("Card Number", exact=True)).to_be_visible()
    expect(page.get_by_text("Expiry Date", exact=True)).to_be_visible()
    expect(page.get_by_text("CVV", exact=True)).to_be_visible()
    expect(page.get_by_text("Name on Card", exact=True)).to_be_visible()

    # 9. 验证订单商品
    expect(page.get_by_text("Classic T-Shirt", exact=True)).to_be_visible()

    # 验证下单按钮
    expect(page.get_by_test_id("place-order-button")).to_be_visible()

# 填写信息
def test_place_order_success(page: Page):
    # 1. 登录
    page.goto("http://127.0.0.1:8787/login")

    page.get_by_placeholder("Enter your username").fill("standard_user")
    page.get_by_placeholder("Enter your password").fill("standard123")
    page.get_by_test_id("login-submit-button").click()

    page.wait_for_timeout(2000)

    # 2. 进入商品目录并加入商品
    page.goto("http://127.0.0.1:8787/catalog")

    product = page.get_by_text("Classic T-Shirt", exact=True).locator("..")
    product.get_by_role("button", name="Add").click()

    # 3. 进入 Checkout
    page.get_by_role("link", name="Shopping cart").click()
    expect(page.get_by_text("Loading...", exact=True)).not_to_be_visible()
    page.get_by_test_id("proceed-to-checkout-button").click()

    # 4. 填写收货信息
    page.get_by_label("First Name").fill("Test")
    page.get_by_label("Last Name").fill("User")
    page.get_by_label("Shipping Address").fill("123 Test Street")

    # 5. 填写支付信息
    page.get_by_label("Card Number").fill("4242424242424242")
    page.get_by_label("Expiry Date").fill("12/30")
    page.get_by_label("CVV").fill("123")
    page.get_by_label("Name on Card").fill("Test User")

    # 6. 验证下单按钮
    place_order_button = page.get_by_test_id("place-order-button")
    expect(place_order_button).to_be_visible()
    expect(place_order_button).to_be_enabled()

    # 7. 提交订单
    place_order_button.click()

    # 8. 等待下单完成
    page.wait_for_timeout(2000)

    print("下单后 URL:", page.url)
    print("下单后页面内容:")
    print(page.locator("body").inner_text())

# 信息有空不能下单
def test_place_order_required_field_empty(page: Page):
    # 1. 登录
    page.goto("http://127.0.0.1:8787/login")

    page.get_by_placeholder("Enter your username").fill("standard_user")
    page.get_by_placeholder("Enter your password").fill("standard123")
    page.get_by_test_id("login-submit-button").click()

    page.wait_for_timeout(2000)

    # 2. 加入商品
    page.goto("http://127.0.0.1:8787/catalog")

    product = page.get_by_text("Classic T-Shirt", exact=True).locator("..")
    product.get_by_role("button", name="Add").click()

    # 3. 进入 Checkout
    page.get_by_role("link", name="Shopping cart").click()
    expect(page.get_by_text("Loading...", exact=True)).not_to_be_visible()
    page.get_by_test_id("proceed-to-checkout-button").click()

    # 4. 填写其他信息，First Name 故意留空
    page.get_by_label("Last Name").fill("User")
    page.get_by_label("Shipping Address").fill("123 Test Street")

    page.get_by_label("Card Number").fill("4242424242424242")
    page.get_by_label("Expiry Date").fill("12/30")
    page.get_by_label("CVV").fill("123")
    page.get_by_label("Name on Card").fill("Test User")

    # 5. First Name 应该仍然为空
    expect(page.get_by_label("First Name")).to_have_value("")

    # 6. 点击下单
    page.get_by_test_id("place-order-button").click()

    # 7. 验证仍然停留在 Checkout 页面
    expect(page).to_have_url("http://127.0.0.1:8787/checkout")