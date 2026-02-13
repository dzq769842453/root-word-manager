import request from './request'

// 创建用户
export function createUser(data) {
  return request({
    url: '/user/create',
    method: 'post',
    data
  })
}

// 获取用户列表
export function getUserList(params) {
  return request({
    url: '/user/list',
    method: 'get',
    params
  })
}

// 删除用户
export function deleteUser(userId) {
  return request({
    url: `/user/delete/${userId}`,
    method: 'delete'
  })
}

// 重置密码
export function resetPassword(userId, newPassword) {
  return request({
    url: `/user/reset-password/${userId}`,
    method: 'post',
    params: { new_password: newPassword }
  })
}
