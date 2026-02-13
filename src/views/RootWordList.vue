<template>
  <div class="root-word-list">
    <el-card class="main-card">
      <template #header>
        <div class="card-header">
          <span>词根列表</span>
        </div>
      </template>
      
      <!-- 固定部分：搜索表单和批量操作工具栏 -->
      <div class="fixed-header">
        <!-- 搜索和筛选 -->
        <el-form :inline="true" :model="searchForm" class="search-form">
          <el-form-item label="词根名称">
            <el-input v-model="searchForm.word_name" placeholder="请输入词根名称" style="width: 200px" />
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="searchForm.status" placeholder="请选择状态" style="width: 150px">
              <el-option label="待审核" value="pending_audit" />
              <el-option label="已生效" value="effective" />
              <el-option label="已废弃" value="discarded" />
            </el-select>
          </el-form-item>
          <el-form-item label="申请人">
            <el-input v-model="searchForm.apply_user" placeholder="请输入申请人" style="width: 150px" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">查询</el-button>
            <el-button @click="resetForm">重置</el-button>
          </el-form-item>
        </el-form>
        
        <!-- 批量操作工具栏 -->
        <div class="batch-operation-toolbar" v-if="userInfo.role === 'admin'">
          <el-button-group>
            <el-button
              type="warning"
              size="small"
              :disabled="selectedRows.length === 0"
              @click="handleBatchDiscard"
              :title="selectedRows.length > 0 ? '批量废弃已选中的词根' : '请先选择词根'"
            >
              批量废弃
            </el-button>
            <el-button
              type="primary"
              size="small"
              :disabled="selectedRows.length === 0"
              @click="handleBatchRecover"
              :title="selectedRows.length > 0 ? '批量恢复已选中的词根' : '请先选择词根'"
            >
              批量恢复
            </el-button>
            <el-button
              type="danger"
              size="small"
              :disabled="selectedRows.length === 0"
              @click="handleBatchDelete"
              :title="selectedRows.length > 0 ? '批量删除已选中的词根' : '请先选择词根'"
            >
              批量删除
            </el-button>
          </el-button-group>
          <el-badge :value="selectedRows.length" class="selected-count" :hidden="selectedRows.length === 0">
            已选择
          </el-badge>
        </div>
      </div>
      
      <!-- 可滚动部分：表格 -->
      <div class="scrollable-table-container">
        <!-- 词根列表 -->
        <el-table 
          :data="rootWordList" 
          style="width: 100%" 
          border 
          v-loading="loading"
          @selection-change="handleSelectionChange"
          show-overflow-tooltip
        >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="word_name" label="词根名称" width="150" />
        <el-table-column prop="mysql_type" label="MySQL 类型" width="120" />
        <el-table-column prop="doris_type" label="Doris 类型" width="120" />
        <el-table-column prop="clickhouse_type" label="ClickHouse 类型" width="150" />
        <el-table-column prop="remark" label="词根注释" width="200" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="apply_user" label="申请人" width="120" />
        <el-table-column prop="apply_time" label="申请时间" width="180" />
        <el-table-column prop="audit_user" label="审核人" width="120" />
        <el-table-column prop="audit_time" label="审核时间" width="180" />
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="scope">
            <!-- 管理员编辑按钮 -->
            <el-button
              v-if="userInfo.role === 'admin'"
              type="primary"
              size="small"
              @click="handleEdit(scope.row)"
            >
              编辑
            </el-button>
            <el-button
              v-if="scope.row.status === 'pending_audit' && scope.row.apply_user === userInfo.username"
              type="danger"
              size="small"
              @click="handleDeletePending(scope.row.id, scope.row.word_name)"
            >
              删除
            </el-button>
            <el-button
              v-if="userInfo.role === 'admin' && scope.row.status === 'effective'"
              type="warning"
              size="small"
              @click="handleDiscard(scope.row.id, scope.row.word_name)"
            >
              废弃
            </el-button>
            <el-button
              v-if="userInfo.role === 'admin' && scope.row.status === 'discarded'"
              type="danger"
              size="small"
              @click="handleForceDelete(scope.row.id, scope.row.word_name)"
            >
              删除
            </el-button>
            <el-button
              v-if="userInfo.role === 'admin' && scope.row.status === 'discarded'"
              type="primary"
              size="small"
              @click="handleRecover(scope.row.id, scope.row.word_name)"
            >
              恢复
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      </div>
      
      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.currentPage"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="pagination.total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          background
        />
      </div>
    </el-card>
    
    <!-- 编辑词根对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑词根"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form :model="editForm" label-width="120px" :rules="editRules" ref="editFormRef">
        <el-form-item label="词根名称" prop="word_name">
          <el-input v-model="editForm.word_name" placeholder="请输入词根名称" />
        </el-form-item>
        <el-form-item label="MySQL 类型" prop="mysql_type">
          <el-input v-model="editForm.mysql_type" placeholder="如：bigint, varchar(32)" />
        </el-form-item>
        <el-form-item label="Doris 类型" prop="doris_type">
          <el-input v-model="editForm.doris_type" placeholder="如：BIGINT, VARCHAR(32)" />
        </el-form-item>
        <el-form-item label="ClickHouse 类型" prop="clickhouse_type">
          <el-input v-model="editForm.clickhouse_type" placeholder="如：Int64, String" />
        </el-form-item>
        <el-form-item label="词根注释" prop="remark">
          <el-input 
            v-model="editForm.remark" 
            type="textarea" 
            :rows="3"
            placeholder="请输入词根注释"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitEdit" :loading="editLoading">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { listRootWord, deletePendingRootWord, discardRootWord, forceDeleteRootWord, recoverRootWord, updateRootWord } from '../api/rootWord'

