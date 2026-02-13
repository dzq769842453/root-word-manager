from sqlalchemy import text
from app.database import get_db
from app.models.root_word import RootWord, RootWordStatus
from app.models.operation_log import RootWordOperationLog
from datetime import datetime

# 重置词根表自增ID并重新初始化数据
def reset_root_word_id():
    db = next(get_db())
    try:
        # 先删除操作日志记录（外键约束）
        db.query(RootWordOperationLog).delete()
        db.commit()
        
        # 删除所有词根记录
        db.query(RootWord).delete()
        db.commit()
        
        # 重置自增ID
        db.execute(text('ALTER TABLE root_word AUTO_INCREMENT = 1'))
        db.execute(text('ALTER TABLE root_word_operation_log AUTO_INCREMENT = 1'))
        db.commit()
        
        # 重新初始化词根数据
        root_words_data = [
            {"word_name": "user", "mysql_type": "varchar(50)", "doris_type": "varchar(50)", "clickhouse_type": "String", "remark": "用户相关"},
            {"word_name": "id", "mysql_type": "bigint", "doris_type": "bigint", "clickhouse_type": "UInt64", "remark": "主键ID"},
            {"word_name": "name", "mysql_type": "varchar(100)", "doris_type": "varchar(100)", "clickhouse_type": "String", "remark": "名称"},
            {"word_name": "age", "mysql_type": "int", "doris_type": "int", "clickhouse_type": "Int32", "remark": "年龄"},
            {"word_name": "email", "mysql_type": "varchar(255)", "doris_type": "varchar(255)", "clickhouse_type": "String", "remark": "邮箱"},
            {"word_name": "phone", "mysql_type": "varchar(20)", "doris_type": "varchar(20)", "clickhouse_type": "String", "remark": "电话"},
            {"word_name": "address", "mysql_type": "varchar(255)", "doris_type": "varchar(255)", "clickhouse_type": "String", "remark": "地址"},
            {"word_name": "create", "mysql_type": "datetime", "doris_type": "datetime", "clickhouse_type": "DateTime", "remark": "创建时间"},
            {"word_name": "update", "mysql_type": "datetime", "doris_type": "datetime", "clickhouse_type": "DateTime", "remark": "更新时间"},
            {"word_name": "delete", "mysql_type": "tinyint", "doris_type": "tinyint", "clickhouse_type": "Int8", "remark": "删除标记"},
            {"word_name": "status", "mysql_type": "tinyint", "doris_type": "tinyint", "clickhouse_type": "Int8", "remark": "状态"},
            {"word_name": "type", "mysql_type": "tinyint", "doris_type": "tinyint", "clickhouse_type": "Int8", "remark": "类型"},
            {"word_name": "count", "mysql_type": "int", "doris_type": "int", "clickhouse_type": "Int32", "remark": "数量"},
            {"word_name": "amount", "mysql_type": "decimal(10,2)", "doris_type": "decimal(10,2)", "clickhouse_type": "Decimal(10,2)", "remark": "金额"},
            {"word_name": "price", "mysql_type": "decimal(10,2)", "doris_type": "decimal(10,2)", "clickhouse_type": "Decimal(10,2)", "remark": "价格"}
        ]
        
        for word_data in root_words_data:
            new_word = RootWord(
                word_name=word_data["word_name"],
                mysql_type=word_data["mysql_type"],
                doris_type=word_data["doris_type"],
                clickhouse_type=word_data["clickhouse_type"],
                remark=word_data["remark"],
                status=RootWordStatus.EFFECTIVE,
                apply_user="admin",
                apply_time=datetime.utcnow(),
                audit_user="admin",
                audit_time=datetime.utcnow(),
                audit_remark="初始化词根",
                delete_flag=0
            )
            db.add(new_word)
        
        db.commit()
        print("词根表ID重置成功，数据已重新初始化！")
    except Exception as e:
        print(f"错误：{e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    reset_root_word_id()
