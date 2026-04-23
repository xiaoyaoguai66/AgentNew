<template>
  <div class="news-detail-page">
    <van-nav-bar
      title="新闻详情"
      left-text="返回"
      left-arrow
      fixed
      @click-left="onClickLeft"
    />

    <div class="detail-shell">
      <section v-if="newsStore.detailLoading" class="detail-card">
        <div class="detail-skeleton-title skeleton" />
        <div class="detail-skeleton-meta skeleton" />
        <div class="detail-skeleton-cover skeleton" />
        <div class="detail-skeleton-paragraph skeleton" />
        <div class="detail-skeleton-paragraph skeleton short" />
        <div class="detail-skeleton-paragraph skeleton" />
      </section>

      <section v-else-if="newsStore.detailError" class="detail-card error-panel">
        <h2>新闻加载失败</h2>
        <p>{{ newsStore.detailError }}</p>
        <button type="button" class="primary-button" @click="loadNewsDetail(newsId)">
          重新加载
        </button>
      </section>

      <template v-else-if="newsDetail.id">
        <section class="detail-card hero-card">
          <div class="eyebrow-row">
            <span class="category-pill">{{ categoryLabel }}</span>
            <button
              type="button"
              class="favorite-button"
              :class="{ active: isFavorite }"
              @click="toggleFavorite"
            >
              {{ isFavorite ? '已收藏' : '收藏' }}
            </button>
          </div>

          <h1 class="detail-title">{{ newsDetail.title }}</h1>
          <p v-if="newsDetail.description" class="detail-summary">
            {{ newsDetail.description }}
          </p>

          <div class="meta-grid">
            <div class="meta-chip">
              <span class="meta-label">作者</span>
              <span class="meta-value">{{ newsDetail.author || 'NewsCopilot' }}</span>
            </div>
            <div class="meta-chip">
              <span class="meta-label">发布时间</span>
              <span class="meta-value">{{ publishTime }}</span>
            </div>
            <div class="meta-chip">
              <span class="meta-label">阅读量</span>
              <span class="meta-value">{{ viewCount }}</span>
            </div>
          </div>
        </section>

        <section v-if="newsDetail.image" class="detail-card cover-card">
          <img class="detail-cover" :src="newsDetail.image" :alt="newsDetail.title">
        </section>

        <section class="detail-card article-card">
          <div class="section-header">
            <p class="section-eyebrow">正文阅读</p>
            <h2>报道内容</h2>
          </div>

          <div class="article-content">
            <p v-for="(paragraph, index) in contentParagraphs" :key="index">
              {{ paragraph }}
            </p>
          </div>
        </section>

        <section class="detail-card insight-card">
          <p class="section-eyebrow">来源延展</p>
          <h2>作为新闻 Agent 的可引用来源</h2>
          <p class="insight-copy">
            当前详情页已经接入真实浏览量、相关推荐与收藏状态。后续接 Agent 时，这一页可以继续扩展成“回答来源展示页”，承接证据片段、引用链接和相关新闻链路。
          </p>
        </section>

        <section v-if="relatedNews.length" class="detail-card related-card">
          <div class="section-header">
            <p class="section-eyebrow">继续阅读</p>
            <h2>相关推荐</h2>
          </div>

          <div class="related-list">
            <button
              v-for="item in relatedNews"
              :key="item.id"
              type="button"
              class="related-item click-effect"
              @click="goToRelatedNews(item.id)"
            >
              <div class="related-image" :class="{ placeholder: !item.image }">
                <img v-if="item.image" :src="item.image" :alt="item.title">
                <span v-else>NEWS</span>
              </div>
              <div class="related-body">
                <p class="related-title">{{ item.title }}</p>
                <div class="related-meta">
                  <span>{{ formatPublishTime(item.publishTime) }}</span>
                  <span>{{ formatViewCount(item.views) }} 阅读</span>
                </div>
              </div>
            </button>
          </div>
        </section>
      </template>

      <section v-else class="detail-card">
        <van-empty description="暂无新闻内容" />
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast } from 'vant'

import { useFavoriteStore } from '../store/modules/favorite'
import { useHistoryStore } from '../store/modules/history'
import { useNewsStore } from '../store/modules/news'
import { useUserStore } from '../store/user'
import { formatPublishTime, formatViewCount } from '../utils/news'


