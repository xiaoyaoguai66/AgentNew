<template>
  <div class="my-page">
    <van-nav-bar title="我的" fixed />

    <div class="my-shell">
      <section class="profile-hero">
        <div class="profile-top">
          <van-image
            round
            width="78"
            height="78"
            src="https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg"
          />

          <div class="profile-main">
            <p class="profile-kicker">个人中心</p>
            <h1>{{ profileTitle }}</h1>
            <p class="profile-copy">{{ profileDescription }}</p>
          </div>
        </div>

        <div class="profile-actions">
          <button
            v-if="!isLogin"
            type="button"
            class="primary-button"
            @click="goToLogin"
          >
            去登录
          </button>
          <button
            v-if="!isLogin"
            type="button"
            class="secondary-button"
            @click="goToRegister"
          >
            注册账号
          </button>
          <button
            v-if="isLogin"
            type="button"
            class="secondary-button"
            @click="goToProfile"
          >
            编辑资料
          </button>
          <button
            v-if="isLogin"
            type="button"
            class="secondary-button"
            @click="handleLogout"
          >
            退出登录
          </button>
        </div>
      </section>

      <section class="summary-grid">
        <button type="button" class="summary-card click-effect" @click="goToFavorite">
          <span class="summary-label">收藏内容</span>
          <strong class="summary-value">{{ favoriteCount }}</strong>
          <span class="summary-note">沉淀高价值新闻</span>
        </button>

        <button type="button" class="summary-card click-effect" @click="goToHistory">
          <span class="summary-label">浏览记录</span>
          <strong class="summary-value">{{ historyCount }}</strong>
          <span class="summary-note">回看阅读路径</span>
        </button>

        <button type="button" class="summary-card click-effect accent" @click="goToAIChat">
          <span class="summary-label">新闻助手</span>
          <strong class="summary-value">AI</strong>
          <span class="summary-note">进入问答与分析页</span>
        </button>
      </section>

      <section class="menu-card">
        <div class="menu-head">
          <p class="menu-kicker">快捷入口</p>
          <h2>我的服务</h2>
        </div>

        <div class="menu-list">
          <button type="button" class="menu-item" @click="goToFavorite">
            <div>
              <p class="menu-title">我的收藏</p>
              <p class="menu-desc">查看收藏的新闻和后续重点阅读内容</p>
            </div>
            <van-icon name="arrow" />
          </button>

          <button type="button" class="menu-item" @click="goToHistory">
            <div>
              <p class="menu-title">浏览历史</p>
              <p class="menu-desc">回看最近读过的新闻内容</p>
            </div>
            <van-icon name="arrow" />
          </button>

          <button type="button" class="menu-item" @click="goToAIChat">
            <div>
              <p class="menu-title">新闻 AI 助手</p>
              <p class="menu-desc">进入问答页，后续承接新闻 Agent 入口</p>
            </div>
            <van-icon name="arrow" />
          </button>

          <button type="button" class="menu-item" @click="goToSettings">
            <div>
              <p class="menu-title">设置</p>
              <p class="menu-desc">语言、主题和账号安全配置</p>
            </div>
            <van-icon name="arrow" />
          </button>
        </div>
      </section>
    </div>

    <tab-bar />
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showDialog } from 'vant'

import TabBar from '../components/TabBar.vue'
import { useFavoriteStore } from '../store/modules/favorite'
import { useHistoryStore } from '../store/modules/history'
import { useUserStore } from '../store/user'


const router = useRouter()
const userStore = useUserStore()
const favoriteStore = useFavoriteStore()
const historyStore = useHistoryStore()

const userInfo = computed(() => userStore.userInfo)
const isLogin = computed(() => userStore.getLoginStatus)
const favoriteCount = computed(() => favoriteStore.getFavorites.length)
const historyCount = computed(() => historyStore.getHistory.length)
const profileTitle = computed(() => (isLogin.value ? userInfo.value?.username || '已登录用户' : '未登录'))
const profileDescription = computed(() => {
  if (!isLogin.value) {
    return '登录后同步收藏、历史和后续新闻 Agent 会话。'
  }
  return userStore.getUserBio || '保持你的新闻阅读轨迹和个人资料同步。'
})

