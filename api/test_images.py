import requests


BASE_URL = "http://127.0.0.1:8787"


def test_get_existing_image():
    image_key = "products/1787824839603-047125c5.jpg"

    response = requests.get(
        f"{BASE_URL}/api/images/{image_key}"
    )

    assert response.status_code == 200
    assert response.headers["Content-Type"] == "image/jpeg"
    assert len(response.content) > 0

def test_get_nonexistent_image():
    image_key = "products/not-exist.jpg"

    response = requests.get(
        f"{BASE_URL}/api/images/{image_key}"
    )

    assert response.status_code == 404

# 测试上传图片
def test_admin_upload_valid_image(admin_session):
    image_path = "test_image.jpg"

    with open(image_path, "rb") as image_file:
        response = admin_session.post(
            f"{BASE_URL}/api/images",
            files={
                "file": (
                    "test_image.jpg",
                    image_file,
                    "image/jpeg",
                )
            },
        )

    assert response.status_code == 201

    data = response.json()

    assert data["success"] is True
    assert data["data"]["size"] > 0
    assert data["data"]["type"] == "image/jpeg"
    assert data["data"]["key"].startswith("products/")

# 验证上传图片可以被正常读取
def test_get_uploaded_image(admin_session):
    image_path = "test_image.jpg"

    with open(image_path, "rb") as image_file:
        upload_response = admin_session.post(
            f"{BASE_URL}/api/images",
            files={
                "file": (
                    "test_image.jpg",
                    image_file,
                    "image/jpeg",
                )
            },
        )

    assert upload_response.status_code == 201

    upload_data = upload_response.json()
    image_key = upload_data["data"]["key"]

    get_response = requests.get(
        f"{BASE_URL}/api/images/{image_key}"
    )

    assert get_response.status_code == 200
    assert get_response.headers["Content-Type"] == "image/jpeg"
    assert len(get_response.content) > 0

# 上传非法文件
def test_upload_invalid_file_type(admin_session):
    response = admin_session.post(
        f"{BASE_URL}/api/images",
        files={
            "file": (
                "test.txt",
                b"this is not an image",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400

# 未登录不可上传
def test_unauthenticated_user_cannot_upload_image(api_session):
    response = api_session.post(
        f"{BASE_URL}/api/images",
        files={
            "file": (
                "test.jpg",
                b"fake image data",
                "image/jpeg",
            )
        },
    )

    assert response.status_code == 401

# 普通用户登录：403
def test_standard_user_cannot_upload_image(auth_session):
    response = auth_session.post(
        f"{BASE_URL}/api/images",
        files={
            "file": (
                "test.jpg",
                b"fake image data",
                "image/jpeg",
            )
        },
    )

    assert response.status_code == 401

# 文件大小边界测试
def test_upload_image_at_size_limit(admin_session):
    image_data = b"x" * (5 * 1024 * 1024)

    response = admin_session.post(
        f"{BASE_URL}/api/images",
        files={
            "file": (
                "test.jpg",
                image_data,
                "image/jpeg",
            )
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["success"] is True
    assert data["data"]["size"] == 5 * 1024 * 1024
    assert data["data"]["type"] == "image/jpeg"

def test_upload_image_over_size_limit(admin_session):
    image_data = b"x" * (5 * 1024 * 1024 + 1)

    response = admin_session.post(
        f"{BASE_URL}/api/images",
        files={
            "file": (
                "test.jpg",
                image_data,
                "image/jpeg",
            )
        },
    )

    assert response.status_code == 400

# 删除图片
def test_admin_delete_image(admin_session):
    image_path = "test_image.jpg"

    # 先上传测试图片
    with open(image_path, "rb") as image_file:
        upload_response = admin_session.post(
            f"{BASE_URL}/api/images",
            files={
                "file": (
                    "test_image.jpg",
                    image_file,
                    "image/jpeg",
                )
            },
        )

    assert upload_response.status_code == 201

    image_key = upload_response.json()["data"]["key"]

    # 删除图片
    delete_response = admin_session.delete(
        f"{BASE_URL}/api/images/{image_key}"
    )

    assert delete_response.status_code == 200

    data = delete_response.json()

    assert data["success"] is True
    assert data["data"]["key"] == image_key
    assert data["data"]["deleted"] is True

def test_get_image_after_delete(admin_session):
    image_path = "test_image.jpg"

    # 上传测试图片
    with open(image_path, "rb") as image_file:
        upload_response = admin_session.post(
            f"{BASE_URL}/api/images",
            files={
                "file": (
                    "test_image.jpg",
                    image_file,
                    "image/jpeg",
                )
            },
        )

    assert upload_response.status_code == 201

    image_key = upload_response.json()["data"]["key"]

    # 删除图片
    delete_response = admin_session.delete(
        f"{BASE_URL}/api/images/{image_key}"
    )

    assert delete_response.status_code == 200

    # 删除后再次获取
    get_response = requests.get(
        f"{BASE_URL}/api/images/{image_key}"
    )

    assert get_response.status_code == 404

def test_standard_user_cannot_delete_image(
    admin_session,
    auth_session,
):
    image_path = "test_image.jpg"
    print("Admin Authorization:", admin_session.headers.get("Authorization", "")[:30])
    print("User Authorization:", auth_session.headers.get("Authorization", "")[:30])

    # 管理员先上传一张测试图片
    with open(image_path, "rb") as image_file:
        upload_response = admin_session.post(
            f"{BASE_URL}/api/images",
            files={
                "file": (
                    "test_image.jpg",
                    image_file,
                    "image/jpeg",
                )
            },
        )
    print(upload_response.status_code)
    print(upload_response.text)
    assert upload_response.status_code == 201

    image_key = upload_response.json()["data"]["key"]

    # 普通用户尝试删除
    delete_response = auth_session.delete(
        f"{BASE_URL}/api/images/{image_key}"
    )

    assert delete_response.status_code == 403
def test_unauthenticated_user_cannot_delete_image(
    admin_session,
    api_session,
):
    image_path = "test_image.jpg"

    # 管理员先上传测试图片
    with open(image_path, "rb") as image_file:
        upload_response = admin_session.post(
            f"{BASE_URL}/api/images",
            files={
                "file": (
                    "test_image.jpg",
                    image_file,
                    "image/jpeg",
                )
            },
        )

    assert upload_response.status_code == 201

    image_key = upload_response.json()["data"]["key"]

    # 未登录用户尝试删除
    delete_response = api_session.delete(
        f"{BASE_URL}/api/images/{image_key}"
    )

    assert delete_response.status_code == 401