export default {
  name: 'RootWordList',
  setup() {
    const rootWordList = ref([])
    const searchForm = ref({
      word_name: '',
      status: '',
      apply_user: ''
    })
    const pagination = ref({
      currentPage: 1,
      pageSize: 10,
      total: 0
    })
    const loading = ref(false)
    const selectedRows = ref([])
    const selectAll = ref(false)
    
    // 编辑对话框相关
    const editDialogVisible = ref(false)
    const editLoading = ref(false)
    const editFormRef = ref(null)
    const editForm = ref({
      word_id: null,
      word_name: '',
      mysql_type: '',
      doris_type: '',
      clickhouse_type: '',
      remark: ''
    })
    const editRules = {
      word_name: [{ required: true, message: '请输入词根名称', trigger: 'blur' }],
      mysql_type: [{ required: true, message: '请输入MySQL类型', trigger: 'blur' }],
      doris_type: [{ required: true, message: '请输入Doris类型', trigger: 'blur' }],
      clickhouse_type: [{ required: true, message: '请输入ClickHouse类型', trigger: 'blur' }]
    }
    
    // 获取用户信息
    const userInfo = computed(() => {
      const userStr = localStorage.getItem('user')
      return userStr ? JSON.parse(userStr) : {}
    })
    
    // 获取词根列表
    const getRootWordList = async () => {
      try {
        loading.value = true
        const response = await listRootWord({
          page_num: pagination.value.currentPage,
          page_size: pagination.value.pageSize,
          word_name: searchForm.value.word_name,
          status: searchForm.value.status,
          apply_user: searchForm.value.apply_user
        })
        rootWordList.value = response.data.list
        pagination.value.total = response.data.total
      } catch (error) {
        ElMessage.error('获取词根列表失败')
      } finally {
        loading.value = false
      }
    }
    
    // 处理搜索
    const handleSearch = () => {
      pagination.value.currentPage = 1
      getRootWordList()
    }
    
    // 重置表单
    const resetForm = () => {
      searchForm.value = {
        word_name: '',
        status: '',
        apply_user: ''
      }
      pagination.value.currentPage = 1
      getRootWordList()
    }
    
    // 处理分页大小变化
    const handleSizeChange = (size) => {
      pagination.value.pageSize = size
      getRootWordList()
    }
    
    // 处理页码变化
    const handleCurrentChange = (current) => {
      pagination.value.currentPage = current
      getRootWordList()
    }
    
    // 处理删除待审核词根
    const handleDeletePending = async (wordId, wordName) => {
      try {
        await ElMessageBox.confirm(
          `确定要删除待审核的词根 "${wordName}" 吗？`,
          '删除确认',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        await deletePendingRootWord(wordId)
        ElMessage.success('删除成功')
        getRootWordList()
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('删除失败')
        }
      }
    }
    
    // 处理废弃词根
    const handleDiscard = async (wordId, wordName) => {
      try {
        await ElMessageBox.confirm(
          `确定要废弃词根 "${wordName}" 吗？`,
          '废弃确认',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        await discardRootWord(wordId)
        ElMessage.success('废弃成功')
        getRootWordList()
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('废弃失败')
        }
      }
    }
    
    // 处理强制删除
    const handleForceDelete = async (wordId, wordName) => {
      try {
        await ElMessageBox.confirm(
          `确定要强制删除词根 "${wordName}" 吗？`,
          '删除确认',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'danger'
          }
        )
        
        await forceDeleteRootWord(wordId)
        ElMessage.success('删除成功')
        getRootWordList()
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('删除失败')
        }
      }
    }
    
    // 处理恢复词根
    const handleRecover = async (wordId, wordName) => {
      try {
        await ElMessageBox.confirm(
          `确定要恢复词根 "${wordName}" 吗？`,
          '恢复确认',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'primary'
          }
        )
        
        await recoverRootWord(wordId)
        ElMessage.success('恢复成功')
        getRootWordList()
      } catch (error) {
        if (error !== 'cancel') {
          if (error?.detail === '只能恢复已废弃状态的词根') {
            ElMessage.warning('该词根不是已废弃状态，无法恢复')
          } else {
            ElMessage.error('恢复失败')
          }
        }
      }
    }
    
    // 处理选择变化
    const handleSelectionChange = (val) => {
      selectedRows.value = val
      // 只有当所有当前页的行都被选中时，才显示全选状态
      selectAll.value = val.length === rootWordList.value.length && rootWordList.value.length > 0
    }
    
    // 处理全选
    const handleSelectAll = (val) => {
      selectAll.value = val
      if (val) {
        // 全选当前页所有行
        selectedRows.value = [...rootWordList.value]
      } else {
        // 取消全选
        selectedRows.value = []
      }
    }
    
    // 处理批量废弃
    const handleBatchDiscard = async () => {
      try {
        await ElMessageBox.confirm(
          `确定要废弃选中的 ${selectedRows.value.length} 个词根吗？`,
          '批量废弃确认',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        // 逐个废弃词根
        for (const row of selectedRows.value) {
          if (row.status === 'effective') {
            await discardRootWord(row.id)
          }
        }
        
        ElMessage.success('批量废弃成功')
        getRootWordList()
        selectedRows.value = []
        selectAll.value = false
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('批量废弃失败')
        }
      }
    }
    
    // 处理批量恢复
    const handleBatchRecover = async () => {
      try {
        await ElMessageBox.confirm(
          `确定要恢复选中的 ${selectedRows.value.length} 个词根吗？`,
          '批量恢复确认',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'primary'
          }
        )
        
        // 逐个恢复词根
        let successCount = 0
        let failCount = 0
        
        for (const row of selectedRows.value) {
          if (row.status === 'discarded') {
            try {
              await recoverRootWord(row.id)
              successCount++
            } catch (error) {
              failCount++
              console.error(`恢复词根 ${row.word_name} 失败:`, error)
            }
          }
        }
        
        if (successCount > 0) {
          ElMessage.success(`成功恢复 ${successCount} 个词根`)
        }
        if (failCount > 0) {
          ElMessage.warning(`有 ${failCount} 个词根恢复失败`)
        }
        
        getRootWordList()
        selectedRows.value = []
        selectAll.value = false
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('批量恢复操作失败')
        }
      }
    }
    
    // 处理批量删除
    const handleBatchDelete = async () => {
      try {
        await ElMessageBox.confirm(
          `确定要删除选中的 ${selectedRows.value.length} 个词根吗？`,
          '批量删除确认',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'danger'
          }
        )
        
        // 逐个删除词根
        for (const row of selectedRows.value) {
          await forceDeleteRootWord(row.id)
        }
        
        ElMessage.success('批量删除成功')
        getRootWordList()
        selectedRows.value = []
        selectAll.value = false
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('批量删除失败')
        }
      }
    }
    
    // 获取状态类型
    const getStatusType = (status) => {
      switch (status) {
        case 'pending_audit':
          return 'info'
        case 'effective':
          return 'success'
        case 'discarded':
          return 'danger'
        default:
          return ''
      }
    }
    
    // 获取状态文本
    const getStatusText = (status) => {
      switch (status) {
        case 'pending_audit':
          return '待审核'
        case 'effective':
          return '已生效'
        case 'discarded':
          return '已废弃'
        default:
          return ''
      }
    }
    
    // 打开编辑对话框
    const handleEdit = (row) => {
      editForm.value = {
        word_id: row.id,
        word_name: row.word_name,
        mysql_type: row.mysql_type,
        doris_type: row.doris_type,
        clickhouse_type: row.clickhouse_type,
        remark: row.remark || ''
      }
      editDialogVisible.value = true
    }
    
    // 提交编辑
    const submitEdit = async () => {
      if (!editFormRef.value) return
      
      await editFormRef.value.validate(async (valid) => {
        if (valid) {
          try {
            editLoading.value = true
            await updateRootWord(editForm.value)
            ElMessage.success('词根编辑成功')
            editDialogVisible.value = false
            getRootWordList()
          } catch (error) {
            ElMessage.error(error.detail || '词根编辑失败')
          } finally {
            editLoading.value = false
          }
        }
      })
    }
    
    // 初始化
    onMounted(() => {
      getRootWordList()
    })
    
    return {
      rootWordList,
      searchForm,
      pagination,
      loading,
      userInfo,
      selectAll,
      selectedRows,
      editDialogVisible,
      editLoading,
      editForm,
      editRules,
      editFormRef,
      handleSearch,
      resetForm,
      handleSizeChange,
      handleCurrentChange,
      handleDeletePending,
      handleDiscard,
      handleForceDelete,
      handleRecover,
      handleBatchDiscard,
      handleBatchRecover,
      handleBatchDelete,
      handleSelectionChange,
      handleSelectAll,
      getStatusType,
      getStatusText,
      handleEdit,
      submitEdit
    }
  }
}
</script>

