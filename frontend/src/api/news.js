import { request } from './http'


function normalizeCategory(item = {}) {
  return {
    id: Number(item.id || 0),
    name: item.name || '',
    sortOrder: Number(item.sortOrder ?? item.sort_order ?? 0),
  }
}


function normalizeNewsItem(item = {}) {
  return {
    id: Number(item.id || 0),
    title: item.title || '',
    description: item.description || '',
    image: item.image || '',
    author: item.author || 'AgentNews',
    categoryId: Number(item.categoryId ?? item.category_id ?? 0),
    views: Number(item.views || 0),
    publishTime: item.publishTime || item.publish_time || '',
  }
}


function normalizeNewsDetail(item = {}) {
  return {
    ...normalizeNewsItem(item),
    content: item.content || '',
    relatedNews: Array.isArray(item.relatedNews)
      ? item.relatedNews.map(normalizeNewsItem)
      : [],
  }
}


export async function fetchNewsCategories() {
  const data = await request({
    url: '/api/news/categories',
    method: 'get',
  })

  return Array.isArray(data) ? data.map(normalizeCategory) : []
}


export async function fetchNewsList(params) {
  const data = await request({
    url: '/api/news/list',
    method: 'get',
    params,
  })

  return {
    list: Array.isArray(data?.list) ? data.list.map(normalizeNewsItem) : [],
    total: Number(data?.total || 0),
    hasMore: Boolean(data?.hasMore),
  }
}


export async function fetchNewsDetail(newsId) {
  const data = await request({
    url: '/api/news/detail',
    method: 'get',
    params: { id: newsId },
  })

  return normalizeNewsDetail(data)
}


export async function fetchHotNews(params = {}) {
  const data = await request({
    url: '/api/news/hot',
    method: 'get',
    params,
  })

  return Array.isArray(data) ? data.map(normalizeNewsItem) : []
}
