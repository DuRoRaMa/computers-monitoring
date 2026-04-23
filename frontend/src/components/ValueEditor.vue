<template>
  <div class="value-editor">
    <div v-if="!forcedMode" class="mode-row">
      <button
        v-if="allowEmpty"
        type="button"
        class="mode-btn"
        :class="{ active: currentValue.mode === 'empty' }"
        @click="setMode('empty')"
      >
        Пусто
      </button>

      <button
        type="button"
        class="mode-btn"
        :class="{ active: currentValue.mode === 'range' }"
        @click="setMode('range')"
      >
        Диапазон
      </button>

      <button
        type="button"
        class="mode-btn"
        :class="{ active: currentValue.mode === 'scalar' }"
        @click="setMode('scalar')"
      >
        Текст
      </button>
    </div>

    <div v-if="currentValue.mode === 'empty'" class="empty-box">
      Значение не задано
    </div>

    <div v-else-if="currentValue.mode === 'scalar'">
      <input
        :value="currentValue.scalar"
        class="editor-input"
        :class="{ invalid: showErrors && validation.fields?.scalar }"
        type="text"
        placeholder="Введите текстовое значение"
        @input="updateField('scalar', $event.target.value)"
      />
    </div>

    <div v-else class="range-box">
      <select
        class="bracket-select"
        :class="{ invalid: showErrors && (validation.fields?.min || validation.fields?.max) }"
        :value="currentValue.minInclusive ? '[' : '('"
        @change="updateField('minInclusive', $event.target.value === '[')"
      >
        <option value="[">[</option>
        <option value="(">(</option>
      </select>

      <input
        :value="currentValue.min"
        class="editor-input"
        :class="{ invalid: showErrors && validation.fields?.min }"
        type="number"
        step="any"
        placeholder="Мин"
        @input="updateField('min', $event.target.value)"
      />

      <span class="separator">;</span>

      <input
        :value="currentValue.max"
        class="editor-input"
        :class="{ invalid: showErrors && validation.fields?.max }"
        type="number"
        step="any"
        placeholder="Макс"
        @input="updateField('max', $event.target.value)"
      />

      <select
        class="bracket-select"
        :class="{ invalid: showErrors && (validation.fields?.min || validation.fields?.max) }"
        :value="currentValue.maxInclusive ? ']' : ')'"
        @change="updateField('maxInclusive', $event.target.value === ']')"
      >
        <option value="]">]</option>
        <option value=")">)</option>
      </select>
    </div>

    <div v-if="showErrors && !validation.valid" class="error-text">
      {{ validation.message }}
    </div>
  </div>
</template>

<script setup>
import { computed, watch } from "vue";
import { createValueEditor, validateValueEditor } from "../utils/valueEditor";

const props = defineProps({
  modelValue: {
    type: Object,
    default: null,
  },
  allowEmpty: {
    type: Boolean,
    default: true,
  },
  showErrors: {
    type: Boolean,
    default: false,
  },
  forcedMode: {
    type: String,
    default: null, // null | range | scalar
  },
});

const emit = defineEmits(["update:modelValue"]);

const fallbackValue = computed(() =>
  createValueEditor(props.forcedMode || (props.allowEmpty ? "empty" : "range"))
);

const currentValue = computed(() => props.modelValue ?? fallbackValue.value);

const validation = computed(() =>
  validateValueEditor(currentValue.value, { allowEmpty: props.allowEmpty })
);

const setMode = (mode) => {
  const base = createValueEditor(mode);
  const source = currentValue.value;

  if (mode === "scalar") {
    base.scalar = source.mode === "scalar" ? source.scalar || "" : "";
  }

  if (mode === "range") {
    base.min = source.mode === "range" ? source.min || "" : "";
    base.max = source.mode === "range" ? source.max || "" : "";
    base.minInclusive = source.mode === "range" ? source.minInclusive : true;
    base.maxInclusive = source.mode === "range" ? source.maxInclusive : true;
  }

  emit("update:modelValue", base);
};

const updateField = (field, value) => {
  emit("update:modelValue", {
    ...currentValue.value,
    [field]: value,
  });
};

watch(
  () => props.forcedMode,
  (mode) => {
    if (!mode) return;

    if (currentValue.value.mode !== mode) {
      setMode(mode);
    }
  },
  { immediate: true }
);
</script>

<style scoped>
.value-editor {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.mode-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.mode-btn {
  border: 1px solid #cbd5e1;
  background: white;
  color: #334155;
  padding: 8px 12px;
  border-radius: 12px;
  font-weight: 700;
  cursor: pointer;
}

.mode-btn.active {
  background: #eff6ff;
  border-color: #60a5fa;
  color: #1d4ed8;
}

.empty-box {
  min-height: 46px;
  display: flex;
  align-items: center;
  padding: 0 14px;
  border: 1px dashed #cbd5e1;
  border-radius: 14px;
  color: #64748b;
  background: #f8fafc;
}

.range-box {
  display: grid;
  grid-template-columns: 72px 1fr 24px 1fr 72px;
  gap: 8px;
  align-items: center;
}

.editor-input,
.bracket-select {
  min-height: 44px;
  border: 1px solid #cbd5e1;
  border-radius: 12px;
  padding: 0 12px;
  font-size: 14px;
  background: white;
  transition: border-color 0.2s ease, background 0.2s ease;
}

.editor-input.invalid,
.bracket-select.invalid {
  border-color: #ef4444;
  background: #fef2f2;
}

.separator {
  text-align: center;
  font-weight: 800;
  color: #64748b;
}

.error-text {
  color: #dc2626;
  font-size: 13px;
  font-weight: 700;
}

@media (max-width: 700px) {
  .range-box {
    grid-template-columns: 1fr;
  }

  .separator {
    display: none;
  }
}
</style>