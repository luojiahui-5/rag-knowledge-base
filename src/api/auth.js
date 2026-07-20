import api from './index'

export const authAPI = {
  login(username, password) {
    return api.post('/auth/login', { username, password })
  },

  register(data) {
    return api.post('/auth/register', data)
  },

  getMe() {
    return api.get('/auth/me')
  },
}
