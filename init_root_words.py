import csv
import re
from app.database import engine, SessionLocal
from app.models.root_word import RootWord, RootWordStatus
from app.models.operation_log import RootWordOperationLog, OperationType
from datetime import datetime

# 词根列表
root_words_data = [
    {"word_name": "book_id", "description": "图书ID"},
    {"word_name": "channel_id", "description": "渠道ID"},
    {"word_name": "adviser_id", "description": "编辑ID"},
    {"word_name": "qrcode_id", "description": "二维码ID"},
    {"word_name": "app_id", "description": "应用ID"},
    {"word_name": "product_id", "description": "作品ID"},
    {"word_name": "official_id", "description": "公众号ID"},
    {"word_name": "official_name", "description": "公众号名称"},
    {"word_name": "book_name", "description": "书刊名称"},
    {"word_name": "qrcode_name", "description": "二维码名称"},
    {"word_name": "app_name", "description": "APP名称"},
    {"word_name": "product_name", "description": "产品名称"},
    {"word_name": "update_time", "description": "数据更新时间"},
    {"word_name": "scan_amount", "description": "扫码量"},
    {"word_name": "share_amount", "description": "分享数量"},
    {"word_name": "online_seconds", "description": "在线时长（秒）"},
    {"word_name": "track_now", "description": "当前节点"},
    {"word_name": "track_index", "description": "当前节点位置"},
    {"word_name": "track_before", "description": "前一节点"},
    {"word_name": "track_after", "description": "后一节点"},
    {"word_name": "spread_type", "description": "传播类型"},
    {"word_name": "user_flow_amount", "description": "节点流向数据量"},
    {"word_name": "user_knot_amount", "description": "节点数据量"},
    {"word_name": "insert_time", "description": "插入时间"},
    {"word_name": "book_group_id", "description": ""},
    {"word_name": "part_id", "description": "分表的后缀,没有实际意义"},
    {"word_name": "battery_level", "description": "电量"},
    {"word_name": "agent_id", "description": "出版社id"},
    {"word_name": "type_id", "description": "类型id"},
    {"word_name": "type_code", "description": "类型编码"},
    {"word_name": "browse_time", "description": "浏览时长"},
    {"word_name": "browse_amount", "description": "阅读次数/浏览量"},
    {"word_name": "readers_amount", "description": "读者数"},
    {"word_name": "create_time", "description": "创建时间"},
    {"word_name": "cvr", "description": "转化率"},
    {"word_name": "users_amount", "description": "浏览、扫码、评论人数"},
    {"word_name": "amount", "description": "除订单以外的次数、数量"},
    {"word_name": "volume", "description": "交易/订单金额"},
    {"word_name": "price", "description": "销售码洋（定价*销售册数）"},
    {"word_name": "quantity", "description": "交易/订单数量"},
    {"word_name": "online", "description": "时长"},
    {"word_name": "statis_type", "description": "统计类型"},
    {"word_name": "persales_volume", "description": "客单价"},
    {"word_name": "rate", "description": "占比、占有率"},
    {"word_name": "create_***", "description": "统计周期"},
    {"word_name": "create_date", "description": "创建日期/查询日期"},
    {"word_name": "server_type", "description": "服务类型"},
    {"word_name": "pro_lab_id", "description": "专业ID"},
    {"word_name": "part_id", "description": "分表的后缀,没有实际意义"},
    {"word_name": "dep_lab_id", "description": "深度ID"},
    {"word_name": "pur_lab_id", "description": "目的ID"},
    {"word_name": "time", "description": "时间"},
    {"word_name": "resource_type", "description": "资源类型"},
    {"word_name": "resource_id", "description": "资源id"},
    {"word_name": "source_type", "description": "数据来源"},
    {"word_name": "msg_id", "description": "消息id"},
    {"word_name": "user_type", "description": "用户类型"},
    {"word_name": "msg_content", "description": "信息原文内容"},
    {"word_name": "resp_content", "description": "信息响应内容"},
    {"word_name": "pers_type", "description": "响应人设"},
    {"word_name": "msg_type", "description": "信息类型"},
    {"word_name": "emo_type", "description": "情感标签"},
    {"word_name": "emo_val", "description": "情绪标签"},
    {"word_name": "emo_level", "description": "情绪程度"},
    {"word_name": "orc_content", "description": "图片文字识别"},
    {"word_name": "voice_content", "description": "语音识别识别"},
    {"word_name": "ai_services", "description": "提供ai服务类型"},
    {"word_name": "msg_time", "description": "发文时间"},
    {"word_name": "resp_time", "description": "响应时间"},
    {"word_name": "agent_income", "description": "出版社收益"},
    {"word_name": "adviser_income", "description": "编辑收益"},
    {"word_name": "adders_amount", "description": "新增用户数量"},
    {"word_name": "time_period", "description": "时间段"},
    {"word_name": "quest_content", "description": "问题内容"},
    {"word_name": "msgers_amount", "description": "会话人数"},
    {"word_name": "msg_amount", "description": "会话次数"},
    {"word_name": "message_amount", "description": "消息量"},
    {"word_name": "sales_range", "description": "销量区间"},
    {"word_name": "one_category_id", "description": "图书一级分类"},
    {"word_name": "two_category_id", "description": "图书二级分类"},
    {"word_name": "three_category_id", "description": "图书三级分类"},
    {"word_name": "feedback_rate", "description": "反馈率"},
    {"word_name": "feedbackers_amount", "description": "问题反馈人数"},
    {"word_name": "scaners_amount_today", "description": "今日扫码人数"},
    {"word_name": "scaners_amount_yesterday", "description": "昨日扫码人数"},
    {"word_name": "scaners_amount_total", "description": "累计扫码人数"},
    {"word_name": "readers_amount_today", "description": "今日访问人数"},
    {"word_name": "readers_amount_yesterday", "description": "昨日访问人数"},
    {"word_name": "readers_amount_total", "description": "累计访问人数"},
    {"word_name": "posreview_rate_today", "description": "今日好评率"},
    {"word_name": "posreview_rate_yesterday", "description": "昨日好评率"},
    {"word_name": "posreview_rate_top", "description": "好评率,峰值"},
    {"word_name": "like_amount", "description": "点赞数量"},
    {"word_name": "stomp_amount", "description": "点踩数量"},
    {"word_name": "sales_price_cur", "description": "本期_销售码洋（本月销售码洋）"},
    {"word_name": "sales_price_lmon", "description": "环比上期_销售码洋(上月销售码洋)"},
    {"word_name": "sales_price_lyear", "description": "同比上期_销售码洋（去年本月销售码洋）"},
    {"word_name": "sales_price_year", "description": "本年销售码洋"},
    {"word_name": "sales_price_last_year", "description": "去年销售码洋"},
    {"word_name": "sales_volume_cur", "description": "本期_销售实洋（本月销售实洋）"},
    {"word_name": "sales_volume_lmon", "description": "环比上期_销售实洋(上月销售实洋)"},
    {"word_name": "sales_volume_lyear", "description": "同比上期_销售实洋（去年本月销售实洋）"},
    {"word_name": "sales_volume_year", "description": "本年销售实洋"},
    {"word_name": "sales_volume_last_year", "description": "去年销售实洋"},
    {"word_name": "topic_name", "description": "选题名称"},
    {"word_name": "behavior_type", "description": "行为类型"},
    {"word_name": "price", "description": "定价"},
    {"word_name": "sale_price", "description": "销售价格"},
    {"word_name": "user_id", "description": "用户id"},
    {"word_name": "isbn", "description": "图书isbn编号"},
    {"word_name": "cip", "description": "cip编号"},
    {"word_name": "publish_date", "description": "出版日期"},
    {"word_name": "inventory_amount", "description": "库存"},
    {"word_name": "real_inventory_amount", "description": "实际库存"},
    {"word_name": "available_inventory_amount", "description": "可用库存"},
    {"word_name": "freeze_inventory_amount", "description": "冻结库存"},
    {"word_name": "lock_inventory_amount", "description": "锁定库存"},
    {"word_name": "store_id", "description": "店铺id"},
    {"word_name": "store_name", "description": "店铺名称"},
    {"word_name": "job_id", "description": "任务id，比如AI编辑工作室里数字员工产生的任务id"},
    {"word_name": "emp_id", "description": "员工id，比如是AI编辑工作室里的AI员工id"},
    {"word_name": "customer_code", "description": "客户编码"},
    {"word_name": "sales_province", "description": "销售省份"},
    {"word_name": "depart_id", "description": "部门ID"},
    {"word_name": "return_quantity", "description": "退货数量"},
    {"word_name": "return_price", "description": "退货码洋"},
    {"word_name": "return_volume", "description": "退货实洋"},
    {"word_name": "zt_one_category", "description": "中图分类一级"},
    {"word_name": "zt_two_category", "description": "中图分类二级"},
    {"word_name": "zt_three_category", "description": "中图分类三级"}
]

