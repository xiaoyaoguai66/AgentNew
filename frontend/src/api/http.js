import axios from 'axios'
import { showToast } from 'vant'

import { apiConfig } from '../config/api'


const http = axios.create({
  baseURL: apiConfig.baseURL,
  timeout: 10000,
})


function resolveErrorMessage(error) {
  if (error.code === 'ECONNABORTED' || /timeout/i.test(error.message || '')) {
    return '请求超时，请稍后重试'
  }

  return error.response?.data?.message || '网络请求失败，请稍后重试'
}


http.interceptors.response.use(
  (response) => response,
  (error) => {
    if (!error.config?.silent) {
      showToast({
        message: resolveErrorMessage(error),
        position: 'bottom',
      })
    }
    return Promise.reject(error)
  },
)


export async function request(config) {
  const response = await http(config)
  const payload = response.data

  if (!payload || payload.code !== 200) {
    throw new Error(payload?.message || '接口请求失败')
  }

  return payload.data
}


export default http
