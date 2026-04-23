<template>
  <article class="news-card click-effect" @click="goToDetail">
    <div class="news-main">
      <p class="news-badge">即时资讯</p>
      <h3 class="news-title">{{ news.title }}</h3>
      <p v-if="news.description" class="news-desc">{{ news.description }}</p>
      <div class="news-meta">
        <span>{{ news.author || 'NewsCopilot' }}</span>
        <span>{{ publishTime }}</span>
        <span>{{ viewCount }} 阅读</span>
      </div>
    </div>

    <div class="news-cover" :class="{ 'is-placeholder': !news.image }">
      <img
        v-if="news.image"
        :src="news.image"
        :alt="news.title"
      >
      <span v-else>NEWS</span>
    </div>
  </article>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'

import { formatPublishTime, formatViewCount } from '../utils/news'


const props = defineProps({
  news: {
    type: Object,
    required: true,
  },
})

const router = useRouter()

const publishTime = computed(() => formatPublishTime(props.news.publishTime))
const viewCount = computed(() => formatViewCount(props.news.views))

const goToDetail = () => {
  router.push(`/news/detail/${props.news.id}`)
}
</script>

<style scoped>
.news-card {
  display: flex;
  gap: 14px;
  padding: 16px;
  margin-bottom: 12px;
  border-radius: 18px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.98) 0%, rgba(249, 250, 252, 0.98) 100%);
  box-shadow: 0 10px 28px rgba(15, 23, 42, 0.06);
}

.news-main {
  flex: 1;
  min-width: 0;
}

.news-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 999px;
  margin-bottom: 10px;
  background: rgba(183, 28, 28, 0.08);
  color: #b71c1c;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.news-title {
  margin: 0 0 10px;
  color: #131a28;
  font-size: 17px;
  line-height: 1.5;
  font-weight: 700;
  display: -webkit-box;
  overflow: hidden;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.news-desc {
  margin: 0 0 12px;
  color: #5f6b7a;
  font-size: 13px;
  line-height: 1.6;
  display: -webkit-box;
  overflow: hidden;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.news-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 12px;
  color: #7b8794;
  font-size: 12px;
}

.news-cover {
  width: 112px;
  height: 112px;
  flex-shrink: 0;
  overflow: hidden;
  border-radius: 16px;
  background: #e6ebf2;
}

.news-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.news-cover.is-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  background:
    radial-gradient(circle at top, rgba(182, 28, 28, 0.18), transparent 55%),
    linear-gradient(135deg, #dde4ee 0%, #f5f7fb 100%);
  color: #5d6b7d;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.12em;
}
</style>