# 类型映射函数
def get_type_mapping(word_name):
    # 基于词根名称推断类型
    if any(suffix in word_name for suffix in ['_id', 'id', '_code']):
        return {
            "mysql_type": "bigint",
            "doris_type": "bigint",
            "clickhouse_type": "UInt64"
        }
    elif any(suffix in word_name for suffix in ['_name', 'name', '_content', 'content', '_province', 'province', 'type']):
        return {
            "mysql_type": "varchar(255)",
            "doris_type": "varchar(255)",
            "clickhouse_type": "String"
        }
    elif any(suffix in word_name for suffix in ['_time', 'time', '_date', 'date']):
        return {
            "mysql_type": "datetime",
            "doris_type": "datetime",
            "clickhouse_type": "DateTime"
        }
    elif any(suffix in word_name for suffix in ['_amount', 'amount', '_volume', 'volume', '_price', 'price', '_quantity', 'quantity', '_seconds', 'seconds', '_level', 'level', '_index', 'index', '_rate', 'rate', '_cvr', 'cvr']):
        return {
            "mysql_type": "bigint",
            "doris_type": "bigint",
            "clickhouse_type": "UInt64"
        }
    else:
        return {
            "mysql_type": "varchar(255)",
            "doris_type": "varchar(255)",
            "clickhouse_type": "String"
        }

