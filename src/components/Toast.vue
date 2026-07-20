<template>
  <Teleport to="body">
    <div class="toast-container">
      <transition-group name="toast">
        <div
          v-for="t in toasts"
          :key="t.id"
          :class="['toast-item', t.type]"
        >
          <span class="toast-msg">{{ t.message }}</span>
          <button class="toast-close" @click="remove(t.id)">&times;</button>
        </div>
      </transition-group>
    </div>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue'

const toasts = ref([])
let _id = 0

const add = (message, type = 'info', duration = 3000) => {
  const id = ++_id
  toasts.value.push({ id, message, type })
  if (duration > 0) setTimeout(() => remove(id), duration)
}

const remove = (id) => {
  toasts.value = toasts.value.filter(t => t.id !== id)
}

const success = (msg) => add(msg, 'success')
const error = (msg) => add(msg, 'error', 5000)
const info = (msg) => add(msg, 'info')

defineExpose({ success, error, info })
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.toast-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  border-radius: 10px;
  font-size: 13px;
  min-width: 260px;
  backdrop-filter: blur(12px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
  animation: slideIn 0.25s ease;
}

.toast-item.success { background: rgba(34, 197, 94, 0.15); border: 1px solid rgba(34, 197, 94, 0.3); color: #4ade80; }
.toast-item.error { background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.3); color: #f87171; }
.toast-item.info { background: rgba(74, 140, 247, 0.15); border: 1px solid rgba(74, 140, 247, 0.3); color: #8bb8ff; }

.toast-msg { flex: 1; }

.toast-close {
  background: none; border: none;
  color: inherit; opacity: 0.5;
  font-size: 18px; cursor: pointer;
  line-height: 1; padding: 0;
}

.toast-close:hover { opacity: 1; }

.toast-enter-active { transition: all 0.3s ease; }
.toast-leave-active { transition: all 0.2s ease; }
.toast-enter-from { opacity: 0; transform: translateX(40px); }
.toast-leave-to { opacity: 0; transform: translateX(40px); }

@keyframes slideIn {
  from { opacity: 0; transform: translateX(40px); }
  to { opacity: 1; transform: translateX(0); }
}
</style>
