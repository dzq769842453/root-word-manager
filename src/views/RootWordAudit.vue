<template>
  <div class="root-word-audit">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>词根审核</span>
          <span v-if="!isAdmin" class="view-only-tag">仅查看模式</span>
        </div>
      </template>

      <!-- 批量操作工具栏 - 仅管理员可见 -->
      <div class="batch-toolbar" v-if="isAdmin && pendingRootWords.length > 0">
        <el-checkbox
          v-model="selectAll"
          @change="handleSelectAll"
          class="select-all-checkbox"
        >
          全选
        </el-checkbox>
        <span class="selected-count" v-if="selectedIds.length > 0">
          已选择 {{ selectedIds.length }} 条
        </span>
        <el-button-group v-if="selectedIds.length > 0">
          <el-button type="success" size="small" @click="handleBatchAudit('pass')">
            批量通过
          </el-button>
          <el-button type="danger" size="small" @click="handleBatchAudit('reject')">
            批量驳回
          </el-button>
        </el-button-group>
      </div>

      <!-- 待审核词根列表 -->
      <el-table
        :data="pendingRootWords"
        style="width: 100%"
        border
        @selection-change="handleSelectionChange"
      >
        <el-table-column v-if="isAdmin" type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="word_name" label="词根名称" width="150" />
        <el-table-column prop="mysql_type" label="MySQL 类型" width="120" />
        <el-table-column prop="doris_type" label="Doris 类型" width="120" />
        <el-table-column prop="clickhouse_type" label="ClickHouse 类型" width="150" />
        <el-table-column prop="apply_user" label="申请人" width="120" />
        <el-table-column prop="apply_time" label="申请时间" width="180" />
        <el-table-column v-if="isAdmin" label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button type="primary" size="small" @click="handleAudit(scope.row, 'pass')">通过</el-button>
            <el-button type="danger" size="small" @click="handleAudit(scope.row, 'reject')">驳回</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 审核弹窗 -->
      <el-dialog
        v-model="auditDialogVisible"
        :title="auditDialogTitle"
        width="500px"
      >
        <el-form :model="auditForm" :rules="auditRules" label-width="80px">
          <el-form-item label="词根名称">
            <el-input v-model="auditForm.word_name" readonly />
          </el-form-item>
          <el-form-item label="审核结果">
            <el-radio-group v-model="auditForm.audit_result">
              <el-radio label="1">通过</el-radio>
              <el-radio label="2">驳回</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="审核备注" prop="audit_remark">
            <el-input
              v-model="auditForm.audit_remark"
              type="textarea"
              :rows="3"
              placeholder="请输入审核备注，驳回时必填"
            />
          </el-form-item>
        </el-form>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="auditDialogVisible = false">取消</el-button>
            <el-button type="primary" @click="submitAudit">确定</el-button>
          </span>
        </template>
      </el-dialog>
      
      <!-- 批量审核弹窗 -->
      <el-dialog
        v-model="batchAuditDialogVisible"
        :title="batchAuditDialogTitle"
        width="500px"
      >
        <el-form :model="batchAuditForm" :rules="batchAuditRules" label-width="80px">
          <el-form-item label="审核数量">
            <el-input :value="selectedIds.length + ' 个词根'" readonly />
          </el-form-item>
          <el-form-item label="审核结果">
            <el-radio-group v-model="batchAuditForm.audit_result">
              <el-radio label="1">通过</el-radio>
              <el-radio label="2">驳回</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="审核备注" prop="audit_remark">
            <el-input
              v-model="batchAuditForm.audit_remark"
              type="textarea"
              :rows="3"
              placeholder="请输入审核备注，驳回时必填"
            />
          </el-form-item>
        </el-form>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="batchAuditDialogVisible = false">取消</el-button>
            <el-button type="primary" @click="submitBatchAudit" :loading="batchAuditLoading">确定</el-button>
          </span>
        </template>
      </el-dialog>
    </el-card>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { listRootWord, auditRootWord } from '../api/rootWord'

