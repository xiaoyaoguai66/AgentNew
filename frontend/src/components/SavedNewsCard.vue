<template>
  <article class="saved-card click-effect" @click="emit('select', news.id)">
    <div class="saved-cover" :class="{ placeholder: !news.image }">
      <img v-if="news.image" :src="news.image" :alt="news.title">
      <span v-else>NEWS</span>
    </div>

    <div class="saved-body">
      <div class="saved-head">
        <span class="saved-tag">{{ secondaryLabel }}</span>
        <button
          v-if="showAction"
          type="button"
          class="saved-action"
          @click.stop="emit('action', news.id)"
        >
          {{ actionText }}
        </button>
      </div>

      <h3 class="saved-title">{{ news.title }}</h3>
      <p v-if="news.description" class="saved-desc">{{ news.description }}</p>

      <div class="saved-meta">
        <span>{{ news.author || 'AgentNews' }}</span>
        <span>{{ publishTime }}</span>
        <span>{{ viewCount }} 阅读</span>
      </div>

      <p v-if="secondaryValue" class="saved-secondary">
        {{ secondaryLabel }}：{{ secondaryValue }}
      </p>
    </div>
  </article>
</template>

<script setup>
import { computed } from 'vue'

import { formatPublishTime, formatViewCount } from '../utils/news'


const props = defineProps({
  news: {
    type: Object,
    required: true,
  },
  secondaryLabel: {
    type: String,
    default: '记录时间',
  },
  secondaryValue: {
    type: String,
    default: '',
  },
  actionText: {
    type: String,
    default: '移除',
  },
  showAction: {
    type: Boolean,
    default: true,
  },
})

const emit = defineEmits(['select', 'action'])

const publishTime = computed(() => formatPublishTime(props.news.publishTime))
const viewCount = computed(() => formatViewCount(props.news.views))
</script>

<style scoped>
.saved-card {
  display: flex;
  gap: 14px;
  padding: 14px;
  border-radius: 20px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.98) 0%, rgba(249, 250, 252, 0.98) 100%);
  box-shadow: 0 14px 34px rgba(15, 23, 42, 0.06);
}

.saved-cover {
  width: 104px;
  height: 104px;
  flex-shrink: 0;
  overflow: hidden;
  border-radius: 16px;
  background: #e6ebf2;
}

.saved-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.saved-cover.placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  background:
    radial-gradient(circle at top, rgba(183, 28, 28, 0.16), transparent 56%),
    linear-gradient(135deg, #dde4ee 0%, #f5f7fb 100%);
  color: #64748b;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.1em;
}

.saved-body {
  flex: 1;
  min-width: 0;
}

.saved-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 10px;
}

.saved-tag {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(183, 28, 28, 0.09);
  color: #b71c1c;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.05em;
}

.saved-action {
  border: 0;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.08);
  color: #475569;
  padding: 6px 10px;
  font-size: 12px;
  font-weight: 600;
}

.saved-title {
  margin: 0 0 8px;
  color: #0f172a;
  font-size: 16px;
  line-height: 1.5;
  font-weight: 700;
  display: -webkit-box;
  overflow: hidden;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.saved-desc {
  margin: 0 0 10px;
  color: #5b6472;
  font-size: 13px;
  line-height: 1.6;
  display: -webkit-box;
  overflow: hidden;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.saved-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 12px;
  color: #7b8794;
  font-size: 12px;
}

.saved-secondary {
  margin: 10px 0 0;
  color: #475569;
  font-size: 12px;
  line-height: 1.5;
}
</style>
