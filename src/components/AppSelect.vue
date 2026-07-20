<template>
  <div class="app-select" :class="{ open: show, disabled }" ref="el" tabindex="0" @blur="onBlur">
    <div class="select-trigger" @click="show = !show">
      <span class="select-value" :class="{ placeholder: !selectedLabel }">{{ selectedLabel || placeholder }}</span>
      <svg viewBox="0 0 16 16" fill="none" class="select-arrow" :class="{ rotated: show }">
        <path d="M4 6l4 4 4-4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </div>
    <transition name="drop">
      <div v-if="show" class="select-dropdown">
        <div
          v-for="opt in options"
          :key="opt.value"
          :class="['select-option', { active: modelValue === opt.value, disabled: opt.disabled }]"
          @click.stop="select(opt)"
        >
          <span>{{ opt.label }}</span>
          <svg v-if="modelValue === opt.value" viewBox="0 0 16 16" fill="none" class="select-check">
            <path d="M3 8l3 3 7-7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  modelValue: [String, Number],
  options: { type: Array, default: () => [] },
  placeholder: { type: String, default: '请选择' },
  disabled: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue', 'change'])
const show = ref(false)
const el = ref(null)

const selectedLabel = computed(() => {
  const opt = props.options.find(o => o.value === props.modelValue)
  return opt ? opt.label : null
})

const select = (opt) => {
  if (opt.disabled || props.disabled) return
  emit('update:modelValue', opt.value)
  emit('change', opt.value)
  show.value = false
}

const onBlur = (e) => {
  // 延迟关闭，让点击事件先执行
  setTimeout(() => {
    if (el.value && !el.value.contains(document.activeElement)) {
      show.value = false
    }
  }, 150)
}

watch(() => props.options, () => { show.value = false })
</script>

<style scoped>
.app-select {
  position: relative;
  width: 100%;
  outline: none;
  font-size: 13px;
  user-select: none;
}
.app-select.disabled { opacity: 0.4; pointer-events: none; }

.select-trigger {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  height: 38px;
  padding: 0 12px;
  background: rgba(255,255,255,.04);
  border: 1px solid rgba(255,255,255,.08);
  border-radius: 8px;
  cursor: pointer;
  transition: border-color .2s, box-shadow .2s;
}
.app-select.open .select-trigger,
.select-trigger:hover { border-color: rgba(255,255,255,.14); }
.app-select.open .select-trigger {
  border-color: rgba(74,140,247,.4);
  box-shadow: 0 0 0 3px rgba(74,140,247,.06);
}
.select-value {
  color: #e2e8f0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.select-value.placeholder {
  color: rgba(255,255,255,.25);
}
.select-arrow {
  width: 14px;
  height: 14px;
  color: rgba(255,255,255,.3);
  flex-shrink: 0;
  transition: transform .2s;
}
.select-arrow.rotated {
  transform: rotate(180deg);
}

.select-dropdown {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  background: #141e3a;
  border: 1px solid rgba(255,255,255,.08);
  border-radius: 10px;
  padding: 4px;
  z-index: 50;
  box-shadow: 0 12px 40px rgba(0,0,0,.5);
  max-height: 220px;
  overflow-y: auto;
}
.select-dropdown::-webkit-scrollbar { width: 3px; }
.select-dropdown::-webkit-scrollbar-thumb { background: rgba(255,255,255,.08); border-radius: 2px; }

.select-option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 10px;
  border-radius: 6px;
  color: rgba(255,255,255,.55);
  cursor: pointer;
  transition: all .12s;
  font-size: 13px;
}
.select-option:hover { background: rgba(255,255,255,.05); color: rgba(255,255,255,.8); }
.select-option.active { color: #8bb8ff; background: rgba(74,140,247,.08); }
.select-option.disabled { color: rgba(255,255,255,.15); cursor: default; }
.select-check { width: 14px; height: 14px; color: #8bb8ff; flex-shrink: 0; }

/* 过渡动画 */
.drop-enter-active { transition: all .15s ease; }
.drop-leave-active { transition: all .1s ease; }
.drop-enter-from { opacity: 0; transform: translateY(-6px); }
.drop-leave-to { opacity: 0; transform: translateY(-4px); }
</style>