const route = useRoute()
const router = useRouter()
const newsStore = useNewsStore()
const historyStore = useHistoryStore()
const favoriteStore = useFavoriteStore()
const userStore = useUserStore()

const newsId = computed(() => Number(route.params.id || 0))
const newsDetail = computed(() => newsStore.newsDetail || {})
const relatedNews = computed(() => newsDetail.value.relatedNews || [])
const categoryLabel = computed(() => newsStore.getCategoryName(newsDetail.value.categoryId) || '新闻')
const publishTime = computed(() => formatPublishTime(newsDetail.value.publishTime))
const viewCount = computed(() => `${formatViewCount(newsDetail.value.views)} 阅读`)

const contentParagraphs = computed(() => {
  const content = newsDetail.value.content || ''
  if (!content) {
    return []
  }

  const paragraphs = content
    .split(/\n+/)
    .map((item) => item.trim())
    .filter(Boolean)

  return paragraphs.length ? paragraphs : [content]
})

const isFavorite = computed(() => favoriteStore.isFavorite(newsId.value))

function onClickLeft() {
  router.back()
}

async function syncHistoryRecord() {
  if (!userStore.getLoginStatus || !newsDetail.value.id) {
    return
  }

  try {
    await historyStore.addHistoryApi(newsDetail.value.id)
  } catch (error) {
    console.error('记录浏览历史失败:', error)
  }
}

async function syncFavoriteStatus() {
  favoriteStore.loadFavorites()

  if (!userStore.getLoginStatus || !newsDetail.value.id) {
    return
  }

  const result = await favoriteStore.checkFavoriteStatusApi(newsDetail.value.id)
  if (!result?.success || result.isLocal) {
    return
  }

  if (result.isFavorite && !favoriteStore.isFavorite(newsDetail.value.id)) {
    favoriteStore.addFavorite(newsDetail.value)
    return
  }

  if (!result.isFavorite && favoriteStore.isFavorite(newsDetail.value.id)) {
    favoriteStore.removeFavorite(newsDetail.value.id)
  }
}

async function loadNewsDetail(targetId) {
  if (!targetId) {
    return
  }

  try {
    await newsStore.getNewsDetail(targetId)
    window.scrollTo({ top: 0, behavior: 'auto' })
    await syncHistoryRecord()
    await syncFavoriteStatus()
  } catch (error) {
    console.error('新闻详情加载失败:', error)
  }
}

async function toggleFavorite() {
  if (!newsDetail.value.id) {
    return
  }

  if (!userStore.getLoginStatus) {
    showToast({
      message: '请先登录后再收藏',
      position: 'bottom',
    })
    router.push('/login')
    return
  }

  const status = await favoriteStore.toggleFavorite(newsDetail.value)

  if (status === true) {
    showToast({
      message: '已添加到收藏',
      position: 'bottom',
    })
    return
  }

  if (status === false) {
    showToast({
      message: '已取消收藏',
      position: 'bottom',
    })
    return
  }

  showToast({
    message: '操作失败，请稍后重试',
    position: 'bottom',
  })
}

function goToRelatedNews(id) {
  if (!id || id === newsId.value) {
    return
  }

  router.push(`/news/detail/${id}`)
}

onMounted(async () => {
  favoriteStore.loadFavorites()
  await loadNewsDetail(newsId.value)
})

watch(
  () => route.params.id,
  async (value, oldValue) => {
    if (!value || value === oldValue) {
      return
    }

    await loadNewsDetail(Number(value))
  },
)
</script>

<style scoped>
.news-detail-page {
  min-height: 100vh;
  padding-top: 46px;
  background:
    radial-gradient(circle at top, rgba(183, 28, 28, 0.08), transparent 28%),
    linear-gradient(180deg, #f5f7fb 0%, #eef2f8 100%);
}

.detail-shell {
  padding: 16px 16px 32px;
}

.detail-card {
  margin-bottom: 16px;
  padding: 18px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 18px 40px rgba(15, 23, 42, 0.08);
}

.hero-card {
  background:
    radial-gradient(circle at top right, rgba(183, 28, 28, 0.12), transparent 36%),
    linear-gradient(180deg, rgba(255, 250, 249, 0.98) 0%, rgba(255, 255, 255, 0.98) 100%);
}

.eyebrow-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}

