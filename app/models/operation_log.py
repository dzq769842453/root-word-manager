from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
import enum
from app.database import Base

# 操作类型枚举
class OperationType(str, enum.Enum):
    CREATE = "create"  # 创建词根
    AUDIT = "audit"  # 审核词根
    DISCARD = "discard"  # 废弃词根
    DELETE = "delete"  # 删除词根
    DDL_CHECK = "ddl_check"  # DDL校验
    RECOVER = "recover"  # 恢复词根
    UPDATE = "update"  # 编辑词根

# 操作日志表模型
class RootWordOperationLog(Base):
    __tablename__ = "root_word_operation_log"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    word_id = Column(Integer, ForeignKey("root_word.id"), nullable=False, comment="词根 ID")
    operation_type = Column(SQLEnum(OperationType), nullable=False, comment="操作类型")
    operation_user = Column(String(32), nullable=False, comment="操作人账号")
    operation_time = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), comment="操作时间")
    operation_content = Column(String(512), nullable=False, comment="操作内容（如 '审核通过'）")