export default {
  name: 'RootWordAudit',
  setup() {
    // 判断是否为管理员
    const isAdmin = computed(() => {
      const userStr = localStorage.getItem('user')
      if (userStr) {
        const user = JSON.parse(userStr)
        return user.role === 'admin'
      }
      return false
    })

    const pendingRootWords = ref([])
    const auditDialogVisible = ref(false)
    const auditDialogTitle = ref('审核词根')
    const auditForm = ref({
      word_id: '',
      word_name: '',
      audit_result: '1',
      audit_remark: ''
    })
    const auditRules = ref({
      audit_remark: [
        {
          required: true,
          message: '请输入审核备注',
          trigger: 'blur',
          validator: (rule, value, callback) => {
            if (auditForm.value.audit_result === '2' && !value) {
              callback(new Error('驳回时必须填写审核备注'))
            } else {
              callback()
            }
          }
        }
      ]
    })
    
    // 批量审核相关
    const selectAll = ref(false)
    const selectedIds = ref([])
    const batchAuditDialogVisible = ref(false)
    const batchAuditDialogTitle = ref('批量审核词根')
    const batchAuditLoading = ref(false)
    const batchAuditForm = ref({
      audit_result: '1',
      audit_remark: ''
    })
    const batchAuditRules = ref({
      audit_remark: [
        {
          required: true,
          message: '请输入审核备注',
          trigger: 'blur',
          validator: (rule, value, callback) => {
            if (batchAuditForm.value.audit_result === '2' && !value) {
              callback(new Error('驳回时必须填写审核备注'))
            } else {
              callback()
            }
          }
        }
      ]
    })
    
    // 获取待审核词根列表
    const getPendingRootWords = async () => {
      try {
        const response = await listRootWord({
          page_num: 1,
          page_size: 100,
          status: 'pending_audit'
        })
        pendingRootWords.value = response.data.list
      } catch (error) {
        ElMessage.error('获取待审核词根列表失败')
      }
    }
    
    // 处理审核
    const handleAudit = (rootWord, type) => {
      auditForm.value = {
        word_id: rootWord.id,
        word_name: rootWord.word_name,
        audit_result: type === 'pass' ? '1' : '2',
        audit_remark: ''
      }
      auditDialogTitle.value = `审核词根：${rootWord.word_name}`
      auditDialogVisible.value = true
    }
    
    // 提交审核
    const submitAudit = async () => {
      try {
        // 表单验证
        await ElMessageBox.confirm(
          `确定要${auditForm.value.audit_result === '1' ? '通过' : '驳回'}该词根吗？`,
          '审核确认',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: auditForm.value.audit_result === '1' ? 'success' : 'warning'
          }
        )
        
        // 调用审核接口
        await auditRootWord({
          word_id: auditForm.value.word_id,
          audit_result: parseInt(auditForm.value.audit_result),
          audit_remark: auditForm.value.audit_remark
        })
        
        ElMessage.success('审核完成')
        auditDialogVisible.value = false
        getPendingRootWords()
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('审核失败')
        }
      }
    }
    
    // 处理表格选择变化
    const handleSelectionChange = (selection) => {
      selectedIds.value = selection.map(item => item.id)
      selectAll.value = selection.length === pendingRootWords.value.length && selection.length > 0
    }
    
    // 处理全选
    const handleSelectAll = (val) => {
      if (val) {
        selectedIds.value = pendingRootWords.value.map(item => item.id)
      } else {
        selectedIds.value = []
      }
    }
    
    // 打开批量审核对话框
    const handleBatchAudit = (type) => {
      if (selectedIds.value.length === 0) {
        ElMessage.warning('请先选择要审核的词根')
        return
      }
      batchAuditForm.value = {
        audit_result: type === 'pass' ? '1' : '2',
        audit_remark: ''
      }
      batchAuditDialogTitle.value = type === 'pass' ? '批量通过词根' : '批量驳回词根'
      batchAuditDialogVisible.value = true
    }
    
    // 提交批量审核
    const submitBatchAudit = async () => {
      try {
        // 验证：驳回时必须填写备注
        if (batchAuditForm.value.audit_result === '2' && !batchAuditForm.value.audit_remark) {
          ElMessage.error('驳回时必须填写审核备注')
          return
        }
        
        // 确认对话框
        await ElMessageBox.confirm(
          `确定要${batchAuditForm.value.audit_result === '1' ? '通过' : '驳回'}选中的 ${selectedIds.value.length} 个词根吗？`,
          '批量审核确认',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: batchAuditForm.value.audit_result === '1' ? 'success' : 'warning'
          }
        )
        
        batchAuditLoading.value = true
        let successCount = 0
        let failCount = 0
        
        // 逐个调用审核接口
        for (const wordId of selectedIds.value) {
          try {
            await auditRootWord({
              word_id: wordId,
              audit_result: parseInt(batchAuditForm.value.audit_result),
              audit_remark: batchAuditForm.value.audit_remark
            })
            successCount++
          } catch (error) {
            failCount++
          }
        }
        
        if (successCount > 0) {
          ElMessage.success(`批量审核完成：成功 ${successCount} 个${failCount > 0 ? `，失败 ${failCount} 个` : ''}`)
        } else {
          ElMessage.error('批量审核失败')
        }
        
        batchAuditDialogVisible.value = false
        selectedIds.value = []
        selectAll.value = false
        getPendingRootWords()
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('批量审核失败')
        }
      } finally {
        batchAuditLoading.value = false
      }
    }
    
    // 初始化
    onMounted(() => {
      getPendingRootWords()
    })
    
    return {
      isAdmin,
      pendingRootWords,
      auditDialogVisible,
      auditDialogTitle,
      auditForm,
      auditRules,
      handleAudit,
      submitAudit,
      selectAll,
      selectedIds,
      batchAuditDialogVisible,
      batchAuditDialogTitle,
      batchAuditLoading,
      batchAuditForm,
      batchAuditRules,
      handleSelectionChange,
      handleSelectAll,
      handleBatchAudit,
      submitBatchAudit
    }
  }
}
</script>

