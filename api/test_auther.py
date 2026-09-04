import requests
import pytest
from test_data.auth_data import INVALID_LOGIN_DATA

BASE_URL = "http://127.0.0.1:8787"


def test_login_success():
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={
            "username": "standard_user",
            "password": "standard123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert "data" in data

    auth_data = data["data"]

    assert "accessToken" in auth_data
    assert auth_data["accessToken"]

# 错误密码
def test_login_wrong_password():
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={
            "username": "standard_user",
            "password": "wrong_password",
        },
    )

    assert response.status_code == 401

    data = response.json()

    assert data["success"] is False
    assert "error" in data

# 不存在用户
def test_login_nonexistent_user():
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={
            "username": "nonexistent_user",
            "password": "123456",
        },
    )

    assert response.status_code == 401

    data = response.json()

    assert data["success"] is False
    assert "error" in data

# 不存在的用户和密码
@pytest.mark.parametrize("login_data", INVALID_LOGIN_DATA)
def test_login_invalid_parameters(login_data):
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json=login_data,
    )

    assert response.status_code == 400

    data = response.json()
    assert data["success"] is False

# 能否识别token
def test_get_current_user(auth_session):
    response = auth_session.get(
        f"{BASE_URL}/api/auth/me"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["data"]["username"] == "standard_user"

# 未登录访问
def test_get_current_user_without_login(api_session):
    response = api_session.get(
        f"{BASE_URL}/api/auth/me"
    )

    assert response.status_code == 401

    data = response.json()

    assert data["success"] is False
    assert "error" in data

# 登出
def test_logout(auth_session):
    response = auth_session.post(
        f"{BASE_URL}/api/auth/logout"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["data"]["message"] == "Logged out successfully"

# 登出后token失效
def test_refresh_token_invalid_after_logout(auth_session):
    # 先确认当前 Session 已经拥有 refresh token
    assert "refresh_token" in auth_session.cookies

    # 登出
    logout_response = auth_session.post(
        f"{BASE_URL}/api/auth/logout"
    )

    assert logout_response.status_code == 200

    # 登出后尝试刷新Token
    refresh_response = auth_session.post(
        f"{BASE_URL}/api/auth/refresh"
    )

    assert refresh_response.status_code == 401

    data = refresh_response.json()

    assert data["success"] is False
    assert "error" in data

# 测试 Refresh Token 正常刷新
'''
    缺陷/环境问题：
    QADemo本地HTTP环境下, refresh_token Cookie设置了Secure属性,
    导致requests无法在HTTP请求中携带 Cookie,
    从而/api/auth/refresh 始终返回401。
'''
def test_refresh_token_success(auth_session):
    # 登录后获取 refresh token
    assert "refresh_token" in auth_session.cookies

    # 本地测试环境使用 HTTP，因此临时关闭 Secure 属性
    auth_session.cookies.set(
        "refresh_token",
        auth_session.cookies["refresh_token"],
        domain="127.0.0.1",
        path="/",
        secure=False,
    )

    response = auth_session.post(
        f"{BASE_URL}/api/auth/refresh"
    )

    print("request cookies:", response.request.headers.get("Cookie"))
    print("status:", response.status_code)
    print("response:", response.text)

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "accessToken" in data["data"]
    assert data["data"]["accessToken"]

def test_refresh_without_token(api_session):
    response = api_session.post(
        f"{BASE_URL}/api/auth/refresh"
    )

    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False
    assert "error" in data

# 非法token
def test_refresh_with_invalid_token(api_session):
    # 手动设置一个伪造的 refresh token
    api_session.cookies.set(
        "refresh_token",
        "invalid-refresh-token",
        domain="127.0.0.1",
        path="/",
        secure=False,
    )

    response = api_session.post(
        f"{BASE_URL}/api/auth/refresh"
    )

    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False
    assert "error" in data