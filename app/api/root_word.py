from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
from typing import List, Optional
from functools import lru_cache
from app.database import get_db
from app.security import get_current_user, check_admin_permission
from app.models.root_word import RootWord, RootWordStatus
from app.models.operation_log import RootWordOperationLog, OperationType
from app.schemas.root_word import (
    RootWordCreate, RootWordResponse, RootWordAudit, RootWordUpdate,
    DDLCheckRequest, DDLCheckResponse, RootWordListRequest
)
import sqlparse
import re

router = APIRouter()

# 缓存：获取所有词根（用于DDL校验）
@lru_cache(maxsize=1)
def get_all_root_words_cached():
    """缓存所有词根，5分钟过期"""
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        root_words = db.query(RootWord).filter(
            and_(
                RootWord.delete_flag == 0,
                RootWord.status == RootWordStatus.EFFECTIVE
            )
        ).all()
        return [
            {
                "word_name": rw.word_name,
                "mysql_type": rw.mysql_type,
                "doris_type": rw.doris_type,
                "clickhouse_type": rw.clickhouse_type,
                "remark": rw.remark
            }
            for rw in root_words
        ]
    finally:
        db.close()

# 创建词根申请
@router.post("/apply", response_model=dict)
async def apply_root_word(
    root_word_data: RootWordCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 查询是否已存在该词根（包括已删除的）
    existing_root_word = db.query(RootWord).filter(
        RootWord.word_name == root_word_data.word_name
    ).first()
    
    if existing_root_word:
        # 如果词根已废弃（delete_flag=1），则恢复并更新为待审核状态
        if existing_root_word.delete_flag == 1 or existing_root_word.status == RootWordStatus.DISCARDED:
            existing_root_word.mysql_type = root_word_data.mysql_type
            existing_root_word.doris_type = root_word_data.doris_type
            existing_root_word.clickhouse_type = root_word_data.clickhouse_type
            existing_root_word.remark = root_word_data.remark
            existing_root_word.status = RootWordStatus.PENDING_AUDIT
            existing_root_word.apply_user = current_user.get("username")
            existing_root_word.apply_time = datetime.utcnow()
            existing_root_word.delete_flag = 0
            existing_root_word.audit_user = None
            existing_root_word.audit_time = None
            existing_root_word.audit_remark = None
            db.commit()
            
            # 插入操作日志
            operation_log = RootWordOperationLog(
                word_id=existing_root_word.id,
                operation_type=OperationType.CREATE,
                operation_user=current_user.get("username"),
                operation_content=f"重新申请已废弃词根：{root_word_data.word_name}"
            )
            db.add(operation_log)
            db.commit()
            
            return {
                "code": 200,
                "msg": "词根重新申请成功，请等待审核",
                "data": {
                    "word_id": existing_root_word.id
                }
            }
        else:
            # 词根已存在且未废弃
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="词根名称已存在"
            )
    
    # 校验类型格式是否符合各引擎规范
    # 这里可以添加更详细的类型校验逻辑
    
    # 插入词根表
    new_root_word = RootWord(
        word_name=root_word_data.word_name,
        mysql_type=root_word_data.mysql_type,
        doris_type=root_word_data.doris_type,
        clickhouse_type=root_word_data.clickhouse_type,
        remark=root_word_data.remark,
        status=RootWordStatus.PENDING_AUDIT,
        apply_user=current_user.get("username"),
        apply_time=datetime.utcnow()
    )
    db.add(new_root_word)
    db.commit()
    db.refresh(new_root_word)
    
    # 插入操作日志
    operation_log = RootWordOperationLog(
        word_id=new_root_word.id,
        operation_type=OperationType.CREATE,
        operation_user=current_user.get("username"),
        operation_content=f"创建词根：{root_word_data.word_name}"
    )
    db.add(operation_log)
    db.commit()
    
    return {
        "code": 200,
        "msg": "词根申请创建成功",
        "data": {
            "word_id": new_root_word.id
        }
    }

