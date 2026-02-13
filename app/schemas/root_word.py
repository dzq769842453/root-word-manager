from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum

# 词根状态枚举
class RootWordStatus(str, Enum):
    PENDING_AUDIT = "pending_audit"  # 待审核
    EFFECTIVE = "effective"  # 已生效
    DISCARDED = "discarded"  # 已废弃

# 创建词根请求模型
class RootWordCreate(BaseModel):
    word_name: str = Field(..., description="词根名称", min_length=1, max_length=64)
    mysql_type: str = Field(..., description="MySQL 数据类型", min_length=1, max_length=64)
    doris_type: str = Field(..., description="Doris 数据类型", min_length=1, max_length=64)
    clickhouse_type: str = Field(..., description="ClickHouse 数据类型", min_length=1, max_length=64)
    remark: Optional[str] = Field(None, description="词根注释", max_length=256)

# 词根响应模型
class RootWordResponse(BaseModel):
    id: int
    word_name: str
    mysql_type: str
    doris_type: str
    clickhouse_type: str
    remark: Optional[str] = None
    status: RootWordStatus
    apply_user: str
    apply_time: datetime
    audit_user: Optional[str] = None
    audit_time: Optional[datetime] = None
    audit_remark: Optional[str] = None
    delete_flag: int
    create_time: datetime
    update_time: datetime
    
    class Config:
        from_attributes = True

# 审核词根请求模型
class RootWordAudit(BaseModel):
    word_id: int = Field(..., description="词根 ID")
    audit_result: int = Field(..., description="审核结果：1-通过，2-驳回")
    audit_remark: Optional[str] = Field(None, description="审核备注（驳回原因）", max_length=256)

# DDL 校验请求模型
class DDLCheckRequest(BaseModel):
    ddl_content: str = Field(..., description="待校验 DDL")

# DDL 校验响应模型
class DDLCheckResponse(BaseModel):
    code: int
    msg: str
    data: dict

# 词根列表查询请求模型
class RootWordListRequest(BaseModel):
    page_num: int = Field(1, description="页码", ge=1)
    page_size: int = Field(10, description="每页大小", ge=1, le=100)
    word_name: Optional[str] = Field(None, description="词根名称模糊查询")
    status: Optional[str] = Field(None, description="状态筛选")
    apply_user: Optional[str] = Field(None, description="申请人筛选")

# 编辑词根请求模型（管理员）
class RootWordUpdate(BaseModel):
    word_id: int = Field(..., description="词根 ID")
    word_name: Optional[str] = Field(None, description="词根名称", min_length=1, max_length=64)
    mysql_type: Optional[str] = Field(None, description="MySQL 数据类型", min_length=1, max_length=32)
    doris_type: Optional[str] = Field(None, description="Doris 数据类型", min_length=1, max_length=32)
    clickhouse_type: Optional[str] = Field(None, description="ClickHouse 数据类型", min_length=1, max_length=32)
    remark: Optional[str] = Field(None, description="词根注释", max_length=256)
