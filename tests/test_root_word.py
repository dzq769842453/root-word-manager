def test_apply_root_word(user_token, client):
    """测试申请创建词根"""
    response = client.post(
        "/api/root-word/apply",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "word_name": "test_id",
            "mysql_type": "bigint",
            "doris_type": "bigint",
            "clickhouse_type": "UInt64"
        }
    )
    assert response.status_code == 200
    assert response.json()["code"] == 200
    assert "word_id" in response.json()["data"]

def test_apply_duplicate_root_word(user_token, client):
    """测试申请创建重复词根"""
    # 先创建一个词根
    client.post(
        "/api/root-word/apply",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "word_name": "duplicate_id",
            "mysql_type": "bigint",
            "doris_type": "bigint",
            "clickhouse_type": "UInt64"
        }
    )
    
    # 再次创建同名词根
    response = client.post(
        "/api/root-word/apply",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "word_name": "duplicate_id",
            "mysql_type": "bigint",
            "doris_type": "bigint",
            "clickhouse_type": "UInt64"
        }
    )
    assert response.status_code == 400

def test_list_root_word(user_token, client):
    """测试查询词根列表"""
    response = client.post(
        "/api/root-word/list",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "page_num": 1,
            "page_size": 10
        }
    )
    assert response.status_code == 200
    assert response.json()["code"] == 200
    assert "list" in response.json()["data"]
    assert "total" in response.json()["data"]

def test_audit_root_word(admin_token, client, user_token):
    """测试审核词根"""
    # 先创建一个词根
    create_response = client.post(
        "/api/root-word/apply",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "word_name": "audit_id",
            "mysql_type": "bigint",
            "doris_type": "bigint",
            "clickhouse_type": "UInt64"
        }
    )
    word_id = create_response.json()["data"]["word_id"]
    
    # 审核通过
    audit_response = client.post(
        "/api/root-word/audit",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "word_id": word_id,
            "audit_result": 1,
            "audit_remark": "审核通过"
        }
    )
    assert audit_response.status_code == 200
    assert audit_response.json()["code"] == 200

def test_check_ddl_root_word(user_token, client):
    """测试 DDL 词根校验"""
    response = client.post(
        "/api/root-word/ddl/check",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "ddl_content": "CREATE TABLE test (test_id bigint, test_name varchar(32))"
        }
    )
    assert response.status_code == 200
    assert "compliant_fields" in response.json()["data"]
    assert "non_compliant_fields" in response.json()["data"]

def test_replace_ddl_root_word(user_token, client):
    """测试 DDL 词根替换"""
    response = client.post(
        "/api/root-word/ddl/replace",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "ddl_content": "CREATE TABLE test (test_id int, test_name string)"
        }
    )
    assert response.status_code == 200
    assert "replaced_ddl" in response.json()["data"]