# 删除待审核词根
@router.delete("/delete-pending/{word_id}", response_model=dict)
async def delete_pending_root_word(
    word_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 查询词根
    root_word = db.query(RootWord).filter(
        and_(
            RootWord.id == word_id,
            RootWord.delete_flag == 0
        )
    ).first()
    if not root_word:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="词根不存在"
        )
    
    # 校验词根状态为待审核
    if root_word.status != RootWordStatus.PENDING_AUDIT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只能删除待审核状态的词根"
        )
    
    # 校验操作人是该词根申请人
    if root_word.apply_user != current_user.get("username"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能删除自己申请的词根"
        )
    
    # 逻辑删除词根
    root_word.delete_flag = 1
    db.commit()
    
    # 插入操作日志
    operation_log = RootWordOperationLog(
        word_id=word_id,
        operation_type=OperationType.DELETE,
        operation_user=current_user.get("username"),
        operation_content=f"删除待审核词根：{root_word.word_name}"
    )
    db.add(operation_log)
    db.commit()
    
    return {
        "code": 200,
        "msg": "词根删除成功",
        "data": {}
    }

# 识别数据库引擎
def identify_database_engine(ddl_content: str) -> str:
    """识别DDL语句所属的数据库引擎"""
    ddl_lower = ddl_content.lower()
    
    # ClickHouse 特征 - 特定的MergeTree引擎类型
    if 'replacingmergetree' in ddl_lower or 'mergetree(' in ddl_lower or 'summingmergetree' in ddl_lower:
        return 'clickhouse'
    # Doris 特征
    elif 'doris' in ddl_lower or 'duplicate key' in ddl_lower or 'engine = olap' in ddl_lower or 'distributed by' in ddl_lower:
        return 'doris'
    # MySQL 特征（默认）
    else:
        return 'mysql'

