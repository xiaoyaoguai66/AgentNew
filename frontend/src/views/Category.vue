<template>
  <div class="category-page">
    <van-nav-bar
      :title="$t('common.allCategories')"
      :left-text="$t('common.back')"
      left-arrow
      fixed
      @click-left="onClickLeft"
    />

    <div class="category-shell">
      <div class="category-head">
        <p class="category-kicker">频道导航</p>
        <h1>按主题快速进入新闻流</h1>
      </div>

      <van-grid :column-num="3" :border="false" gutter="12">
        <van-grid-item
          v-for="category in displayCategories"
          :key="category.id"
          class="category-card"
          :text="getCategoryLabel(category.name)"
          icon="newspaper-o"
          @click="goToCategoryNews(category.id)"
        />
      </van-grid>
    </div>

    <tab-bar />
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

import TabBar from '../components/TabBar.vue'
import { useNewsStore } from '../store/modules/news'
import { getCategoryTranslationKey } from '../utils/news'


const newsStore = useNewsStore()
const router = useRouter()
const { t } = useI18n()

const displayCategories = computed(() => newsStore.displayCategories)

function getCategoryLabel(categoryName) {
  const key = getCategoryTranslationKey(categoryName)
  return key ? t(`home.categories.${key}`) : categoryName
}

function onClickLeft() {
  router.back()
}

function goToCategoryNews(categoryId) {
  newsStore.changeCategory(categoryId)
  router.push({
    path: '/home',
    query: { categoryId },
  })
}

onMounted(async () => {
  await newsStore.getCategories()
})
</script>

<style scoped>
.category-page {
  min-height: 100vh;
  padding-top: 46px;
  padding-bottom: 72px;
  background:
    radial-gradient(circle at top, rgba(183, 28, 28, 0.08), transparent 28%),
    linear-gradient(180deg, #f6f7fb 0%, #edf1f7 100%);
}

.category-shell {
  margin: 16px;
  padding: 20px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 16px 36px rgba(15, 23, 42, 0.08);
}

.category-head {
  margin-bottom: 16px;
}

.category-head h1 {
  margin: 0;
  color: #111827;
  font-size: 24px;
  line-height: 1.35;
}

.category-kicker {
  margin: 0 0 8px;
  color: #b71c1c;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

:deep(.category-card .van-grid-item__content) {
  border-radius: 18px;
  padding: 20px 0;
  background:
    linear-gradient(180deg, rgba(248, 250, 252, 0.95) 0%, rgba(241, 245, 249, 0.95) 100%);
}

:deep(.category-card .van-grid-item__icon) {
  color: #b71c1c;
  font-size: 28px;
}

:deep(.category-card .van-grid-item__text) {
  margin-top: 8px;
  color: #0f172a;
  font-size: 14px;
  font-weight: 600;
}
</style>