def init_root_words():
    db = SessionLocal()
    try:
        for word_data in root_words_data:
            word_name = word_data["word_name"].strip()
            # 跳过空的词根名称
            if not word_name or word_name == '_cvr' or word_name == '"_cvr' or word_name == '"':
                continue
            
            # 检查词根是否已存在
            existing = db.query(RootWord).filter(
                RootWord.word_name == word_name,
                RootWord.delete_flag == 0
            ).first()
            
            if not existing:
                # 获取类型映射
                type_mapping = get_type_mapping(word_name)
                
                # 创建词根
                new_word = RootWord(
                    word_name=word_name,
                    mysql_type=type_mapping["mysql_type"],
                    doris_type=type_mapping["doris_type"],
                    clickhouse_type=type_mapping["clickhouse_type"],
                    remark=word_data["description"],
                    status=RootWordStatus.EFFECTIVE,  # 直接设为已生效
                    apply_user="admin",
                    apply_time=datetime.utcnow(),
                    audit_user="admin",
                    audit_time=datetime.utcnow(),
                    audit_remark="初始化词根",
                    delete_flag=0
                )
                db.add(new_word)
                db.flush()  # 立即提交，获取 ID
                
                # 创建操作日志
                log = RootWordOperationLog(
                    word_id=new_word.id,
                    operation_type=OperationType.CREATE,
                    operation_user="admin",
                    operation_content=f"初始化词根：{word_name}"
                )
                db.add(log)
                
                print(f"初始化词根：{word_name}")
        
        db.commit()
        print("词根初始化完成！")
    except Exception as e:
        print(f"初始化过程中出错：{e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_root_words()