# 提取字段信息
def extract_fields(ddl_content: str) -> list:
    """从DDL语句中提取字段信息，返回 (字段名, 字段类型, 字段注释) 的列表"""
    fields = []
    debug_info = {"steps": []}
    
    # 清理DDL内容，移除多余的空白和注释
    clean_ddl = re.sub(r'--.*$', '', ddl_content, flags=re.MULTILINE)
    clean_ddl = re.sub(r'/\*.*?\*/', '', clean_ddl, flags=re.DOTALL)
    clean_ddl = clean_ddl.strip()
    debug_info["steps"].append(f"清理后的DDL长度: {len(clean_ddl)}")
    
    # 查找CREATE TABLE语句中的字段定义部分
    # 匹配 CREATE TABLE table_name ( 后的内容，支持反引号包裹的表名
    table_match = re.search(
        r'create\s+table\s+(?:`?[^`\(]+`?\s*)\((.*)',
        clean_ddl, 
        re.DOTALL | re.IGNORECASE
    )
    
    if not table_match:
        debug_info["steps"].append("未匹配到CREATE TABLE语句")
        # 尝试更宽松的匹配
        table_match = re.search(
            r'create\s+table\s+.*\((.*)',
            clean_ddl, 
            re.DOTALL | re.IGNORECASE
        )
    
    if table_match:
        table_body = table_match.group(1)
        debug_info["steps"].append(f"提取到表体内容，长度: {len(table_body)}")
        debug_info["table_body_preview"] = table_body[:200] + "..." if len(table_body) > 200 else table_body
        
        # 找到最后一个闭合括号之前的所有内容（排除表级约束和引擎定义）
        # 找到 ENGINE、PARTITION BY、ORDER BY、SETTINGS 等关键字之前的部分
        # 注意：COMMENT 在字段级别使用，不应该作为结束标记
        end_keywords = ['ENGINE', 'PARTITION BY', 'ORDER BY', 'SETTINGS', 'DISTRIBUTED BY']
        end_pos = len(table_body)
        for keyword in end_keywords:
            # 匹配 ') KEYWORD' 或 ')\nKEYWORD' 模式（表级关键字）
            pattern = re.compile(r'\s*\)\s*' + keyword, re.IGNORECASE)
            match = pattern.search(table_body)
            if match:
                end_pos = min(end_pos, match.start())
        
        if end_pos < len(table_body):
            table_body = table_body[:end_pos]
            debug_info["steps"].append(f"截断到引擎定义前，新长度: {len(table_body)}")
        
        # 分割字段定义，考虑括号内的逗号
        field_defs = []
        depth = 0
        current_field = ""
        
        for char in table_body:
            if char == '(':
                depth += 1
                current_field += char
            elif char == ')':
                if depth > 0:
                    depth -= 1
                current_field += char
            elif char == ',' and depth == 0:
                if current_field.strip():
                    field_defs.append(current_field.strip())
                current_field = ""
            else:
                current_field += char
        
        # 添加最后一个字段
        if current_field.strip():
            field_defs.append(current_field.strip())
        
        debug_info["steps"].append(f"分割得到 {len(field_defs)} 个字段定义")
        if field_defs:
            debug_info["first_field_preview"] = field_defs[0][:100] if len(field_defs[0]) > 100 else field_defs[0]
        
        # 解析每个字段定义
        for i, field_def in enumerate(field_defs):
            field_def = field_def.strip()
            if not field_def:
                continue
            
            debug_info["steps"].append(f"处理字段 {i+1}: {field_def[:50]}...")
            
            # 跳过约束定义
            if field_def.lower().startswith(('primary key', 'unique', 'foreign key', 'key', 'index', 'constraint')):
                debug_info["steps"].append(f"  跳过约束定义")
                continue
            
            # 匹配字段名和类型
            # 字段名可以是：字母数字下划线，或者被反引号包裹
            # 类型可能包含括号，如 varchar(32)，或者不带括号如 DateTime
            # ClickHouse 类型可能包含 Nullable() 包装
            # 需要处理 COMMENT 注释
            
            # 提取 COMMENT 内容（支持单引号、双引号、反引号包裹的注释）
            comment_match = re.search(r"\s+COMMENT\s+(['\"`])(.*?)\1", field_def, flags=re.IGNORECASE)
            field_comment = comment_match.group(2) if comment_match else ""
            
            # 移除 COMMENT 部分用于匹配字段名和类型
            field_def_no_comment = re.sub(r"\s+COMMENT\s+(['\"`]).*?\1", '', field_def, flags=re.IGNORECASE)
            
            field_match = re.match(
                r'^`?([a-zA-Z_][a-zA-Z0-9_]*)`?\s+(Nullable\()?([a-zA-Z][a-zA-Z0-9_]*(?:\([^)]*\))?)(\))?',
                field_def_no_comment,
                re.IGNORECASE
            )
            
            if field_match:
                field_name = field_match.group(1)
                # 组合类型，包括 Nullable 包装
                nullable_prefix = field_match.group(2) or ""
                base_type = field_match.group(3)
                nullable_suffix = field_match.group(4) or ""
                field_type = f"{nullable_prefix}{base_type}{nullable_suffix}"
                # 返回三元组：(字段名, 字段类型, 字段注释)
                fields.append((field_name, field_type, field_comment))
                debug_info["steps"].append(f"  成功匹配: {field_name} - {field_type} - 注释: {field_comment[:20] if field_comment else '无'}")
            else:
                debug_info["steps"].append(f"  未匹配到字段名和类型")
    else:
        debug_info["steps"].append("未能提取表体内容")
    
    # 将调试信息附加到函数上，供调用者使用
    extract_fields.debug_info = debug_info
    return fields