<style scoped>
.root-word-list {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-form {
  margin-bottom: 20px;
}

.batch-operation-toolbar {
  margin: 15px 0;
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 15px;
}

.select-all-checkbox {
  font-weight: 500;
}

.selected-count {
  margin-left: auto;
  font-weight: 500;
  color: #409eff;
}

.pagination-container {
  margin-top: 15px;
  margin-bottom: 10px;
  display: flex;
  justify-content: flex-end;
  background-color: #fff;
  padding: 15px 0;
  border-top: 1px solid #e4e7ed;
}

/* 为根容器添加底部 padding，确保分页控件有足够的显示空间 */
.root-word-list {
  padding: 15px;
  min-height: 100vh;
  box-sizing: border-box;
}

.main-card {
  height: calc(100vh - 30px);
  display: flex;
  flex-direction: column;
}

/* 固定头部 */
.fixed-header {
  flex-shrink: 0;
  margin-bottom: 10px;
}

/* 可滚动表格容器 */
.scrollable-table-container {
  flex: 1;
  overflow: auto;
  max-height: calc(100vh - 200px);
  position: relative;
}

/* 确保表格容器有足够的空间 */
.el-card__body {
  padding-bottom: 20px;
  box-sizing: border-box;
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* 调整表格样式，确保它在容器中正确显示 */
.el-table {
  width: 100%;
}

/* 分页容器 */
.pagination-container {
  margin-top: 15px;
  margin-bottom: 10px;
  display: flex;
  justify-content: flex-end;
  flex-shrink: 0;
  background-color: #fff;
  padding: 15px 0;
  border-top: 1px solid #e4e7ed;
}

/* 确保表格内容在滚动时不会被分页控件遮挡 */
.el-table__body-wrapper {
  max-height: calc(100vh - 250px);
  overflow-y: auto;
  transition: all 0.3s ease;
}

/* 批量操作工具栏 */
.batch-operation-toolbar {
  margin: 15px 0;
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 15px;
  flex-wrap: wrap;
}

/* 搜索表单 */
.search-form {
  margin-bottom: 15px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: flex-end;
}

/* 响应式样式 */
@media screen and (max-width: 1200px) {
  /* 在中等屏幕上隐藏一些列 */
  .el-table-column:nth-child(9), /* 申请人 */
  .el-table-column:nth-child(10), /* 申请时间 */
  .el-table-column:nth-child(11), /* 审核人 */
  .el-table-column:nth-child(12) { /* 审核时间 */
    display: none;
  }
}

@media screen and (max-width: 992px) {
  /* 在小屏幕上隐藏更多列 */
  .el-table-column:nth-child(6), /* Doris 类型 */
  .el-table-column:nth-child(7) { /* ClickHouse 类型 */
    display: none;
  }
  
  /* 调整搜索表单 */
  .search-form {
    flex-direction: column;
    align-items: stretch;
  }
  
  /* 调整批量操作工具栏 */
  .batch-operation-toolbar {
    justify-content: center;
  }
}

@media screen and (max-width: 768px) {
  .root-word-list {
    padding: 10px;
  }
  
  /* 在移动设备上隐藏更多列 */
  .el-table-column:nth-child(5) { /* MySQL 类型 */
    display: none;
  }
  
  /* 调整表格列宽度 */
  .el-table-column:nth-child(3) { /* 词根名称 */
    width: 120px !important;
  }
  
  /* 调整分页控件 */
  .pagination-container {
    padding: 10px 0;
  }
  
  .el-pagination {
    font-size: 12px;
  }
  
  .el-pagination__sizes {
    margin-right: 5px;
  }
  
  .el-pagination__jump {
    margin-left: 5px;
  }
}

@media screen and (max-width: 480px) {
  /* 在小屏幕上进一步调整 */
  .el-table-column:nth-child(4) { /* 词根注释 */
    display: none;
  }
  
  /* 调整表格列宽度 */
  .el-table-column:nth-child(3) { /* 词根名称 */
    width: 100px !important;
  }
  
  /* 调整操作按钮 */
  .el-button--small {
    padding: 4px 8px;
    font-size: 11px;
  }
}

/* 确保表格在移动设备上可以水平滚动 */
@media screen and (max-width: 768px) {
  .scrollable-table-container {
    overflow-x: auto;
  }
  
  .el-table {
    min-width: 800px;
  }
}
</style>
