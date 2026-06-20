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

export default apiClient
