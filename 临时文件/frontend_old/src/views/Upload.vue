<template>
  <div class="upload-page">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <el-icon><Upload /></el-icon>
              <span>数据文件上传</span>
            </div>
          </template>
          
          <el-upload
            class="upload-dragger"
            drag
            :action="uploadUrl"
            :on-success="handleSuccess"
            :on-error="handleError"
            :before-upload="beforeUpload"
            :file-list="fileList"
            :auto-upload="false"
            ref="uploadRef"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              将文件拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                支持 .xlsx, .xls, .csv 格式文件，文件大小不超过10MB
              </div>
            </template>
          </el-upload>

          <el-space style="margin-top: 20px;" v-if="fileList.length > 0">
            <el-button type="primary" @click="submitUpload" :loading="uploading">
              <el-icon><Upload /></el-icon>
              开始上传
            </el-button>
            <el-button @click="clearFiles">清空文件</el-button>
          </el-space>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;" v-if="uploadedFiles.length > 0">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <el-icon><Files /></el-icon>
              <span>已上传文件</span>
            </div>
          </template>
          
          <el-table :data="uploadedFiles" style="width: 100%">
            <el-table-column prop="filename" label="文件名" width="300"></el-table-column>
            <el-table-column prop="upload_time" label="上传时间" width="200"></el-table-column>
            <el-table-column prop="file_size" label="文件大小" width="120"></el-table-column>
            <el-table-column prop="rows" label="数据行数" width="100"></el-table-column>
            <el-table-column prop="columns" label="列数" width="100"></el-table-column>
            <el-table-column label="操作" min-width="200">
              <template #default="scope">
                <el-space>
                  <el-button type="primary" size="small" @click="previewFile(scope.row)">
                    预览
                  </el-button>
                  <el-button type="success" size="small" @click="analyzeFile(scope.row)">
                    分析
                  </el-button>
                  <el-button type="danger" size="small" @click="deleteFile(scope.row)">
                    删除
                  </el-button>
                </el-space>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- 文件预览对话框 -->
    <el-dialog v-model="previewVisible" title="文件预览" width="80%" draggable>
      <el-table :data="previewData" style="width: 100%" max-height="400">
        <el-table-column
          v-for="column in previewColumns"
          :key="column"
          :prop="column"
          :label="column"
          :width="120"
        >
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="previewVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import axios from 'axios'
import { Upload, UploadFilled, Files } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

export default {
  name: 'Upload',
  components: {
    Upload,
    UploadFilled,
    Files
  },
  data() {
    return {
      uploadUrl: '/api/files/upload',
      fileList: [],
      uploading: false,
      uploadedFiles: [],
      previewVisible: false,
      previewData: [],
      previewColumns: []
    }
  },
  methods: {
    beforeUpload(file) {
      const isValidType = file.type === 'application/vnd.ms-excel' || 
                         file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' ||
                         file.type === 'text/csv' ||
                         file.name.endsWith('.xlsx') ||
                         file.name.endsWith('.xls') ||
                         file.name.endsWith('.csv')
      
      const isLt10M = file.size / 1024 / 1024 < 10

      if (!isValidType) {
        ElMessage.error('只能上传 Excel 或 CSV 文件!')
        return false
      }
      if (!isLt10M) {
        ElMessage.error('文件大小不能超过 10MB!')
        return false
      }
      return true
    },
    
    submitUpload() {
      this.uploading = true
      this.$refs.uploadRef.submit()
    },
    
    handleSuccess(response, file) {
      this.uploading = false
      ElMessage.success(`文件 ${file.name} 上传成功!`)
      this.loadUploadedFiles()
      this.fileList = []
    },
    
    handleError(error, file) {
      this.uploading = false
      console.error('Upload error:', error)
      ElMessage.error(`文件 ${file.name} 上传失败!`)
    },
    
    clearFiles() {
      this.fileList = []
      this.$refs.uploadRef.clearFiles()
    },
    
    async loadUploadedFiles() {
      try {
        const response = await axios.get('/api/files/list')
        this.uploadedFiles = response.data.files || []
      } catch (error) {
        console.error('Failed to load files:', error)
        ElMessage.error('加载文件列表失败')
      }
    },
    
    async previewFile(file) {
      try {
        const response = await axios.get(`/api/files/preview/${file.id}`)
        this.previewData = response.data.data || []
        this.previewColumns = response.data.columns || []
        this.previewVisible = true
      } catch (error) {
        console.error('Preview error:', error)
        ElMessage.error('预览文件失败')
      }
    },
    
    analyzeFile(file) {
      this.$router.push({
        path: '/analysis',
        query: { fileId: file.id, filename: file.filename }
      })
    },
    
    async deleteFile(file) {
      try {
        await ElMessageBox.confirm(
          `确定要删除文件 "${file.filename}" 吗？`,
          '确认删除',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning',
          }
        )
        
        await axios.delete(`/api/files/delete/${file.id}`)
        ElMessage.success('文件删除成功')
        this.loadUploadedFiles()
      } catch (error) {
        if (error !== 'cancel') {
          console.error('Delete error:', error)
          ElMessage.error('删除文件失败')
        }
      }
    }
  },
  
  mounted() {
    this.loadUploadedFiles()
  }
}
</script>

<style scoped>
.upload-page {
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.upload-dragger {
  width: 100%;
}

.el-upload-dragger {
  width: 100%;
}

.el-table {
  margin-top: 20px;
}
</style> 