.category-pill {
  display: inline-flex;
  align-items: center;
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(183, 28, 28, 0.09);
  color: #b71c1c;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.06em;
}

.favorite-button,
.primary-button {
  padding: 9px 14px;
  border: 0;
  border-radius: 999px;
  background: #111827;
  color: #fff;
  font-size: 13px;
  font-weight: 600;
}

.favorite-button.active {
  background: #b71c1c;
}

.detail-title {
  margin: 0;
  color: #111827;
  font-size: 28px;
  line-height: 1.42;
  font-weight: 800;
}

.detail-summary {
  margin: 14px 0 0;
  color: #5d6776;
  font-size: 15px;
  line-height: 1.8;
}

.meta-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  margin-top: 18px;
}

.meta-chip {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 12px;
  border-radius: 18px;
  background: rgba(248, 250, 252, 0.92);
}

.meta-label {
  color: #7b8794;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.meta-value {
  color: #111827;
  font-size: 13px;
  line-height: 1.5;
}

.cover-card {
  padding: 10px;
}

.detail-cover {
  width: 100%;
  display: block;
  border-radius: 18px;
}

.section-header {
  margin-bottom: 16px;
}

.section-eyebrow {
  margin: 0 0 8px;
  color: #b71c1c;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.section-header h2 {
  margin: 0;
  color: #111827;
  font-size: 22px;
  line-height: 1.35;
}

.article-content {
  color: #1f2937;
  font-size: 17px;
  line-height: 1.95;
}

.article-content p {
  margin: 0 0 18px;
  text-align: justify;
}

.article-content p:last-child {
  margin-bottom: 0;
}

.insight-card {
  background:
    linear-gradient(135deg, rgba(15, 23, 42, 0.98) 0%, rgba(31, 41, 55, 0.98) 100%);
  color: #fff;
}

.insight-card .section-eyebrow,
.insight-card h2,
.insight-copy {
  color: inherit;
}

.insight-copy {
  margin: 0;
  color: rgba(255, 255, 255, 0.82);
  font-size: 14px;
  line-height: 1.8;
}

.related-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.related-item {
  display: flex;
  gap: 12px;
  width: 100%;
  padding: 12px;
  border: 0;
  border-radius: 18px;
  background: rgba(248, 250, 252, 0.92);
  text-align: left;
}

.related-image {
  width: 92px;
  height: 92px;
  flex-shrink: 0;
  overflow: hidden;
  border-radius: 16px;
  background: #e6ebf2;
}

.related-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.related-image.placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #5f6b7a;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.1em;
}

.related-body {
  flex: 1;
  min-width: 0;
}

.related-title {
  margin: 0 0 12px;
  color: #111827;
  font-size: 15px;
  line-height: 1.6;
  font-weight: 700;
  display: -webkit-box;
  overflow: hidden;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.related-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 12px;
  color: #7b8794;
  font-size: 12px;
}

.error-panel {
  text-align: center;
}

.error-panel h2 {
  margin: 0 0 8px;
  color: #111827;
  font-size: 22px;
}

.error-panel p {
  margin: 0 0 16px;
  color: #687588;
  font-size: 14px;
}

.detail-skeleton-title,
.detail-skeleton-meta,
.detail-skeleton-cover,
.detail-skeleton-paragraph {
  border-radius: 16px;
}

.detail-skeleton-title {
  height: 34px;
  margin-bottom: 16px;
}

.detail-skeleton-meta {
  height: 68px;
  margin-bottom: 16px;
}

.detail-skeleton-cover {
  height: 220px;
  margin-bottom: 16px;
}

.detail-skeleton-paragraph {
  height: 18px;
  margin-bottom: 12px;
}

.detail-skeleton-paragraph.short {
  width: 72%;
}

@media (max-width: 480px) {
  .meta-grid {
    grid-template-columns: 1fr;
  }

  .detail-title {
    font-size: 24px;
  }

  .article-content {
    font-size: 16px;
  }
}
</style>