# DDL 词根校验
@router.post("/ddl/check", response_model=DDLCheckResponse)
async def check_ddl_root_word(
    ddl_request: DDLCheckRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 识别数据库引擎
    db_engine = identify_database_engine(ddl_request.ddl_content)
    
    # 提取表字段
    fields = extract_fields(ddl_request.ddl_content)
    
    # 校验词根
    compliant_fields = []
    non_compliant_fields = []
    missing_root_words = []
    
    for field_name, field_type, field_comment in fields:
        # 直接查询词根表，匹配完整的字段名
        root_word = db.query(RootWord).filter(
            and_(
                RootWord.word_name == field_name,
                RootWord.status == RootWordStatus.EFFECTIVE,
                RootWord.delete_flag == 0
            )
        ).first()
        
        if root_word:
            # 根据数据库引擎选择对应的类型
            if db_engine == 'mysql':
                standard_type = root_word.mysql_type
            elif db_engine == 'doris':
                standard_type = root_word.doris_type
            else:  # clickhouse
                standard_type = root_word.clickhouse_type
            
            # 简单校验类型
            if field_type.lower() == standard_type.lower():
                compliant_fields.append({
                    "field_name": field_name,
                    "field_type": field_type,
                    "field_comment": field_comment,
                    "root_word": field_name,
                    "standard_type": standard_type,
                    "remark": root_word.remark
                })
            else:
                non_compliant_fields.append({
                    "field_name": field_name,
                    "field_type": field_type,
                    "field_comment": field_comment,
                    "root_word": field_name,
                    "standard_type": standard_type,
                    "remark": root_word.remark,
                    "reason": "类型不一致"
                })
        else:
            # 词根不存在，添加到缺失列表
            if field_name not in [word['word_name'] for word in missing_root_words]:
                missing_root_words.append({
                    "word_name": field_name,
                    "suggested_type": field_type,
                    "field_comment": field_comment
                })
            
            non_compliant_fields.append({
                "field_name": field_name,
                "field_type": field_type,
                "field_comment": field_comment,
                "reason": "未找到匹配的词根"
            })
    
    # 不记录 DDL 校验的操作日志，因为没有具体的词根 ID
    # 避免外键约束错误
    
    # 获取调试信息
    debug_info = getattr(extract_fields, 'debug_info', {})
    
    return DDLCheckResponse(
        code=200,
        msg="DDL 校验完成" if len(fields) > 0 else "DDL 校验完成：未提取到字段信息",
        data={
            "compliant_fields": compliant_fields,
            "non_compliant_fields": non_compliant_fields,
            "missing_root_words": missing_root_words,
            "database_engine": db_engine,
            "parsed_fields": [{"field_name": f[0], "field_type": f[1], "field_comment": f[2]} for f in fields],
            "debug_info": debug_info
        }
    )

# 词根替换（DDL 属性替换）
@router.post("/ddl/replace", response_model=dict)
async def replace_ddl_root_word(
    ddl_request: DDLCheckRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 识别数据库引擎
    db_engine = identify_database_engine(ddl_request.ddl_content)
    ddl_content = ddl_request.ddl_content
    
    # 提取表字段并替换类型
    fields = extract_fields(ddl_request.ddl_content)
    
    for field_name, old_type, field_comment in fields:
        # 提取词根（简单按下划线拆分）
        parts = field_name.split('_')
        for part in parts:
            # 查询词根
            root_word = db.query(RootWord).filter(
                and_(
                    RootWord.word_name == part,
                    RootWord.status == RootWordStatus.EFFECTIVE,
                    RootWord.delete_flag == 0
                )
            ).first()
            if root_word:
                # 根据数据库引擎选择对应的类型
                if db_engine == 'mysql':
                    new_type = root_word.mysql_type
                elif db_engine == 'doris':
                    new_type = root_word.doris_type
                else:  # clickhouse
                    new_type = root_word.clickhouse_type
                
                # 替换类型
                ddl_content = ddl_content.replace(
                    f"{field_name} {old_type}",
                    f"{field_name} {new_type}"
                )
                break
    
    # 不记录 DDL 替换的操作日志，因为没有具体的词根 ID
    # 避免外键约束错误
    
    return {
        "code": 200,
        "msg": "DDL 词根替换完成",
        "data": {
            "replaced_ddl": ddl_content,
            "database_engine": db_engine
        }
    }

# 审核词根（管理员）
@router.post("/audit", response_model=dict)
async def audit_root_word(
    audit_data: RootWordAudit,
    current_user: dict = Depends(check_admin_permission),
    db: Session = Depends(get_db)
):
    # 查询词根
    root_word = db.query(RootWord).filter(
        and_(
            RootWord.id == audit_data.word_id,
            RootWord.delete_flag == 0
        )
    ).first()
    if not root_word:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="词根不存在"
        )
    
    # 校验词根状态为待审核
    if root_word.status != RootWordStatus.PENDING_AUDIT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只能审核待审核状态的词根"
        )
    
    # 更新词根状态
    if audit_data.audit_result == 1:
        # 通过
        root_word.status = RootWordStatus.EFFECTIVE
        root_word.audit_user = current_user.get("username")
        root_word.audit_time = datetime.utcnow()
        root_word.audit_remark = audit_data.audit_remark
        operation_content = f"审核通过词根：{root_word.word_name}"
    else:
        # 驳回
        root_word.audit_user = current_user.get("username")
        root_word.audit_time = datetime.utcnow()
        root_word.audit_remark = audit_data.audit_remark
        operation_content = f"审核驳回词根：{root_word.word_name}，原因：{audit_data.audit_remark}"
    
    db.commit()
    
    # 插入操作日志
    operation_log = RootWordOperationLog(
        word_id=audit_data.word_id,
        operation_type=OperationType.AUDIT,
        operation_user=current_user.get("username"),
        operation_content=operation_content
    )
    db.add(operation_log)
    db.commit()
    
    return {
        "code": 200,
        "msg": "词根审核完成",
        "data": {}
    }

