<template>
  <div class="app-container">
    <el-container v-if="isLoggedIn">
      <el-header height="60px" class="header">
        <div class="header-left">
          <el-button
            type="text"
            class="menu-toggle-btn"
            @click="toggleSidebar"
            v-show="!isMobile"
          >
            <el-icon><menu /></el-icon>
          </el-button>
          <el-button
            type="text"
            class="menu-toggle-btn mobile-menu-btn"
            @click="toggleSidebar"
            v-show="isMobile"
          >
            <el-icon><menu /></el-icon>
          </el-button>
          <div class="logo">词根管理工具</div>
        </div>
        <div class="user-info">
          <span class="username">{{ userInfo.username }}</span>
          <el-dropdown>
            <span class="el-dropdown-link">
              {{ userInfo.role === 'admin' ? '管理员' : '普通用户' }}
              <el-icon class="el-icon--right"><arrow-down /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item v-if="userInfo.role === 'admin'" @click="goToUserManagement">用户管理</el-dropdown-item>
                <el-dropdown-item @click="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-container>
        <el-aside
          :width="sidebarWidth"
          class="sidebar"
          :class="{ 'sidebar-collapsed': sidebarCollapsed, 'sidebar-mobile': isMobile && sidebarVisible }"
        >
          <el-menu
            :default-active="activeMenu"
            class="el-menu-vertical-demo"
            @select="handleMenuSelect"
            :collapse="sidebarCollapsed && !isMobile"
          >
            <el-menu-item index="/root-word/list">
              <el-icon><menu /></el-icon>
              <template #title>
                <span>词根列表</span>
              </template>
            </el-menu-item>
            <el-menu-item index="/root-word/apply">
              <el-icon><plus /></el-icon>
              <template #title>
                <span>申请词根</span>
              </template>
            </el-menu-item>
            <el-menu-item index="/root-word/ddl-check">
              <el-icon><edit /></el-icon>
              <template #title>
                <span>DDL 校验</span>
              </template>
            </el-menu-item>
            <el-menu-item index="/root-word/audit">
              <el-icon><check /></el-icon>
              <template #title>
                <span>词根审核</span>
              </template>
            </el-menu-item>
          </el-menu>
        </el-aside>
        <el-main class="main-content" :class="{ 'main-content-expanded': sidebarCollapsed || isMobile && !sidebarVisible }">
          <router-view v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </el-main>
      </el-container>
    </el-container>
    <router-view v-else />
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowDown, Menu, Plus, Edit, Check, User } from '@element-plus/icons-vue'

export default {
  name: 'App',
  components: {
    ArrowDown,
    Menu,
    Plus,
    User,
    Edit,
    Check
  },
  setup() {
    const router = useRouter()
    const activeMenu = ref('/root-word/list')
    const userInfo = ref({})
    const sidebarCollapsed = ref(false)
    const sidebarVisible = ref(true)
    const isMobile = ref(false)
    
    // 计算是否已登录
    const isLoggedIn = computed(() => {
      return localStorage.getItem('token') !== null
    })
    
    // 计算侧边栏宽度
    const sidebarWidth = computed(() => {
      if (isMobile.value) {
        return sidebarVisible.value ? '200px' : '0px'
      }
      return sidebarCollapsed.value ? '64px' : '200px'
    })
    
    // 获取用户信息
    const getUserInfo = () => {
      const userStr = localStorage.getItem('user')
      if (userStr) {
        userInfo.value = JSON.parse(userStr)
      }
    }
    
    // 处理菜单选择
    const handleMenuSelect = (key) => {
      activeMenu.value = key
      router.push(key)
      // 在移动设备上选择菜单后自动折叠侧边栏
      if (isMobile.value) {
        sidebarVisible.value = false
      }
    }
    
    // 切换侧边栏
    const toggleSidebar = () => {
      if (isMobile.value) {
        sidebarVisible.value = !sidebarVisible.value
      } else {
        sidebarCollapsed.value = !sidebarCollapsed.value
      }
    }
    
    // 退出登录
    const logout = () => {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      router.push('/login')
    }
    
    // 跳转到用户管理
    const goToUserManagement = () => {
      router.push('/user/management')
    }
    
    // 检查是否为移动设备
    const checkMobile = () => {
      isMobile.value = window.innerWidth < 768
      if (isMobile.value) {
        sidebarVisible.value = false
      } else {
        sidebarVisible.value = true
      }
    }
    
    // 挂载时获取用户信息和检查设备类型
    onMounted(() => {
      getUserInfo()
      checkMobile()
      window.addEventListener('resize', checkMobile)
    })
    
    // 卸载时移除事件监听
    onUnmounted(() => {
      window.removeEventListener('resize', checkMobile)
    })
    
    return {
      activeMenu,
      userInfo,
      isLoggedIn,
      sidebarWidth,
      sidebarCollapsed,
      sidebarVisible,
      isMobile,
      handleMenuSelect,
      toggleSidebar,
      logout,
      goToUserManagement
    }
  }
}
</script>

<style scoped>
.app-container {
  width: 100vw;
  height: 100vh;
  overflow: hidden;
}

.header {
  background-color: #409EFF;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.menu-toggle-btn {
  color: white;
  font-size: 20px;
}

.mobile-menu-btn {
  font-size: 24px;
}

.logo {
  font-size: 20px;
  font-weight: bold;
  white-space: nowrap;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.username {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 120px;
}

.sidebar {
  background-color: #f5f7fa;
  border-right: 1px solid #e4e7ed;
  transition: all 0.3s ease;
}

.sidebar-collapsed {
  transition: all 0.3s ease;
}

.sidebar-mobile {
  position: fixed;
  left: 0;
  top: 60px;
  height: calc(100vh - 60px);
  z-index: 1000;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
}

.main-content {
  padding: 20px;
  overflow-y: auto;
  overflow-x: hidden;
  height: calc(100vh - 60px);
  transition: all 0.3s ease;
}

.main-content-expanded {
  transition: all 0.3s ease;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 响应式样式 */
@media screen and (max-width: 768px) {
  .header {
    padding: 0 15px;
  }
  
  .logo {
    font-size: 18px;
  }
  
  .user-info {
    gap: 10px;
  }
  
  .username {
    max-width: 80px;
  }
  
  .main-content {
    padding: 15px;
  }
}

@media screen and (max-width: 480px) {
  .header {
    padding: 0 10px;
  }
  
  .logo {
    font-size: 16px;
  }
  
  .main-content {
    padding: 10px;
  }
}
</style>
