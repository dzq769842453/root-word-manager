from app.database import SessionLocal
from app.models.root_word import RootWord
from app.models.user import User
from app.models.operation_log import RootWordOperationLog

# 连接数据库并检查数据
with SessionLocal() as db:
    try:
        # 检查用户表
        user_count = db.query(User).count()
        print(f'用户表数量: {user_count}')
        
        # 检查词根表
        root_word_count = db.query(RootWord).count()
        print(f'词根表数量: {root_word_count}')
        
        # 检查操作日志表
        log_count = db.query(RootWordOperationLog).count()
        print(f'操作日志表数量: {log_count}')
        
        # 打印前5条词根
        print('\n前5条词根:')
        for word in db.query(RootWord).limit(5).all():
            print(f'ID: {word.id}, 名称: {word.word_name}, 状态: {word.status}')
            
        print('\n数据库检查完成！')
    except Exception as e:
        print(f'检查失败: {e}')
