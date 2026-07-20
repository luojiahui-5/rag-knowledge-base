import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI } from '../api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(sessionStorage.getItem('token') || '')

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  async function login(username, password) {
    const { data } = await authAPI.login(username, password)
    token.value = data.access_token
    user.value = data.user
    sessionStorage.setItem('token', data.access_token)
    sessionStorage.setItem('auth', '1')
    sessionStorage.setItem('role', data.user.role)
    return data
  }

  async function fetchUser() {
    if (!token.value) return
    try {
      const { data } = await authAPI.getMe()
      user.value = data
    } catch {
      logout()
    }
  }

  function logout() {
    token.value = ''
    user.value = null
    sessionStorage.removeItem('token')
    sessionStorage.removeItem('auth')
  }

  return { user, token, isLoggedIn, isAdmin, login, fetchUser, logout }
})
