<template>
  <div class="ddl-check">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>DDL 词根校验</span>
        </div>
      </template>
      
      <el-form :model="ddlForm" class="ddl-form">
        <el-form-item label="DDL 内容">
          <el-input
            v-model="ddlForm.ddlContent"
            type="textarea"
            :rows="10"
            placeholder="请输入 DDL 语句，如：CREATE TABLE user (user_id bigint, user_name varchar(32))"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleCheck">校验 DDL</el-button>
          <el-button @click="resetForm">清空</el-button>
        </el-form-item>
      </el-form>
      
      <!-- 校验结果 -->
      <div v-if="checkResult" class="check-result">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <h3>校验结果</h3>
          <el-tag v-if="checkResult.data.database_engine" :type="getEngineTagType(checkResult.data.database_engine)" size="large" effect="dark">
            {{ getEngineDisplayName(checkResult.data.database_engine) }}
          </el-tag>
        </div>
        <el-divider />
        
        <!-- 一键操作按钮区域 -->
        <div style="margin-bottom: 20px; padding: 15px; background: #f0f9ff; border-radius: 4px; border: 1px solid #91d5ff;">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="color: #096dd9; font-weight: 500;">批量操作</span>
            <el-button-group>
              <el-button 
                v-if="typeMismatchFields.length > 0"
                type="warning" 
                @click="handleBatchReplaceType"
              >
                一键替换词根类型 ({{ typeMismatchFields.length }})
              </el-button>
              <el-button 
                v-if="missingRootWords.length > 0"
                type="success" 
                @click="handleBatchApplyFromTable"
              >
                一键申请缺失词根 ({{ missingRootWords.length }})
              </el-button>
            </el-button-group>
          </div>
        </div>
        
        <!-- 字段校验结果表单 -->
        <div v-if="checkResult.data.parsed_fields && checkResult.data.parsed_fields.length > 0" class="table-container">
          <h4>字段校验结果</h4>
          <div class="table-scroll-container">
            <el-table 
              :data="fieldCheckResults" 
              style="width: 100%;" 
              border
              height="400"
              :header-cell-style="{background:'#f5f7fa', color:'#606266'}"
            >
              <el-table-column type="index" label="序号" width="60" />
              <el-table-column prop="field_name" label="字段名" min-width="150" show-overflow-tooltip />
              <el-table-column prop="field_type" label="DDL字段类型" min-width="130" show-overflow-tooltip />
              <el-table-column prop="matched_root_word" label="匹配词根" min-width="140" show-overflow-tooltip />
              <el-table-column prop="standard_type" label="词根库标准类型" min-width="150" show-overflow-tooltip />
              <el-table-column label="状态" width="100">
                <template #default="scope">
                  <el-tag :type="scope.row.status === '合规' ? 'success' : scope.row.status === '类型不一致' ? 'warning' : 'danger'" size="small">
                    {{ scope.row.status }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="100">
                <template #default="scope">
                  <el-button 
                    v-if="scope.row.status === '缺失词根'"
                    type="primary" 
                    size="small" 
                    @click="handleApplyRootWord({word_name: scope.row.matched_root_word, suggested_type: scope.row.field_type, field_comment: scope.row.field_comment})"
                  >
                    申请
                  </el-button>
                  <el-button 
                    v-else-if="scope.row.status === '类型不一致'"
                    type="warning" 
                    size="small" 
                    @click="handleReplaceSingleType(scope.row)"
                  >
                    替换
                  </el-button>
                  <el-tag v-else-if="scope.row.status === '合规'" type="success" size="small">✓</el-tag>
                </template>
              </el-table-column>
            </el-table>
          </div>
          <div class="table-info" v-if="fieldCheckResults.length > 0">
            <small style="color: #909399;">共 {{ fieldCheckResults.length }} 条记录，表格可上下左右滚动查看</small>
          </div>
        </div>
        
        <!-- 详细调试信息 -->
        <div v-if="checkResult.data.debug_info" style="margin-top: 20px; padding: 10px; background: #fff3cd; border-radius: 4px; border: 1px solid #ffc107;">
          <h4 @click="showDebugDetails = !showDebugDetails" style="cursor: pointer; margin: 0;">
            调试信息 (点击{{ showDebugDetails ? '收起' : '展开' }})
          </h4>
          <div v-if="showDebugDetails" style="margin-top: 10px;">
            <div v-if="checkResult.data.debug_info.table_body_preview" style="margin-bottom: 10px;">
              <strong>表体预览：</strong>
              <pre style="background: #f8f9fa; padding: 5px; overflow-x: auto;">{{ checkResult.data.debug_info.table_body_preview }}</pre>
            </div>
            <div v-if="checkResult.data.debug_info.first_field_preview" style="margin-bottom: 10px;">
              <strong>第一个字段预览：</strong>
              <pre style="background: #f8f9fa; padding: 5px; overflow-x: auto;">{{ checkResult.data.debug_info.first_field_preview }}</pre>
            </div>
            <div>
              <strong>处理步骤：</strong>
              <ol style="margin: 5px 0; padding-left: 20px;">
                <li v-for="(step, index) in checkResult.data.debug_info.steps" :key="index">{{ step }}</li>
              </ol>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 替换结果 -->
      <div v-if="replaceResult" class="replace-result">
        <h3>替换结果</h3>
        <el-divider />
        <el-input
          v-model="replaceResult.data.replaced_ddl"
          type="textarea"
          :rows="10"
          placeholder="替换后的 DDL 语句"
          readonly
        />
      </div>
    </el-card>
    
    <!-- 单个词根申请对话框 -->
    <el-dialog
      v-model="applyDialogVisible"
      title="申请词根"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form :model="applyForm" label-width="120px" :rules="applyRules" ref="applyFormRef">
        <el-form-item label="词根名称" prop="word_name">
          <el-input v-model="applyForm.word_name" placeholder="请输入词根名称" disabled />
        </el-form-item>
        <el-form-item label="MySQL 类型" prop="mysql_type">
          <el-input v-model="applyForm.mysql_type" placeholder="如：bigint, varchar(32)" />
        </el-form-item>
        <el-form-item label="Doris 类型" prop="doris_type">
          <el-input v-model="applyForm.doris_type" placeholder="如：BIGINT, VARCHAR(32)" />
        </el-form-item>
        <el-form-item label="ClickHouse 类型" prop="clickhouse_type">
          <el-input v-model="applyForm.clickhouse_type" placeholder="如：Int64, String" />
        </el-form-item>
        <el-form-item label="词根注释" prop="remark">
          <el-input 
            v-model="applyForm.remark" 
            type="textarea" 
            :rows="3"
            placeholder="请输入词根注释"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="applyDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitApply" :loading="applyLoading">确定</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 批量申请词根对话框 -->
    <el-dialog
      v-model="batchApplyDialogVisible"
      title="批量申请词根"
      width="800px"
      :close-on-click-modal="false"
    >
      <el-table :data="batchApplyList" style="width: 100%" border max-height="400">
        <el-table-column prop="word_name" label="词根名称" width="150" />
        <el-table-column label="MySQL 类型" width="150">
          <template #default="scope">
            <el-input v-model="scope.row.mysql_type" size="small" />
          </template>
        </el-table-column>
        <el-table-column label="Doris 类型" width="150">
          <template #default="scope">
            <el-input v-model="scope.row.doris_type" size="small" />
          </template>
        </el-table-column>
        <el-table-column label="ClickHouse 类型" width="150">
          <template #default="scope">
            <el-input v-model="scope.row.clickhouse_type" size="small" />
          </template>
        </el-table-column>
        <el-table-column label="注释">
          <template #default="scope">
            <el-input v-model="scope.row.remark" size="small" />
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="batchApplyDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitBatchApply" :loading="batchApplyLoading">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { checkDDLRootWord, replaceDDLRootWord, applyRootWord } from '../api/rootWord'

export default {
  name: 'DDLCheck',
  setup() {
    const ddlForm = ref({
      ddlContent: ''
    })
    const checkResult = ref(null)
    const replaceResult = ref(null)
    const showDebugDetails = ref(false)
    
    // 单个申请对话框相关
    const applyDialogVisible = ref(false)
    const applyLoading = ref(false)
    const applyFormRef = ref(null)
    const applyForm = ref({
      word_name: '',
      mysql_type: '',
      doris_type: '',
      clickhouse_type: '',
      remark: ''
    })
    const applyRules = {
      word_name: [{ required: true, message: '请输入词根名称', trigger: 'blur' }],
      mysql_type: [{ required: true, message: '请输入MySQL类型', trigger: 'blur' }],
      doris_type: [{ required: true, message: '请输入Doris类型', trigger: 'blur' }],
      clickhouse_type: [{ required: true, message: '请输入ClickHouse类型', trigger: 'blur' }]
    }
    
    // 批量申请对话框相关
    const batchApplyDialogVisible = ref(false)
    const batchApplyLoading = ref(false)
    const batchApplyList = ref([])
    
    // 计算属性：字段校验结果表格数据
    const fieldCheckResults = computed(() => {
      if (!checkResult.value || !checkResult.value.data.parsed_fields) {
        return []
      }
      
      const compliantFields = checkResult.value.data.compliant_fields || []
      const nonCompliantFields = checkResult.value.data.non_compliant_fields || []
      const missingRootWords = checkResult.value.data.missing_root_words || []
      
      return checkResult.value.data.parsed_fields.map(field => {
        // 查找合规字段
        const compliant = compliantFields.find(f => f.field_name === field.field_name)
        if (compliant) {
          return {
            field_name: field.field_name,
            field_type: field.field_type,
            field_comment: field.field_comment,
            matched_root_word: compliant.root_word,
            standard_type: compliant.standard_type,
            remark: compliant.remark,
            status: '合规'
          }
        }
        
        // 查找不合规字段（类型不一致）
        const nonCompliant = nonCompliantFields.find(f => f.field_name === field.field_name && f.reason === '类型不一致')
        if (nonCompliant) {
          return {
            field_name: field.field_name,
            field_type: field.field_type,
            field_comment: field.field_comment,
            matched_root_word: nonCompliant.root_word,
            standard_type: nonCompliant.standard_type,
            remark: nonCompliant.remark,
            status: '类型不一致'
          }
        }
        
        // 查找缺失词根（现在直接匹配完整的字段名）
        const missing = missingRootWords.find(m => m.word_name === field.field_name)
        if (missing) {
          return {
            field_name: field.field_name,
            field_type: field.field_type,
            field_comment: field.field_comment,
            matched_root_word: field.field_name,
            standard_type: '-',
            status: '缺失词根'
          }
        }
        
        // 默认情况
        return {
          field_name: field.field_name,
          field_type: field.field_type,
          field_comment: field.field_comment,
          matched_root_word: field.field_name,
          standard_type: '-',
          status: '缺失词根'
        }
      })
    })
    
    // 计算属性：缺失的词根列表（用于批量申请）
    const missingRootWords = computed(() => {
      return fieldCheckResults.value.filter(f => f.status === '缺失词根')
    })
    
    // 计算属性：类型不一致的字段列表（用于一键替换）
    const typeMismatchFields = computed(() => {
      return fieldCheckResults.value.filter(f => f.status === '类型不一致')
    })
    
    // 获取数据库引擎显示名称
    const getEngineDisplayName = (engine) => {
      const engineMap = {
        'mysql': 'MySQL',
        'doris': 'Doris',
        'clickhouse': 'ClickHouse'
      }
      return engineMap[engine] || engine
    }
    
    // 获取数据库引擎标签类型
    const getEngineTagType = (engine) => {
      const typeMap = {
        'mysql': 'success',
        'doris': 'primary',
        'clickhouse': 'warning'
      }
      return typeMap[engine] || 'info'
    }
    
    // 处理 DDL 校验
    const handleCheck = async () => {
      try {
        if (!ddlForm.value.ddlContent) {
          ElMessage.warning('请输入 DDL 内容')
          return
        }
        
        const response = await checkDDLRootWord(ddlForm.value.ddlContent)
        checkResult.value = response
        replaceResult.value = null
        
        // 显示详细的校验结果
        const totalFields = (response.data.compliant_fields?.length || 0) + (response.data.non_compliant_fields?.length || 0)
        const missingWordsCount = response.data.missing_root_words?.length || 0
        
        if (missingWordsCount > 0) {
          ElMessage.warning(`DDL 校验完成：共 ${totalFields} 个字段，其中 ${missingWordsCount} 个词根需要申请`)
        } else if (totalFields > 0) {
          ElMessage.success(`DDL 校验完成：共 ${totalFields} 个字段，所有词根均已存在`)
        } else {
          ElMessage.info('DDL 校验完成：未提取到字段信息')
        }
      } catch (error) {
        ElMessage.error('DDL 校验失败：' + (error.msg || error.message || '未知错误'))
      }
    }
    
    // 处理词根替换
    const handleReplace = async () => {
      try {
        if (!ddlForm.value.ddlContent) {
          ElMessage.warning('请输入 DDL 内容')
          return
        }
        
        const response = await replaceDDLRootWord(ddlForm.value.ddlContent)
        replaceResult.value = response
        checkResult.value = null
        
        // 显示详细的替换结果
        const replacedDDL = response.data.replaced_ddl
        if (replacedDDL) {
          ElMessage.success('词根替换完成，已根据词根表中的标准类型更新字段类型')
        } else {
          ElMessage.info('词根替换完成，未检测到需要替换的字段')
        }
      } catch (error) {
        ElMessage.error('词根替换失败：' + (error.msg || error.message || '未知错误'))
      }
    }
    
    // 重置表单
    const resetForm = () => {
      ddlForm.value.ddlContent = ''
      checkResult.value = null
      replaceResult.value = null
    }
    
    // 打开单个词根申请对话框
    const handleApplyRootWord = (rootWord) => {
      // 优先使用DDL中的字段注释，如果没有则使用默认提示
      const fieldComment = rootWord.field_comment || ''
      const defaultRemark = fieldComment 
        ? fieldComment 
        : `从DDL校验中申请的词根，建议类型：${rootWord.suggested_type}`
      
      applyForm.value = {
        word_name: rootWord.word_name,
        mysql_type: rootWord.suggested_type,
        doris_type: rootWord.suggested_type,
        clickhouse_type: rootWord.suggested_type,
        remark: defaultRemark
      }
      applyDialogVisible.value = true
    }
    
    // 提交单个词根申请
    const submitApply = async () => {
      if (!applyFormRef.value) return
      
      await applyFormRef.value.validate(async (valid) => {
        if (valid) {
          try {
            applyLoading.value = true
            await applyRootWord(applyForm.value)
            ElMessage.success('词根申请成功，请等待审核')
            applyDialogVisible.value = false
            
            // 刷新校验结果
            if (ddlForm.value.ddlContent) {
              await handleCheck()
            }
          } catch (error) {
            ElMessage.error('词根申请失败：' + (error.msg || error.message || '未知错误'))
          } finally {
            applyLoading.value = false
          }
        }
      })
    }
    
    // 替换单个字段类型和注释
    const handleReplaceSingleType = (row) => {
      // 在DDL中替换该字段的类型和注释
      let ddlContent = ddlForm.value.ddlContent
      const fieldName = row.field_name
      const oldType = row.field_type
      const newType = row.standard_type
      const newRemark = row.remark || ''
      
      // 处理反引号包裹的字段名
      const escapedFieldName = fieldName.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
      
      // 构建正则表达式来匹配字段定义（包括可选的COMMENT）
      // 匹配模式：字段名 类型 [COMMENT 'xxx']
      const fullRegex = new RegExp(
        `(\\\`?${escapedFieldName}\\\`?\\s+)${oldType.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}(\\s+COMMENT\\s+'[^']*')?`,
        'i'
      )
      
      if (fullRegex.test(ddlContent)) {
        // 替换类型和注释
        const replacement = newRemark 
          ? `$1${newType} COMMENT '${newRemark}'`
          : `$1${newType}`
        ddlContent = ddlContent.replace(fullRegex, replacement)
        ddlForm.value.ddlContent = ddlContent
        ElMessage.success(`已将 ${fieldName} 的类型从 ${oldType} 替换为 ${newType}${newRemark ? '，注释已更新' : ''}`)
      } else {
        // 如果直接替换失败，尝试更宽松的匹配（处理Nullable包装）
        const looseRegex = new RegExp(
          `(\\\`?${escapedFieldName}\\\`?\\s+)(Nullable\\()?${oldType.replace(/[.*+?^${}()|[\]\\]/g, '\\$&').replace('Nullable(', '')}(\\))?(\\s+COMMENT\\s+'[^']*')?`,
          'i'
        )
        if (looseRegex.test(ddlContent)) {
          const replacement = newRemark
            ? `$1$2${newType}$3 COMMENT '${newRemark}'`
            : `$1$2${newType}$3`
          ddlContent = ddlContent.replace(looseRegex, replacement)
          ddlForm.value.ddlContent = ddlContent
          ElMessage.success(`已将 ${fieldName} 的类型从 ${oldType} 替换为 ${newType}${newRemark ? '，注释已更新' : ''}`)
        } else {
          ElMessage.warning(`未找到字段 ${fieldName} 的类型定义`)
        }
      }
    }
    
    // 一键替换所有类型不一致的字段
    const handleBatchReplaceType = () => {
      const mismatchFields = typeMismatchFields.value
      if (mismatchFields.length === 0) {
        ElMessage.warning('没有需要替换类型的字段')
        return
      }
      
      let ddlContent = ddlForm.value.ddlContent
      let replaceCount = 0
      let failCount = 0
      
      mismatchFields.forEach(row => {
        const fieldName = row.field_name
        const oldType = row.field_type
        const newType = row.standard_type
        const newRemark = row.remark || ''
        
        // 处理反引号包裹的字段名
        const escapedFieldName = fieldName.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
        
        // 构建正则表达式来匹配字段定义（包括可选的COMMENT）
        const fullRegex = new RegExp(
          `(\\\`?${escapedFieldName}\\\`?\\s+)${oldType.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}(\\s+COMMENT\\s+'[^']*')?`,
          'i'
        )
        
        if (fullRegex.test(ddlContent)) {
          const replacement = newRemark
            ? `$1${newType} COMMENT '${newRemark}'`
            : `$1${newType}`
          ddlContent = ddlContent.replace(fullRegex, replacement)
          replaceCount++
        } else {
          // 尝试更宽松的匹配（处理Nullable包装）
          const looseRegex = new RegExp(
            `(\\\`?${escapedFieldName}\\\`?\\s+)(Nullable\\()?${oldType.replace(/[.*+?^${}()|[\]\\]/g, '\\$&').replace('Nullable(', '')}(\\))?(\\s+COMMENT\\s+'[^']*')?`,
            'i'
          )
          if (looseRegex.test(ddlContent)) {
            const replacement = newRemark
              ? `$1$2${newType}$3 COMMENT '${newRemark}'`
              : `$1$2${newType}$3`
            ddlContent = ddlContent.replace(looseRegex, replacement)
            replaceCount++
          } else {
            failCount++
          }
        }
      })
      
      ddlForm.value.ddlContent = ddlContent
      
      if (replaceCount > 0 && failCount === 0) {
        ElMessage.success(`一键替换完成：共替换 ${replaceCount} 个字段的类型和注释`)
      } else if (replaceCount > 0 && failCount > 0) {
        ElMessage.warning(`替换完成：成功 ${replaceCount} 个，失败 ${failCount} 个`)
      } else {
        ElMessage.error(`替换失败：未能替换任何字段`)
      }
    }
    
    // 从表格打开批量申请对话框
    const handleBatchApplyFromTable = () => {
      const missingFields = missingRootWords.value
      if (missingFields.length === 0) {
        ElMessage.warning('没有可申请的词根')
        return
      }
      
      batchApplyList.value = missingFields.map(field => {
        // 优先使用DDL中的字段注释
        const fieldComment = field.field_comment || ''
        const defaultRemark = fieldComment
          ? fieldComment
          : `从DDL校验中申请的词根，字段：${field.field_name}，类型：${field.field_type}`
        
        return {
          word_name: field.matched_root_word,
          mysql_type: field.field_type,
          doris_type: field.field_type,
          clickhouse_type: field.field_type,
          remark: defaultRemark
        }
      })
      
      batchApplyDialogVisible.value = true
    }
    
    // 打开批量申请对话框（兼容旧版）
    const handleBatchApplyRootWord = () => {
      if (!checkResult.value || !checkResult.value.data.missing_root_words) {
        ElMessage.warning('没有可申请的词根')
        return
      }
      
      const missingWords = checkResult.value.data.missing_root_words
      batchApplyList.value = missingWords.map(word => {
        // 优先使用DDL中的字段注释
        const fieldComment = word.field_comment || ''
        const defaultRemark = fieldComment
          ? fieldComment
          : `从DDL校验中申请的词根，建议类型：${word.suggested_type}`
        
        return {
          word_name: word.word_name,
          mysql_type: word.suggested_type,
          doris_type: word.suggested_type,
          clickhouse_type: word.suggested_type,
          remark: defaultRemark
        }
      })
      
      batchApplyDialogVisible.value = true
    }
    
    // 提交批量申请
    const submitBatchApply = async () => {
      try {
        batchApplyLoading.value = true
        let successCount = 0
        let failCount = 0
        let failReasons = []
        
        for (const rootWord of batchApplyList.value) {
          try {
            await applyRootWord(rootWord)
            successCount++
          } catch (error) {
            failCount++
            failReasons.push(`${rootWord.word_name}：${error.msg || error.message || '未知错误'}`)
          }
        }
        
        if (successCount > 0) {
          ElMessage.success(`批量申请完成：成功 ${successCount} 个，失败 ${failCount} 个`)
        }
        if (failCount > 0) {
          ElMessage.warning(`失败原因：\n${failReasons.join('\n')}`)
        }
        
        batchApplyDialogVisible.value = false
        
        // 刷新校验结果
        if (ddlForm.value.ddlContent) {
          await handleCheck()
        }
      } catch (error) {
        ElMessage.error('批量申请失败：' + (error.msg || error.message || '未知错误'))
      } finally {
        batchApplyLoading.value = false
      }
    }
    
    return {
      ddlForm,
      checkResult,
      replaceResult,
      showDebugDetails,
      fieldCheckResults,
      missingRootWords,
      typeMismatchFields,
      applyDialogVisible,
      applyLoading,
      applyForm,
      applyRules,
      applyFormRef,
      batchApplyDialogVisible,
      batchApplyLoading,
      batchApplyList,
      getEngineDisplayName,
      getEngineTagType,
      handleCheck,
      resetForm,
      handleApplyRootWord,
      submitApply,
      handleReplaceSingleType,
      handleBatchReplaceType,
      handleBatchApplyRootWord,
      handleBatchApplyFromTable,
      submitBatchApply
    }
  }
}
</script>

<style scoped>
.ddl-check {
  padding: 0;
  min-height: calc(100vh - 100px);
  overflow: visible;
}

:deep(.el-card) {
  overflow: visible;
}

:deep(.el-card__body) {
  overflow: visible;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.ddl-form {
  margin-bottom: 30px;
}

.check-result,
.replace-result {
  margin-top: 30px;
}

.check-result h4,
.replace-result h4 {
  margin-top: 20px;
}

/* 表格容器样式 */
.table-container {
  width: 100%;
  margin-top: 15px;
}

.table-scroll-container {
  width: 100%;
  overflow: auto;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  max-height: 400px;
}

.table-scroll-container .el-table {
  margin: 0;
}

.table-info {
  text-align: center;
  padding: 8px;
  background: #f5f7fa;
  border-radius: 0 0 4px 4px;
  margin-top: -1px;
  border: 1px solid #ebeef5;
  border-top: none;
}

.check-result h3 {
  margin-bottom: 10px;
  font-weight: bold;
}

/* 响应式样式 */
@media screen and (max-width: 768px) {
  .ddl-check {
    padding: 10px;
  }
  
  /* 调整表单 */
  .ddl-form {
    margin-bottom: 20px;
  }
  
  .el-form-item {
    margin-bottom: 15px;
  }
  
  .el-input {
    font-size: 14px;
  }
  
  .el-input__textarea {
    min-height: 150px;
  }
  
  /* 调整按钮 */
  .el-button {
    font-size: 14px;
    padding: 8px 16px;
    margin-right: 10px;
  }
  
  /* 调整结果区域 */
  .check-result,
  .replace-result {
    margin-top: 20px;
  }
  
  /* 调整表格 */
  .el-table {
    font-size: 14px;
  }
  
  .el-table-column {
    font-size: 14px;
  }
  
  /* 隐藏一些列以适应小屏幕 */
  .el-table-column:nth-child(4) { /* 标准类型 */
    display: none;
  }
  
  /* 调整表格列宽度 */
  .el-table-column:nth-child(1) { /* 字段名 */
    width: 120px !important;
  }
}

@media screen and (max-width: 480px) {
  /* 进一步调整表单 */
  .el-form {
    label-width: 80px;
  }
  
  .el-form-item__label {
    font-size: 13px;
  }
  
  .el-input {
    font-size: 13px;
  }
  
  .el-input__textarea {
    min-height: 120px;
  }
  
  /* 调整按钮 */
  .el-button {
    font-size: 13px;
    padding: 6px 12px;
    margin-right: 8px;
    margin-bottom: 10px;
  }
  
  /* 调整表格 */
  .el-table-column:nth-child(3) { /* 匹配词根 */
    display: none;
  }
  
  /* 调整表格列宽度 */
  .el-table-column:nth-child(1) { /* 字段名 */
    width: 100px !important;
  }
}

/* 确保表格在移动设备上可以水平滚动 */
@media screen and (max-width: 768px) {
  .check-result,
  .replace-result {
    overflow-x: auto;
  }
  
  .el-table {
    min-width: 500px;
  }
}

/* 确保页面在小屏幕上可以垂直滚动 */
@media screen and (max-height: 600px) {
  .ddl-check {
    overflow-y: auto;
    max-height: calc(100vh - 60px);
  }
}
</style>