# 废弃已生效词根（管理员）
@router.post("/discard/{word_id}", response_model=dict)
async def discard_root_word(
    word_id: int,
    current_user: dict = Depends(check_admin_permission),
    db: Session = Depends(get_db)
):
    # 查询词根
    root_word = db.query(RootWord).filter(
        and_(
            RootWord.id == word_id,
            RootWord.delete_flag == 0
        )
    ).first()
    if not root_word:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="词根不存在"
        )
    
    # 校验词根状态为已生效
    if root_word.status != RootWordStatus.EFFECTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只能废弃已生效状态的词根"
        )
    
    # 更新状态为已废弃
    root_word.status = RootWordStatus.DISCARDED
    db.commit()
    
    # 插入操作日志
    operation_log = RootWordOperationLog(
        word_id=word_id,
        operation_type=OperationType.DISCARD,
        operation_user=current_user.get("username"),
        operation_content=f"废弃词根：{root_word.word_name}"
    )
    db.add(operation_log)
    db.commit()
    
    return {
        "code": 200,
        "msg": "词根废弃成功",
        "data": {}
    }

# 编辑词根（管理员）
@router.put("/update", response_model=dict)
async def update_root_word(
    update_data: RootWordUpdate,
    current_user: dict = Depends(check_admin_permission),
    db: Session = Depends(get_db)
):
    # 查询词根
    root_word = db.query(RootWord).filter(
        and_(
            RootWord.id == update_data.word_id,
            RootWord.delete_flag == 0
        )
    ).first()
    if not root_word:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="词根不存在"
        )
    
    # 如果修改了词根名称，检查是否与其他词根冲突
    if update_data.word_name and update_data.word_name != root_word.word_name:
        existing = db.query(RootWord).filter(
            and_(
                RootWord.word_name == update_data.word_name,
                RootWord.delete_flag == 0,
                RootWord.id != update_data.word_id
            )
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="词根名称已存在"
            )
        root_word.word_name = update_data.word_name
    
    # 更新其他字段
    if update_data.mysql_type:
        root_word.mysql_type = update_data.mysql_type
    if update_data.doris_type:
        root_word.doris_type = update_data.doris_type
    if update_data.clickhouse_type:
        root_word.clickhouse_type = update_data.clickhouse_type
    if update_data.remark is not None:
        root_word.remark = update_data.remark
    
    db.commit()
    
    # 插入操作日志
    operation_log = RootWordOperationLog(
        word_id=update_data.word_id,
        operation_type=OperationType.UPDATE,
        operation_user=current_user.get("username"),
        operation_content=f"编辑词根：{root_word.word_name}"
    )
    db.add(operation_log)
    db.commit()
    
    return {
        "code": 200,
        "msg": "词根编辑成功",
        "data": {
            "word_id": root_word.id,
            "word_name": root_word.word_name,
            "mysql_type": root_word.mysql_type,
            "doris_type": root_word.doris_type,
            "clickhouse_type": root_word.clickhouse_type,
            "remark": root_word.remark
        }
    }

