import axios from 'axios'

// 创建用户
export const createUser = async (userData) => {
  try {
    const response = await axios.post('/api/user/create', userData)
    return response.data
  } catch (error) {
    throw error.response?.data || error
  }
}

// 获取用户列表
export const getUserList = async (params) => {
  try {
    const response = await axios.get('/api/user/list', { params })
    return response.data
  } catch (error) {
    throw error.response?.data || error
  }
}

// 删除用户
export const deleteUser = async (userId) => {
  try {
    const response = await axios.delete(`/api/user/delete/${userId}`)
    return response.data
  } catch (error) {
    throw error.response?.data || error
  }
}

// 重置密码
export const resetPassword = async (userId, newPassword) => {
  try {
    const response = await axios.post(`/api/user/reset-password/${userId}`, null, {
      params: { new_password: newPassword }
    })
    return response.data
  } catch (error) {
    throw error.response?.data || error
  }
}
