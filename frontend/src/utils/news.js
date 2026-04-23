const CATEGORY_TRANSLATION_KEY_MAP = {
  头条: 'headline',
  社会: 'society',
  国内: 'domestic',
  国际: 'international',
  娱乐: 'entertainment',
  体育: 'sports',
  军事: 'military',
  科技: 'technology',
  财经: 'finance',
  更多: 'more',
}


export function getCategoryTranslationKey(categoryName) {
  return CATEGORY_TRANSLATION_KEY_MAP[categoryName] || ''
}


export function formatPublishTime(value) {
  if (!value) {
    return '刚刚'
  }

  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return value
  }

  return new Intl.DateTimeFormat('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date)
}


export function formatViewCount(value) {
  const views = Number(value || 0)
  if (views >= 10000) {
    return `${(views / 10000).toFixed(1)}万`
  }
  if (views >= 1000) {
    return `${(views / 1000).toFixed(1)}k`
  }
  return `${views}`
}
