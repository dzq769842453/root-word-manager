def test_login_success(client):
    """测试登录成功"""
    response = client.post("/api/auth/login", data={
        "username": "admin",
        "password": "admin123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "user" in response.json()

def test_login_failure(client):
    """测试登录失败（用户名或密码错误）"""
    response = client.post("/api/auth/login", data={
        "username": "admin",
        "password": "wrong_password"
    })
    assert response.status_code == 401

def test_login_missing_params(client):
    """测试登录失败（缺少参数）"""
    response = client.post("/api/auth/login", data={
        "username": "admin"
    })
    assert response.status_code == 422