function goToLogin() {
  router.push('/login')
}

function goToRegister() {
  router.push('/register')
}

function goToProfile() {
  if (!isLogin.value) {
    router.push('/login')
    return
  }
  router.push('/profile')
}

function goToFavorite() {
  router.push('/favorite')
}

function goToHistory() {
  router.push('/history')
}

function goToAIChat() {
  router.push('/aichat')
}

function goToSettings() {
  router.push('/settings')
}

function handleLogout() {
  showDialog({
    title: '提示',
    message: '确定要退出当前账号吗？',
    showCancelButton: true,
  }).then((action) => {
    if (action === 'confirm') {
      userStore.logout()
      router.push('/login')
    }
  })
}

async function hydrateCollections() {
  favoriteStore.loadFavorites()
  historyStore.loadHistory()

  if (!isLogin.value) {
    return
  }

  await Promise.allSettled([
    userStore.getUserInfoDetail(),
    favoriteStore.getFavoriteListApi(),
    historyStore.getHistoryListApi(),
  ])
}

onMounted(async () => {
  await hydrateCollections()
})
</script>

<style scoped>
.my-page {
  min-height: 100vh;
  padding-top: 46px;
  padding-bottom: 72px;
  background:
    radial-gradient(circle at top, rgba(183, 28, 28, 0.1), transparent 30%),
    linear-gradient(180deg, #f6f7fb 0%, #edf1f7 100%);
}

.my-shell {
  padding: 16px;
}

.profile-hero,
.menu-card {
  margin-bottom: 16px;
  padding: 18px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 18px 40px rgba(15, 23, 42, 0.08);
}

.profile-hero {
  color: #fff;
  background:
    radial-gradient(circle at top right, rgba(255, 255, 255, 0.16), transparent 32%),
    linear-gradient(135deg, #0f172a 0%, #1f2937 60%, #7f1d1d 100%);
}

.profile-top {
  display: flex;
  gap: 16px;
  align-items: center;
}

.profile-main {
  min-width: 0;
}

.profile-kicker,
.menu-kicker {
  margin: 0 0 8px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.profile-main h1,
.menu-head h2 {
  margin: 0;
  line-height: 1.35;
}

.profile-main h1 {
  font-size: 28px;
}

.profile-copy {
  margin: 10px 0 0;
  color: rgba(255, 255, 255, 0.82);
  font-size: 14px;
  line-height: 1.8;
}

.profile-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 18px;
}

.primary-button,
.secondary-button {
  border: 0;
  border-radius: 999px;
  padding: 10px 14px;
  font-size: 13px;
  font-weight: 600;
}

.primary-button {
  background: #fff;
  color: #111827;
}

.secondary-button {
  background: rgba(255, 255, 255, 0.14);
  color: #fff;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}

.summary-card {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 18px 14px;
  border: 0;
  border-radius: 22px;
  text-align: left;
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 16px 36px rgba(15, 23, 42, 0.06);
}

.summary-card.accent {
  background:
    radial-gradient(circle at top right, rgba(183, 28, 28, 0.12), transparent 38%),
    linear-gradient(180deg, #fffaf9 0%, #ffffff 100%);
}

.summary-label {
  color: #7b8794;
  font-size: 12px;
}

.summary-value {
  color: #111827;
  font-size: 28px;
  line-height: 1;
}

.summary-note {
  color: #475569;
  font-size: 12px;
  line-height: 1.5;
}

.menu-head {
  margin-bottom: 14px;
}

.menu-list {
  display: flex;
  flex-direction: column;
}

.menu-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 16px 0;
  border: 0;
  border-bottom: 1px solid rgba(226, 232, 240, 0.9);
  background: transparent;
  text-align: left;
}

.menu-item:last-child {
  border-bottom: 0;
}

.menu-title {
  margin: 0 0 6px;
  color: #111827;
  font-size: 16px;
  font-weight: 700;
}

.menu-desc {
  margin: 0;
  color: #64748b;
  font-size: 13px;
  line-height: 1.6;
}

@media (max-width: 560px) {
  .summary-grid {
    grid-template-columns: 1fr;
  }
}
</style>
