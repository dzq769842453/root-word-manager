from app.database import SessionLocal
from app.models.root_word import RootWord

# 连接数据库并检查注释数据
with SessionLocal() as db:
    try:
        # 查询前10条词根数据，检查remark字段
        root_words = db.query(RootWord).limit(10).all()
        print("前10条词根数据:")
        for word in root_words:
            print(f'ID: {word.id}, 名称: {word.word_name}, 注释: "{word.remark}"')
        
        # 统计有注释的词根数量
        words_with_remark = db.query(RootWord).filter(RootWord.remark.isnot(None), RootWord.remark != '').count()
        total_words = db.query(RootWord).count()
        print(f'\n总词根数: {total_words}')
        print(f'有注释的词根数: {words_with_remark}')
        print(f'无注释的词根数: {total_words - words_with_remark}')
        
    except Exception as e:
        print(f'检查失败: {e}')
