import uuid
from test_data.auth_data import STANDARD_USER, ADMIN_USER
import pytest
import requests

BASE_URL = "http://127.0.0.1:8787"


# 每个测试函数生成一个新的 Session ID
@pytest.fixture
def session_id():
    return str(uuid.uuid4())


# 未登录的 API Session
@pytest.fixture
def api_session(session_id):
    session = requests.Session()
    session.headers.update({
        "X-Session-ID": session_id,
    })
    return session


# 已登录的 API Session
@pytest.fixture
def auth_session(session_id):
    session = requests.Session()
    session.headers.update({
        "X-Session-ID": session_id,
    })

    response = session.post(
        f"{BASE_URL}/api/auth/login",
        json=STANDARD_USER
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert "data" in data

    access_token = data["data"]["accessToken"]

    session.headers.update({
        "Authorization": f"Bearer {access_token}",
    })

    return session


@pytest.fixture
def admin_session(session_id):
    session = requests.Session()
    session.headers.update({
        "X-Session-ID": session_id,
    })

    response = session.post(
        f"{BASE_URL}/api/auth/login",
        json=ADMIN_USER,
    )

    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True

    access_token = data["data"]["accessToken"]

    session.headers.update({
        "Authorization": f"Bearer {access_token}",
    })

    return session