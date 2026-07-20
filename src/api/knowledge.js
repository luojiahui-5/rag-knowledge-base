import api from './index'

export const kbAPI = {
  list() {
    return api.get('/knowledge')
  },

  get(id) {
    return api.get(`/knowledge/${id}`)
  },

  create(data) {
    return api.post('/knowledge', data)
  },

  update(id, data) {
    return api.put(`/knowledge/${id}`, data)
  },

  remove(id) {
    return api.delete(`/knowledge/${id}`)
  },
}

export const docAPI = {
  list(params = {}) {
    return api.get('/documents', { params })
  },

  get(id) {
    return api.get(`/documents/${id}`)
  },

  upload(kbId, file) {
    const form = new FormData()
    form.append('kb_id', kbId)
    form.append('file', file)
    return api.post('/documents/upload', form)
  },

  remove(id) {
    return api.delete(`/documents/${id}`)
  },
}

export const searchAPI = {
  search(query, kbIds = null, topK = 5) {
    return api.post('/search', { query, kb_ids: kbIds, top_k: topK })
  },
}

export const dashboardAPI = {
  stats() {
    return api.get('/dashboard/stats')
  },
}
