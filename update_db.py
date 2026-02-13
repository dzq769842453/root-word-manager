from app.database import engine
from sqlalchemy import text

# 连接数据库并执行 ALTER TABLE 语句
with engine.connect() as conn:
    try:
        # 添加 remark 字段
        conn.execute(text('ALTER TABLE root_word ADD COLUMN remark VARCHAR(256) COMMENT \'词根注释\' AFTER clickhouse_type;'))
        conn.commit()
        print('数据库表结构更新成功！')
    except Exception as e:
        print(f'更新失败: {e}')
        conn.rollback()
