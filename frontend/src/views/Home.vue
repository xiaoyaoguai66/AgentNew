<template>
  <div class="home-page">
    <van-nav-bar title="NewsCopilot" fixed>
      <template #right>
        <button class="nav-action" type="button" @click="goToCategory">
          全部分类
        </button>
      </template>
    </van-nav-bar>

    <div class="home-shell">
      <section class="hero-panel">
        <p class="hero-kicker">新闻 Agent 基座</p>
        <h1 class="hero-title">移动端新闻流与热门趋势一体化体验</h1>
        <p class="hero-summary">
          当前分类：{{ activeCategoryLabel }}。列表走缓存链路，热榜走 Redis 实时热度。
        </p>
      </section>

      <section class="hot-panel">
        <div class="section-head">
          <div>
            <p class="section-eyebrow">热门快读</p>
            <h2 class="section-title">当前分类下的热门新闻</h2>
          </div>
          <button class="section-action" type="button" @click="refreshHotNews">
            刷新
          </button>
        </div>

        <div v-if="newsStore.hotLoading && !newsStore.hotNews.length" class="hot-skeleton-list">
          <div v-for="index in 3" :key="index" class="hot-skeleton skeleton" />
        </div>

        <template v-else-if="heroNews">
          <button class="hero-hot-card click-effect" type="button" @click="openNews(heroNews.id)">
            <div class="hero-hot-rank">01</div>
            <div class="hero-hot-main">
              <h3 class="hero-hot-title">{{ heroNews.title }}</h3>
              <p class="hero-hot-desc">
                {{ heroNews.description || '基于实时热度排序，适合展示 Redis 计数与回刷链路。' }}
              </p>
              <div class="hero-hot-meta">
                <span>{{ formatPublishTime(heroNews.publishTime) }}</span>
                <span>{{ formatViewCount(heroNews.views) }} 阅读</span>
              </div>
            </div>
          </button>

          <div class="hot-list">
            <button
              v-for="(item, index) in secondaryHotNews"
              :key="item.id"
              class="hot-item click-effect"
              type="button"
              @click="openNews(item.id)"
            >
              <span class="hot-rank">{{ String(index + 2).padStart(2, '0') }}</span>
              <div class="hot-item-main">
                <p class="hot-item-title">{{ item.title }}</p>
                <div class="hot-item-meta">
                  <span>{{ formatPublishTime(item.publishTime) }}</span>
                  <span>{{ formatViewCount(item.views) }} 阅读</span>
                </div>
              </div>
            </button>
          </div>
        </template>

        <div v-else class="empty-panel">
          <van-empty description="当前分类下暂无热门新闻" />
        </div>
      </section>

      <section class="feed-panel">
        <div class="section-head">
          <div>
            <p class="section-eyebrow">分类新闻流</p>
            <h2 class="section-title">持续滚动的内容列表</h2>
          </div>
        </div>

        <van-tabs
          v-model:active="activeTab"
          class="category-tabs"
          sticky
          swipeable
          animated
          :offset-top="46"
          @change="handleTabChange"
        >
          <van-tab
            v-for="category in displayCategories"
            :key="category.id"
            :title="getCategoryLabel(category.name)"
          />
        </van-tabs>

        <div v-if="newsStore.listError && !newsStore.newsList.length" class="error-panel">
          <p>{{ newsStore.listError }}</p>
          <button type="button" class="section-action" @click="retryFeed">
            重新加载
          </button>
        </div>

        <van-pull-refresh v-else v-model="newsStore.refreshing" @refresh="onRefresh">
          <van-list
            v-model:loading="newsStore.loading"
            :finished="newsStore.finished"
            finished-text="已经到底了"
            @load="onLoad"
          >
            <news-item
              v-for="item in newsStore.newsList"
              :key="item.id"
              :news="item"
            />
          </van-list>

          <div v-if="!newsStore.loading && !newsStore.newsList.length" class="empty-panel">
            <van-empty description="当前分类下暂无新闻" />
          </div>
        </van-pull-refresh>
      </section>
    </div>

    <tab-bar />
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

import NewsItem from '../components/NewsItem.vue'
import TabBar from '../components/TabBar.vue'
import { useNewsStore } from '../store/modules/news'
import {
  formatPublishTime,
  formatViewCount,
  getCategoryTranslationKey,
} from '../utils/news'


const newsStore = useNewsStore()
const route = useRoute()
const router = useRouter()
const { t } = useI18n()

const activeTab = ref(0)
const initialized = ref(false)

const displayCategories = computed(() => newsStore.displayCategories)
const heroNews = computed(() => newsStore.hotNews[0] || null)
const secondaryHotNews = computed(() => newsStore.hotNews.slice(1))
const activeCategoryLabel = computed(() => getCategoryLabel(newsStore.getCategoryName(newsStore.currentCategory)))

function getCategoryLabel(categoryName) {
  const key = getCategoryTranslationKey(categoryName)
  return key ? t(`home.categories.${key}`) : categoryName
}

function findCategoryIndex(categoryId) {
  return displayCategories.value.findIndex((category) => category.id === categoryId)
}

async function selectCategory(categoryId) {
  if (!categoryId) {
    return
  }

  newsStore.changeCategory(categoryId)
  await newsStore.refreshHomeFeed()
}

function syncActiveTab(categoryId) {
  const index = findCategoryIndex(categoryId)
  activeTab.value = index >= 0 ? index : 0
}

function goToCategory() {
  router.push('/category')
}

function openNews(newsId) {
  router.push(`/news/detail/${newsId}`)
}