<style scoped>
.root-word-audit {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dialog-footer {
  width: 100%;
  display: flex;
  justify-content: flex-end;
}

/* 仅查看模式标签 */
.view-only-tag {
  font-size: 12px;
  color: #909399;
  background-color: #f4f4f5;
  padding: 2px 8px;
  border-radius: 4px;
  margin-left: 10px;
}

/* 批量操作工具栏 */
.batch-toolbar {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 10px 0;
  margin-bottom: 10px;
  border-bottom: 1px solid #e4e7ed;
}

.select-all-checkbox {
  font-weight: 500;
}

.selected-count {
  font-weight: 500;
  color: #409eff;
}

/* 响应式样式 */
@media screen and (max-width: 768px) {
  .root-word-audit {
    padding: 10px;
  }
  
  /* 调整表格布局 */
  .el-table {
    font-size: 14px;
  }
  
  .el-table-column {
    font-size: 14px;
  }
  
  /* 隐藏一些列以适应小屏幕 */
  .el-table-column:nth-child(4), /* MySQL 类型 */
  .el-table-column:nth-child(5), /* Doris 类型 */
  .el-table-column:nth-child(6) { /* ClickHouse 类型 */
    display: none;
  }
  
  /* 调整按钮大小 */
  .el-button--small {
    padding: 4px 8px;
    font-size: 11px;
  }
  
  /* 调整对话框大小 */
  .el-dialog {
    width: 90% !important;
    margin: 20px auto !important;
  }
  
  .el-dialog__header {
    padding: 15px 20px;
  }
  
  .el-dialog__body {
    padding: 20px;
  }
  
  .el-dialog__footer {
    padding: 15px 20px;
  }
}

@media screen and (max-width: 480px) {
  /* 进一步调整表格列 */
  .el-table-column:nth-child(3) { /* 词根名称 */
    width: 120px !important;
  }
  
  /* 调整对话框表单 */
  .el-form {
    label-width: 80px;
  }
  
  .el-form-item__label {
    font-size: 13px;
  }
  
  .el-input {
    font-size: 13px;
  }
  
  /* 调整按钮 */
  .el-button {
    font-size: 13px;
    padding: 6px 12px;
  }
}

/* 确保表格在移动设备上可以水平滚动 */
@media screen and (max-width: 768px) {
  .el-card__body {
    overflow-x: auto;
  }
  
  .el-table {
    min-width: 600px;
  }
}
</style>
