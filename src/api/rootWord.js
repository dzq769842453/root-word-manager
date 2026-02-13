import axios from 'axios'

// 创建词根申请
export const applyRootWord = async (rootWordData) => {
  try {
    const response = await axios.post('/api/root-word/apply', rootWordData)
    return response.data
  } catch (error) {
    throw error.response.data
  }
}

// 删除待审核词根
export const deletePendingRootWord = async (wordId) => {
  try {
    const response = await axios.delete(`/api/root-word/delete-pending/${wordId}`)
    return response.data
  } catch (error) {
    throw error.response.data
  }
}

// DDL 词根校验
export const checkDDLRootWord = async (ddlContent) => {
  try {
    const response = await axios.post('/api/root-word/ddl/check', {
      ddl_content: ddlContent
    })
    return response.data
  } catch (error) {
    throw error.response.data
  }
}

// DDL 词根替换
export const replaceDDLRootWord = async (ddlContent) => {
  try {
    const response = await axios.post('/api/root-word/ddl/replace', {
      ddl_content: ddlContent
    })
    return response.data
  } catch (error) {
    throw error.response.data
  }
}

// 审核词根
export const auditRootWord = async (auditData) => {
  try {
    const response = await axios.post('/api/root-word/audit', auditData)
    return response.data
  } catch (error) {
    throw error.response.data
  }
}

// 废弃已生效词根
export const discardRootWord = async (wordId) => {
  try {
    const response = await axios.post(`/api/root-word/discard/${wordId}`)
    return response.data
  } catch (error) {
    throw error.response.data
  }
}

// 强制删除词根
export const forceDeleteRootWord = async (wordId) => {
  try {
    const response = await axios.delete(`/api/root-word/force-delete/${wordId}`)
    return response.data
  } catch (error) {
    throw error.response.data
  }
}

// 词根列表查询
export const listRootWord = async (queryData) => {
  try {
    const response = await axios.post('/api/root-word/list', queryData)
    return response.data
  } catch (error) {
    throw error.response.data
  }
}

// 恢复废弃词根
export const recoverRootWord = async (wordId) => {
  try {
    const response = await axios.post(`/api/root-word/recover/${wordId}`)
    return response.data
  } catch (error) {
    throw error.response.data
  }
}

// 编辑词根（管理员）
export const updateRootWord = async (updateData) => {
  try {
    const response = await axios.put('/api/root-word/update', updateData)
    return response.data
  } catch (error) {
    throw error.response.data
  }
}
