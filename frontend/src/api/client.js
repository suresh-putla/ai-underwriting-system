import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const authenticateUser = async (username, password) => {
  try {
    const response = await apiClient.post('/user-auth', {
      username,
      password,
    })
    return response.data
  } catch (error) {
    throw error.response?.data || { error: 'Authentication failed' }
  }
}

// Admin table API functions
export const getAdminTables = async () => {
  const response = await apiClient.get('/admin/tables')
  return response.data
}

export const getTableSchema = async (tableName) => {
  const response = await apiClient.get(`/admin/tables/${tableName}/schema`)
  return response.data
}

export const getTableRows = async (tableName) => {
  const response = await apiClient.get(`/admin/tables/${tableName}/rows`)
  return response.data
}

export const createTableRow = async (tableName, rowData) => {
  const response = await apiClient.post(`/admin/tables/${tableName}/rows`, rowData)
  return response.data
}

export const deleteTableRow = async (tableName, primaryKey) => {
  const response = await apiClient.delete(`/admin/tables/${tableName}/rows`, {
    data: { primary_key: primaryKey }
  })
  return response.data
}

// Borrower API functions
export const getSubmittedDocs = async (userId) => {
  try {
    const response = await apiClient.get('/submitted-docs', {
      params: { user_id: userId }
    })
    return response.data
  } catch (error) {
    console.error('Error fetching submitted docs:', error)
    throw error.response?.data || { error: 'Failed to fetch documents' }
  }
}

export const updateDocumentStatus = async (userId, docType, status) => {
  try {
    const response = await apiClient.put('/document-status', {
      user_id: userId,
      doc_type: docType,
      status: status
    })
    return response.data
  } catch (error) {
    console.error('Error updating document status:', error)
    throw error.response?.data || { error: 'Failed to update document status' }
  }
}

export default apiClient
