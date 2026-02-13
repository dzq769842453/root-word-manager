<template>
  <div class="root-word-apply">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>申请词根</span>
        </div>
      </template>
      
      <el-form
        ref="applyFormRef"
        :model="applyForm"
        :rules="applyRules"
        label-width="120px"
        class="apply-form"
      >
        <el-form-item label="词根名称" prop="word_name">
          <el-input v-model="applyForm.word_name" placeholder="请输入词根名称" />
        </el-form-item>
        <el-form-item label="MySQL 数据类型" prop="mysql_type">
          <el-input v-model="applyForm.mysql_type" placeholder="请输入 MySQL 数据类型，如：bigint、varchar(32)" />
        </el-form-item>
        <el-form-item label="Doris 数据类型" prop="doris_type">
          <el-input v-model="applyForm.doris_type" placeholder="请输入 Doris 数据类型，如：bigint、varchar(32)" />
        </el-form-item>
        <el-form-item label="ClickHouse 数据类型" prop="clickhouse_type">
          <el-input v-model="applyForm.clickhouse_type" placeholder="请输入 ClickHouse 数据类型，如：UInt64、String" />
        </el-form-item>
        <el-form-item label="词根注释" prop="remark">
          <el-input v-model="applyForm.remark" placeholder="请输入词根注释，如：图书 ID" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleApply">提交申请</el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { applyRootWord } from '../api/rootWord'

export default {
  name: 'RootWordApply',
  setup() {
    const router = useRouter()
    const applyForm = ref({
      word_name: '',
      mysql_type: '',
      doris_type: '',
      clickhouse_type: '',
      remark: ''
    })
    const applyRules = ref({
      word_name: [{ required: true, message: '请输入词根名称', trigger: 'blur' }],
      mysql_type: [{ required: true, message: '请输入 MySQL 数据类型', trigger: 'blur' }],
      doris_type: [{ required: true, message: '请输入 Doris 数据类型', trigger: 'blur' }],
      clickhouse_type: [{ required: true, message: '请输入 ClickHouse 数据类型', trigger: 'blur' }]
    })
    const applyFormRef = ref(null)
    
    // 处理提交申请
    const handleApply = async () => {
      try {
        // 表单验证
        await applyFormRef.value.validate()
        
        // 调用申请接口
        const response = await applyRootWord(applyForm.value)
        
        // 提示成功
        ElMessage.success('词根申请提交成功，请等待审核')
        
        // 重置表单
        resetForm()
        
        // 跳转到词根列表页面
        router.push('/root-word/list')
      } catch (error) {
        // 处理错误
        if (error.msg) {
          ElMessage.error(error.msg)
        } else {
          ElMessage.error('词根申请提交失败')
        }
      }
    }
    
    // 重置表单
    const resetForm = () => {
      applyForm.value = {
        word_name: '',
        mysql_type: '',
        doris_type: '',
        clickhouse_type: '',
        remark: ''
      }
      if (applyFormRef.value) {
        applyFormRef.value.resetFields()
      }
    }
    
    return {
      applyForm,
      applyRules,
      applyFormRef,
      handleApply,
      resetForm
    }
  }
}
</script>

<style scoped>
.root-word-apply {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.apply-form {
  max-width: 600px;
  width: 100%;
}

/* 响应式样式 */
@media screen and (max-width: 768px) {
  .root-word-apply {
    padding: 10px;
  }
  
  .apply-form {
    max-width: 100%;
  }
  
  .el-form-item {
    margin-bottom: 15px;
  }
  
  .el-form-item__label {
    font-size: 14px;
  }
  
  .el-input {
    font-size: 14px;
  }
  
  .el-button {
    font-size: 14px;
    padding: 8px 16px;
  }
}

@media screen and (max-width: 480px) {
  .el-form {
    label-width: 100px;
  }
  
  .el-form-item__label {
    font-size: 13px;
  }
  
  .el-input {
    font-size: 13px;
  }
  
  .el-button {
    font-size: 13px;
    padding: 6px 12px;
  }
}

/* 确保表单在移动设备上可以滚动 */
@media screen and (max-height: 600px) {
  .root-word-apply {
    overflow-y: auto;
    max-height: calc(100vh - 60px);
  }
}
</style>
