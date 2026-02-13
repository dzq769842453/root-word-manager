#!/usr/bin/env python3
"""
更新数据库表结构
"""
import pymysql

# 数据库连接配置
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'database': 'root_word_manager'
}

def update_table():
    try:
        # 连接数据库
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 修改字段长度
        alter_sql = """
        ALTER TABLE root_word 
        MODIFY COLUMN mysql_type VARCHAR(64) NOT NULL COMMENT 'MySQL 数据类型',
        MODIFY COLUMN doris_type VARCHAR(64) NOT NULL COMMENT 'Doris 数据类型',
        MODIFY COLUMN clickhouse_type VARCHAR(64) NOT NULL COMMENT 'ClickHouse 数据类型';
        """
        
        cursor.execute(alter_sql)
        conn.commit()
        
        print("✅ 数据库表结构更新成功！")
        print("- mysql_type: VARCHAR(32) -> VARCHAR(64)")
        print("- doris_type: VARCHAR(32) -> VARCHAR(64)")
        print("- clickhouse_type: VARCHAR(32) -> VARCHAR(64)")
        
    except Exception as e:
        print(f"❌ 更新失败: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    update_table()
