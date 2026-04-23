import { defineStore } from 'pinia'

import {
  fetchHotNews,
  fetchNewsCategories,
  fetchNewsDetail,
  fetchNewsList,
} from '../../api/news'


const MORE_CATEGORY = { id: 10, name: '更多', sortOrder: 999 }
const DEFAULT_CATEGORIES = [
  { id: 1, name: '头条', sortOrder: 1 },
  { id: 2, name: '社会', sortOrder: 2 },
  { id: 3, name: '国内', sortOrder: 3 },
  { id: 4, name: '国际', sortOrder: 4 },
  { id: 5, name: '娱乐', sortOrder: 5 },
  { id: 6, name: '体育', sortOrder: 6 },
  { id: 7, name: '科技', sortOrder: 7 },
]


export const useNewsStore = defineStore('news', {
  state: () => ({
    newsList: [],
    newsDetail: {},
    hotNews: [],
    categories: [],
    currentCategory: 1,
    page: 1,
    pageSize: 10,
    total: 0,
    loading: false,
    refreshing: false,
    finished: false,
    categoriesLoading: false,
    hotLoading: false,
    detailLoading: false,
    listError: '',
    detailError: '',
    hotError: '',
  }),

  getters: {
    displayCategories: (state) => state.categories.filter((item) => item.name !== MORE_CATEGORY.name),
  },

  actions: {
    async getCategories(force = false) {
      if (this.categoriesLoading) {
        return this.categories
      }
      if (this.categories.length && !force) {
        return this.categories
      }

      this.categoriesLoading = true

      try {
        const categories = await fetchNewsCategories()
        this.categories = [...categories, MORE_CATEGORY]

        if (!this.currentCategory && categories.length) {
          this.currentCategory = categories[0].id
        }

        return this.categories
      } catch (error) {
        console.error('获取新闻分类失败:', error)

        if (!this.categories.length) {
          this.categories = [...DEFAULT_CATEGORIES, MORE_CATEGORY]
        }

        return this.categories
      } finally {
        this.categoriesLoading = false
      }
    },

    resetListState() {
      this.newsList = []
      this.page = 1
      this.total = 0
      this.finished = false
      this.listError = ''
    },

    changeCategory(categoryId) {
      if (this.currentCategory === categoryId) {
        return
      }

      this.currentCategory = categoryId
      this.resetListState()
    },

    async getNewsList(refresh = false) {
      if (this.loading && !refresh) {
        return
      }
      if (this.finished && !refresh) {
        return
      }

      if (refresh) {
        this.refreshing = true
        this.page = 1
        this.finished = false
        this.listError = ''
      }

      this.loading = true

      try {
        const result = await fetchNewsList({
          categoryId: this.currentCategory,
          page: this.page,
          pageSize: this.pageSize,
        })

        this.newsList = refresh
          ? result.list
          : [...this.newsList, ...result.list]
        this.total = result.total
        this.finished = !result.hasMore || result.list.length === 0
        this.page += 1
        return result
      } catch (error) {
        this.listError = error.message || '获取新闻列表失败'
        console.error('获取新闻列表失败:', error)
        return {
          list: [],
          total: this.total,
          hasMore: false,
        }
      } finally {
        this.loading = false
        this.refreshing = false
      }
    },

    async getNewsDetail(newsId) {
      this.newsDetail = {}
      this.detailLoading = true
      this.detailError = ''

      try {
        const detail = await fetchNewsDetail(newsId)
        this.newsDetail = detail
        return detail
      } catch (error) {
        this.newsDetail = {}
        this.detailError = error.message || '获取新闻详情失败'
        console.error('获取新闻详情失败:', error)
        throw error
      } finally {
        this.detailLoading = false
      }
    },

    clearNewsDetail() {
      this.newsDetail = {}
      this.detailError = ''
      this.detailLoading = false
    },

    async getHotNews(categoryId = this.currentCategory, limit = 5) {
      this.hotLoading = true
      this.hotError = ''

      try {
        const hotNews = await fetchHotNews({ categoryId, limit })
        this.hotNews = hotNews
        return hotNews
      } catch (error) {
        this.hotNews = []
        this.hotError = error.message || '获取热门新闻失败'
        console.error('获取热门新闻失败:', error)
        return []
      } finally {
        this.hotLoading = false
      }
    },

    async refreshHomeFeed() {
      await Promise.all([
        this.getHotNews(this.currentCategory, 5),
        this.getNewsList(true),
      ])
    },

    getCategoryName(categoryId) {
      const category = this.categories.find((item) => item.id === categoryId)
      return category ? category.name : '未知'
    },
  },
})
