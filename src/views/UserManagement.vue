<template>
  <div class="user-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>用户管理</span>
          <el-button type="primary" @click="handleCreateUser">创建用户</el-button>
        </div>
      </template>
      
      <!-- 搜索和筛选 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="用户名">
          <el-input v-model="searchForm.username" placeholder="请输入用户名" style="width: 200px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
      
      <!-- 用户列表 -->
      <el-table :data="userList" style="width: 100%" border v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" width="150" />
        <el-table-column prop="role" label="角色" width="120">
          <template #default="scope">
            <el-tag :type="scope.row.role === 'admin' ? 'danger' : 'info'">
              {{ scope.row.role === 'admin' ? '管理员' : '普通用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="创建时间" width="180" />
        <el-table-column prop="update_time" label="更新时间" width="180" />
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="scope">
            <el-button 
              type="warning" 
              size="small" 
              @click="handleResetPassword(scope.row)"
              :disabled="scope.row.username === currentUsername"
            >
              重置密码
            </el-button>
            <el-button 
              type="danger" 
              size="small" 
              @click="handleDelete(scope.row)"
              :disabled="scope.row.username === currentUsername"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
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
    
    <!-- 创建用户对话框 -->
    <el-dialog
      v-model="createDialogVisible"
      title="创建用户"
      width="500px"
    >
      <el-form :model="createForm" :rules="createRules" ref="createFormRef" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="createForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input 
            v-model="createForm.password" 
            type="password" 
            placeholder="请输入密码"
            show-password
          />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input 
            v-model="createForm.confirmPassword" 
            type="password" 
            placeholder="请再次输入密码"
            show-password
          />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-radio-group v-model="createForm.role">
            <el-radio label="user">普通用户</el-radio>
            <el-radio label="admin">管理员</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="createDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitCreate" :loading="createLoading">确定</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 重置密码对话框 -->
    <el-dialog
      v-model="resetDialogVisible"
      title="重置密码"
      width="400px"
    >
      <el-form :model="resetForm" :rules="resetRules" ref="resetFormRef" label-width="100px">
        <el-form-item label="新密码" prop="newPassword">
          <el-input 
            v-model="resetForm.newPassword" 
            type="password" 
            placeholder="请输入新密码"
            show-password
          />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input 
            v-model="resetForm.confirmPassword" 
            type="password" 
            placeholder="请再次输入新密码"
            show-password
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="resetDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitReset" :loading="resetLoading">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { createUser, getUserList, deleteUser, resetPassword } from '../api/user'

export default {
  name: 'UserManagement',
  setup() {
    const userList = ref([])
    const loading = ref(false)
    const currentUsername = ref(localStorage.getItem('username') || '')
    
    const searchForm = ref({
      username: ''
    })
    
    const pagination = ref({
      currentPage: 1,
      pageSize: 10,
      total: 0
    })
    
    // 创建用户相关
    const createDialogVisible = ref(false)
    const createLoading = ref(false)
    const createFormRef = ref(null)
    const createForm = ref({
      username: '',
      password: '',
      confirmPassword: '',
      role: 'user'
    })
    
    const validateConfirmPassword = (rule, value, callback) => {
      if (value !== createForm.value.password) {
        callback(new Error('两次输入的密码不一致'))
      } else {
        callback()
      }
    }
    
    const createRules = ref({
      username: [
        { required: true, message: '请输入用户名', trigger: 'blur' },
        { min: 3, max: 32, message: '用户名长度应在3-32个字符之间', trigger: 'blur' }
      ],
      password: [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { min: 6, max: 32, message: '密码长度应在6-32个字符之间', trigger: 'blur' }
      ],
      confirmPassword: [
        { required: true, message: '请再次输入密码', trigger: 'blur' },
        { validator: validateConfirmPassword, trigger: 'blur' }
      ],
      role: [
        { required: true, message: '请选择角色', trigger: 'change' }
      ]
    })
    
    // 重置密码相关
    const resetDialogVisible = ref(false)
    const resetLoading = ref(false)
    const resetFormRef = ref(null)
    const resetForm = ref({
      userId: null,
      newPassword: '',
      confirmPassword: ''
    })
    
    const validateResetConfirmPassword = (rule, value, callback) => {
      if (value !== resetForm.value.newPassword) {
        callback(new Error('两次输入的密码不一致'))
      } else {
        callback()
      }
    }
    
    const resetRules = ref({
      newPassword: [
        { required: true, message: '请输入新密码', trigger: 'blur' },
        { min: 6, max: 32, message: '密码长度应在6-32个字符之间', trigger: 'blur' }
      ],
      confirmPassword: [
        { required: true, message: '请再次输入新密码', trigger: 'blur' },
        { validator: validateResetConfirmPassword, trigger: 'blur' }
      ]
    })
    
    // 获取用户列表
    const getUsers = async () => {
      try {
        loading.value = true
        const response = await getUserList({
          page_num: pagination.value.currentPage,
          page_size: pagination.value.pageSize,
          username: searchForm.value.username
        })
        userList.value = response.data.list
        pagination.value.total = response.data.total
      } catch (error) {
        ElMessage.error('获取用户列表失败')
      } finally {
        loading.value = false
      }
    }
    
    // 处理搜索
    const handleSearch = () => {
      pagination.value.currentPage = 1
      getUsers()
    }
    
    // 重置表单
    const resetForm = () => {
      searchForm.value.username = ''
      pagination.value.currentPage = 1
      getUsers()
    }
    
    // 处理分页大小变化
    const handleSizeChange = (size) => {
      pagination.value.pageSize = size
      getUsers()
    }
    
    // 处理页码变化
    const handleCurrentChange = (current) => {
      pagination.value.currentPage = current
      getUsers()
    }
    
    // 打开创建用户对话框
    const handleCreateUser = () => {
      createForm.value = {
        username: '',
        password: '',
        confirmPassword: '',
        role: 'user'
      }
      createDialogVisible.value = true
    }
    
    // 提交创建用户
    const submitCreate = async () => {
      if (!createFormRef.value) return
      
      await createFormRef.value.validate(async (valid) => {
        if (valid) {
          try {
            createLoading.value = true
            await createUser({
              username: createForm.value.username,
              password: createForm.value.password,
              role: createForm.value.role
            })
            ElMessage.success('用户创建成功')
            createDialogVisible.value = false
            getUsers()
          } catch (error) {
            ElMessage.error(error.response?.data?.detail || '用户创建失败')
          } finally {
            createLoading.value = false
          }
        }
      })
    }
    
    // 打开重置密码对话框
    const handleResetPassword = (user) => {
      resetForm.value = {
        userId: user.id,
        newPassword: '',
        confirmPassword: ''
      }
      resetDialogVisible.value = true
    }
    
    // 提交重置密码
    const submitReset = async () => {
      if (!resetFormRef.value) return
      
      await resetFormRef.value.validate(async (valid) => {
        if (valid) {
          try {
            resetLoading.value = true
            await resetPassword(resetForm.value.userId, resetForm.value.newPassword)
            ElMessage.success('密码重置成功')
            resetDialogVisible.value = false
          } catch (error) {
            ElMessage.error(error.response?.data?.detail || '密码重置失败')
          } finally {
            resetLoading.value = false
          }
        }
      })
    }
    
    // 删除用户
    const handleDelete = async (user) => {
      try {
        await ElMessageBox.confirm(
          `确定要删除用户 "${user.username}" 吗？`,
          '删除确认',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        await deleteUser(user.id)
        ElMessage.success('用户删除成功')
        getUsers()
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error(error.response?.data?.detail || '用户删除失败')
        }
      }
    }
    
    // 初始化
    onMounted(() => {
      getUsers()
    })
    
    return {
      userList,
      loading,
      currentUsername,
      searchForm,
      pagination,
      createDialogVisible,
      createLoading,
      createFormRef,
      createForm,
      createRules,
      resetDialogVisible,
      resetLoading,
      resetFormRef,
      resetForm,
      resetRules,
      handleSearch,
      resetForm,
      handleSizeChange,
      handleCurrentChange,
      handleCreateUser,
      submitCreate,
      handleResetPassword,
      submitReset,
      handleDelete
    }
  }
}
</script>

<style scoped>
.user-management {
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

.pagination-container {
  margin-top: 15px;
  margin-bottom: 10px;
  display: flex;
  justify-content: flex-end;
}

.dialog-footer {
  width: 100%;
  display: flex;
  justify-content: flex-end;
}

/* 响应式样式 */
@media screen and (max-width: 768px) {
  .user-management {
    padding: 10px;
  }
  
  .el-form--inline .el-form-item {
    margin-right: 0;
    margin-bottom: 10px;
    width: 100%;
  }
  
  .el-form--inline .el-form-item__content {
    width: 100%;
  }
  
  .el-input {
    width: 100% !important;
  }
}
</style>