# 强制删除词根（管理员）
@router.delete("/force-delete/{word_id}", response_model=dict)
async def force_delete_root_word(
    word_id: int,
    current_user: dict = Depends(check_admin_permission),
    db: Session = Depends(get_db)
):
    # 查询词根
    root_word = db.query(RootWord).filter(
        and_(
            RootWord.id == word_id,
            RootWord.delete_flag == 0
        )
    ).first()
    if not root_word:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="词根不存在"
        )
    
    # 逻辑删除词根
    root_word.delete_flag = 1
    db.commit()
    
    # 插入操作日志
    operation_log = RootWordOperationLog(
        word_id=word_id,
        operation_type=OperationType.DELETE,
        operation_user=current_user.get("username"),
        operation_content=f"强制删除词根：{root_word.word_name}"
    )
    db.add(operation_log)
    db.commit()
    
    return {
        "code": 200,
        "msg": "词根删除成功",
        "data": {}
    }

# 恢复废弃词根（管理员）
@router.post("/recover/{word_id}", response_model=dict)
async def recover_root_word(
    word_id: int,
    current_user: dict = Depends(check_admin_permission),
    db: Session = Depends(get_db)
):
    # 查询词根
    root_word = db.query(RootWord).filter(
        and_(
            RootWord.id == word_id,
            RootWord.delete_flag == 0
        )
    ).first()
    if not root_word:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="词根不存在"
        )
    
    # 校验词根状态为已废弃
    if root_word.status != RootWordStatus.DISCARDED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只能恢复已废弃状态的词根"
        )
    
    # 更新状态为已生效
    root_word.status = RootWordStatus.EFFECTIVE
    db.commit()
    
    # 插入操作日志
    operation_log = RootWordOperationLog(
        word_id=word_id,
        operation_type=OperationType.RECOVER,
        operation_user=current_user.get("username"),
        operation_content=f"恢复词根：{root_word.word_name}"
    )
    db.add(operation_log)
    db.commit()
    
    return {
        "code": 200,
        "msg": "词根恢复成功",
        "data": {}
    }

# 词根列表查询
@router.post("/list", response_model=dict)
async def list_root_word(
    query_data: RootWordListRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 构建查询
    query = db.query(RootWord).filter(RootWord.delete_flag == 0)
    
    # 应用筛选条件
    if query_data.word_name:
        query = query.filter(RootWord.word_name.like(f"%{query_data.word_name}%"))
    if query_data.status:
        query = query.filter(RootWord.status == query_data.status)
    if query_data.apply_user:
        query = query.filter(RootWord.apply_user == query_data.apply_user)
    
    # 计算总数
    total = query.count()
    
    # 分页
    offset = (query_data.page_num - 1) * query_data.page_size
    root_words = query.offset(offset).limit(query_data.page_size).all()
    
    # 构建响应数据
    items = []
    for root_word in root_words:
        items.append(
            RootWordResponse(
                id=root_word.id,
                word_name=root_word.word_name,
                mysql_type=root_word.mysql_type,
                doris_type=root_word.doris_type,
                clickhouse_type=root_word.clickhouse_type,
                remark=root_word.remark,
                status=root_word.status,
                apply_user=root_word.apply_user,
                apply_time=root_word.apply_time,
                audit_user=root_word.audit_user,
                audit_time=root_word.audit_time,
                audit_remark=root_word.audit_remark,
                delete_flag=root_word.delete_flag,
                create_time=root_word.create_time,
                update_time=root_word.update_time
            )
        )
    
    return {
        "code": 200,
        "msg": "查询成功",
        "data": {
            "list": items,
            "total": total,
            "page_num": query_data.page_num,
            "page_size": query_data.page_size
        }
    }
