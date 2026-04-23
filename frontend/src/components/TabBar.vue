<template>
  <van-tabbar route class="app-tabbar">
    <van-tabbar-item to="/home" icon="home-o">{{ $t('nav.home') }}</van-tabbar-item>
    <van-tabbar-item to="/aichat" icon="chat-o">{{ $t('nav.aiChat') }}</van-tabbar-item>
    <van-tabbar-item to="/my" icon="user-o">{{ $t('nav.my') }}</van-tabbar-item>
  </van-tabbar>
</template>

<style scoped>
.app-tabbar {
  box-shadow: 0 -8px 24px rgba(15, 23, 42, 0.08);
  backdrop-filter: blur(14px);
}

:deep(.app-tabbar .van-tabbar-item) {
  color: #64748b;
}

:deep(.app-tabbar .van-tabbar-item--active) {
  color: #b71c1c;
}
</style>
