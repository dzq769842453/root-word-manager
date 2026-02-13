<template>
  <div class="login-container">
    <div class="login-form-wrapper">
      <h2 class="login-title">词根管理工具</h2>
      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        label-width="80px"
        class="login-form"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="loginForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            show-password
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" class="login-button" @click="handleLogin">登录</el-button>
        </el-form-item>
      </el-form>
      <div class="login-tip">
        <p>管理员账号：admin/admin123</p>
        <p>普通用户账号：user/user123（需先创建）</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { login } from '../api/auth'

export default {
  name: 'Login',
  setup() {
    const router = useRouter()
    const loginForm = ref({
      username: '',
      password: ''
    })
    const loginRules = ref({
      username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
      password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
    })
    const loginFormRef = ref(null)
    
    // 处理登录
    const handleLogin = async () => {
      try {
        // 表单验证
        await loginFormRef.value.validate()
        
        // 调用登录接口
        const response = await login(loginForm.value.username, loginForm.value.password)
        
        // 保存 token 和用户信息
        localStorage.setItem('token', response.access_token)
        localStorage.setItem('user', JSON.stringify(response.user))
        
        // 跳转到词根列表页面
        router.push('/root-word/list')
      } catch (error) {
        // 处理错误
        console.error('登录错误:', error)
        if (error.msg) {
          ElMessage.error(error.msg)
        } else {
          ElMessage.error('登录失败，请检查用户名和密码')
        }
      }
    }
    
    return {
      loginForm,
      loginRules,
      loginFormRef,
      handleLogin
    }
  }
}
</script>

<style scoped>
.login-container {
  width: 100vw;
  height: 100vh;
  background-color: #f5f7fa;
  display: flex;
  justify-content: center;
  align-items: center;
}

.login-form-wrapper {
  background-color: white;
  padding: 40px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  width: 400px;
}

.login-title {
  text-align: center;
  margin-bottom: 30px;
  color: #409EFF;
}

.login-form {
  margin-bottom: 20px;
}

.login-button {
  width: 100%;
}

.login-tip {
  margin-top: 20px;
  font-size: 12px;
  color: #909399;
  text-align: center;
}

.login-tip p {
  margin: 5px 0;
}
</style>
