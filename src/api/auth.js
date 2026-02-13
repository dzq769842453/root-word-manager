import axios from 'axios'

// 登录接口
export const login = async (username, password) => {
  try {
    // 使用 URLSearchParams 格式发送数据
    const params = new URLSearchParams()
    params.append('username', username)
    params.append('password', password)
    
    const response = await axios.post('/api/auth/login', params, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    })
    return response.data
  } catch (error) {
    console.error('登录请求错误:', error)
    throw error.response ? error.response.data : { msg: '网络错误' }
  }
}
