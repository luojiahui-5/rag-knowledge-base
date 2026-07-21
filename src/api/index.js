import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 120000,
})

// 请求拦截器：自动附加 token
api.interceptors.request.use((config) => {
  const token = sessionStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  // 只有非 FormData 请求才设 JSON Content-Type
  if (!(config.data instanceof FormData)) {
    config.headers['Content-Type'] = 'application/json'
  }
  return config
})

// 响应拦截器：401 时跳转登录
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      sessionStorage.removeItem('token')
      sessionStorage.removeItem('auth')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  },
)

export default api
