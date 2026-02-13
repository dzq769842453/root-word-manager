from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum as SQLEnum
from sqlalchemy.sql import func
import enum
from app.database import Base

# 词根状态枚举
class RootWordStatus(str, enum.Enum):
    PENDING_AUDIT = "pending_audit"  # 待审核
    EFFECTIVE = "effective"  # 已生效
    DISCARDED = "discarded"  # 已废弃

# 词根主表模型
class RootWord(Base):
    __tablename__ = "root_word"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    word_name = Column(String(64), nullable=False, unique=True, comment="词根名称")
    mysql_type = Column(String(64), nullable=False, comment="MySQL 数据类型")
    doris_type = Column(String(64), nullable=False, comment="Doris 数据类型")
    clickhouse_type = Column(String(64), nullable=False, comment="ClickHouse 数据类型")
    remark = Column(String(256), nullable=True, comment="词根注释")
    status = Column(SQLEnum(RootWordStatus), nullable=False, default=RootWordStatus.PENDING_AUDIT, comment="词根状态")
    apply_user = Column(String(32), nullable=False, comment="申请人账号")
    apply_time = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), comment="申请时间")
    audit_user = Column(String(32), nullable=True, comment="审核人账号")
    audit_time = Column(DateTime(timezone=True), nullable=True, comment="审核时间")
    audit_remark = Column(String(256), nullable=True, comment="审核备注（驳回原因）")
    delete_flag = Column(Integer, nullable=False, default=0, comment="删除标记：0-未删除，1-已删除")
    create_time = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), comment="创建时间")
    update_time = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间")