async function refreshHotNews() {
  await newsStore.getHotNews(newsStore.currentCategory, 5)
}

async function retryFeed() {
  await newsStore.refreshHomeFeed()
}

async function onRefresh() {
  await newsStore.refreshHomeFeed()
}

async function onLoad() {
  await newsStore.getNewsList()
}

async function handleTabChange(index) {
  if (!initialized.value) {
    return
  }

  const category = displayCategories.value[index]
  if (!category) {
    return
  }

  if (category.id !== newsStore.currentCategory) {
    await selectCategory(category.id)
  } else {
    await newsStore.getHotNews(category.id, 5)
  }
}

onMounted(async () => {
  await newsStore.getCategories()

  const routeCategoryId = Number(route.query.categoryId || 0)
  const defaultCategoryId =
    routeCategoryId && findCategoryIndex(routeCategoryId) >= 0
      ? routeCategoryId
      : displayCategories.value[0]?.id || newsStore.currentCategory

  syncActiveTab(defaultCategoryId)
  newsStore.changeCategory(defaultCategoryId)
  await newsStore.refreshHomeFeed()
  initialized.value = true
})

watch(
  () => route.query.categoryId,
  async (value) => {
    if (!initialized.value) {
      return
    }

    const categoryId = Number(value || 0)
    if (!categoryId || categoryId === newsStore.currentCategory) {
      return
    }

    if (findCategoryIndex(categoryId) === -1) {
      return
    }

    syncActiveTab(categoryId)
    await selectCategory(categoryId)
  },
)
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  padding-top: 46px;
  padding-bottom: 72px;
  background:
    radial-gradient(circle at top, rgba(183, 28, 28, 0.12), transparent 32%),
    linear-gradient(180deg, #f6f7fb 0%, #edf1f7 100%);
}

.home-shell {
  padding: 16px;
}

.nav-action {
  border: 0;
  background: transparent;
  color: #0f172a;
  font-size: 13px;
  font-weight: 600;
}

.hero-panel,
.hot-panel,
.feed-panel {
  margin-bottom: 16px;
  padding: 18px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 18px 40px rgba(15, 23, 42, 0.08);
}

.hero-panel {
  color: #fff;
  background:
    radial-gradient(circle at top right, rgba(255, 255, 255, 0.16), transparent 34%),
    linear-gradient(135deg, #0f172a 0%, #1f2937 58%, #7f1d1d 100%);
}

.hero-kicker,
.section-eyebrow {
  margin: 0 0 8px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.hero-title,
.section-title {
  margin: 0;
  line-height: 1.35;
}

.hero-title {
  max-width: 14em;
  font-size: 28px;
}

.hero-summary {
  margin: 12px 0 0;
  max-width: 24em;
  color: rgba(255, 255, 255, 0.82);
  font-size: 14px;
  line-height: 1.7;
}

.section-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}

.section-action {
  padding: 8px 12px;
  border: 0;
  border-radius: 999px;
  background: #111827;
  color: #fff;
  font-size: 12px;
  font-weight: 600;
}

.hero-hot-card,
.hot-item {
  width: 100%;
  border: 0;
  text-align: left;
  background: transparent;
}

.hero-hot-card {
  display: flex;
  gap: 14px;
  padding: 16px;
  margin-bottom: 12px;
  border-radius: 20px;
  background:
    radial-gradient(circle at top right, rgba(183, 28, 28, 0.12), transparent 42%),
    linear-gradient(180deg, #fffaf9 0%, #ffffff 100%);
  box-shadow: inset 0 0 0 1px rgba(183, 28, 28, 0.08);
}

.hero-hot-rank,
.hot-rank {
  color: #b71c1c;
  font-weight: 800;
  letter-spacing: 0.06em;
}

.hero-hot-rank {
  font-size: 28px;
  line-height: 1;
}

.hero-hot-main {
  min-width: 0;
}

.hero-hot-title,
.hot-item-title {
  margin: 0;
  color: #111827;
  line-height: 1.5;
}

.hero-hot-title {
  font-size: 18px;
}

.hero-hot-desc {
  margin: 10px 0 12px;
  color: #5b6472;
  font-size: 13px;
  line-height: 1.7;
}

.hero-hot-meta,
.hot-item-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 12px;
  color: #7b8794;
  font-size: 12px;
}

.hot-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.hot-item {
  display: flex;
  gap: 12px;
  padding: 14px 0;
  border-top: 1px solid rgba(226, 232, 240, 0.9);
}

.hot-item-main {
  flex: 1;
  min-width: 0;
}

.hot-item-title {
  font-size: 15px;
  display: -webkit-box;
  overflow: hidden;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.category-tabs {
  margin-bottom: 12px;
}

:deep(.category-tabs .van-tabs__wrap) {
  border-radius: 16px;
  background: rgba(247, 248, 250, 0.92);
}

:deep(.category-tabs .van-tab) {
  color: #5d6b7d;
  font-size: 14px;
}

:deep(.category-tabs .van-tab--active) {
  color: #111827;
  font-weight: 700;
}

:deep(.category-tabs .van-tabs__line) {
  background: #b71c1c;
}

.hot-skeleton-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.hot-skeleton {
  height: 82px;
  border-radius: 18px;
}

.empty-panel,
.error-panel {
  padding: 16px 0 8px;
}

.error-panel {
  display: flex;
  flex-direction: column;
  gap: 12px;
  align-items: center;
  color: #7b8794;
  font-size: 14px;
}
</style>

