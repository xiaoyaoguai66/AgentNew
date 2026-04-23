<template>
  <div class="collection-page">
    <van-nav-bar
      title="浏览历史"
      left-text="返回"
      left-arrow
      fixed
      @click-left="onClickLeft"
    >
      <template #right>
        <button v-if="items.length" type="button" class="nav-clear" @click="onClickClear">
          清空
        </button>
      </template>
    </van-nav-bar>

    <div class="collection-shell">
      <section class="collection-hero history-hero">
        <p class="collection-kicker">阅读轨迹</p>
        <h1>最近看过的新闻</h1>
        <p class="collection-copy">
          共 {{ items.length }} 条历史。
          {{ isLogin ? '已优先同步账号下的阅读记录。' : '当前展示本地浏览记录，登录后可同步账号数据。' }}
        </p>
      </section>

      <section v-if="loading" class="collection-card">
        <div v-for="index in 3" :key="index" class="collection-skeleton skeleton" />
      </section>

      <section v-else-if="items.length" class="collection-card list-card">
        <saved-news-card
          v-for="item in items"
          :key="item.id"
          :news="item"
          secondary-label="浏览时间"
          :secondary-value="item.viewTime"
          action-text="删除"
          @select="goToNewsDetail"
          @action="confirmDelete"
        />
      </section>

      <section v-else class="collection-card empty-card">
        <van-empty description="暂无浏览历史" />
        <button
          v-if="!isLogin"
          type="button"
          class="primary-button"
          @click="goToLogin"
        >
          去登录
        </button>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { showDialog, showToast } from 'vant'

import SavedNewsCard from '../components/SavedNewsCard.vue'
import { useHistoryStore } from '../store/modules/history'
import { useUserStore } from '../store/user'


const router = useRouter()
const historyStore = useHistoryStore()
const userStore = useUserStore()

const loading = ref(true)
const items = computed(() => historyStore.getHistory)
const isLogin = computed(() => userStore.getLoginStatus)

function onClickLeft() {
  router.back()
}

function goToLogin() {
  router.push('/login')
}

function goToNewsDetail(id) {
  router.push(`/news/detail/${id}`)
}

async function hydrateHistory() {
  loading.value = true
  historyStore.loadHistory()

  try {
    const result = await historyStore.getHistoryListApi()
    if (!result?.success) {
      historyStore.loadHistory()
    }
  } catch (error) {
    historyStore.loadHistory()
  } finally {
    loading.value = false
  }
}

async function removeHistory(id) {
  const result = await historyStore.removeHistoryApi(id)
  if (result.success) {
    showToast({
      message: '已移除历史记录',
      position: 'bottom',
    })
    return
  }

  showToast({
    message: result.message || '删除失败，请稍后重试',
    position: 'bottom',
  })
}

function confirmDelete(id) {
  showDialog({
    title: '提示',
    message: '确定要删除这条浏览记录吗？',
    showCancelButton: true,
  }).then((action) => {
    if (action === 'confirm') {
      removeHistory(id)
    }
  })
}

function onClickClear() {
  showDialog({
    title: '提示',
    message: '确定要清空所有浏览历史吗？',
    showCancelButton: true,
  }).then(async (action) => {
    if (action !== 'confirm') {
      return
    }

    const result = await historyStore.clearHistoryApi()
    if (result?.success) {
      showToast({
        message: '浏览历史已清空',
        position: 'bottom',
      })
      return
    }

    showToast({
      message: result?.message || '清空失败，请稍后重试',
      position: 'bottom',
    })
  })
}

onMounted(async () => {
  await hydrateHistory()
})
</script>

<style scoped>
.collection-page {
  min-height: 100vh;
  padding-top: 46px;
  background:
    radial-gradient(circle at top, rgba(15, 23, 42, 0.08), transparent 28%),
    linear-gradient(180deg, #f6f7fb 0%, #edf1f7 100%);
}

.collection-shell {
  padding: 16px;
}

.collection-hero,
.collection-card {
  margin-bottom: 16px;
  padding: 18px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 18px 40px rgba(15, 23, 42, 0.08);
}

.history-hero {
  color: #fff;
  background:
    radial-gradient(circle at top right, rgba(255, 255, 255, 0.14), transparent 34%),
    linear-gradient(135deg, #0f172a 0%, #1f2937 62%, #334155 100%);
}

.collection-kicker {
  margin: 0 0 8px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.collection-hero h1 {
  margin: 0;
  font-size: 28px;
  line-height: 1.35;
}

.collection-copy {
  margin: 12px 0 0;
  color: rgba(255, 255, 255, 0.82);
  font-size: 14px;
  line-height: 1.8;
}

.nav-clear,
.primary-button {
  border: 0;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 600;
}

.nav-clear {
  background: transparent;
  color: #0f172a;
}

.primary-button {
  padding: 10px 16px;
  background: #111827;
  color: #fff;
}

.list-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.empty-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
}

.collection-skeleton {
  height: 104px;
  border-radius: 20px;
  margin-bottom: 12px;
}
</style>
