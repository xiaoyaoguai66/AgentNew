<template>
  <div class="ai-assistant-page">
    <van-nav-bar title="新闻 AI 助手" fixed>
      <template #left>
        <button class="nav-action" type="button" @click="openSessionDrawer">
          会话
        </button>
      </template>
      <template #right>
        <button class="nav-action" type="button" @click="createNewConversation">
          新对话
        </button>
      </template>
    </van-nav-bar>

    <van-popup
      v-model:show="showSessionDrawer"
      position="left"
      class="session-popup"
      :style="{ width: '82%', height: '100%' }"
    >
      <div class="session-panel">
        <div class="session-panel-head">
          <div>
            <p class="section-kicker">会话列表</p>
            <h2>聊天窗口</h2>
          </div>
          <button type="button" class="session-new-button" @click="createNewConversation">
            新对话
          </button>
        </div>

        <div class="session-panel-hint">
          当前会话会保存在后端 Redis 中，支持切换、恢复和删除。
        </div>

        <div v-if="sessionListLoading" class="session-loading">
          正在加载会话列表...
        </div>

        <div v-else class="session-list">
          <div
            v-for="item in sessionItems"
            :key="item.sessionId"
            class="session-item"
            :class="{ active: item.sessionId === sessionState.sessionId }"
            @click="switchSession(item)"
          >
            <div class="session-item-main">
              <strong>{{ item.title }}</strong>
              <span>{{ item.preview || '继续对话后会自动生成摘要。' }}</span>
              <small>{{ formatSessionMeta(item) }}</small>
            </div>
            <button
              type="button"
              class="session-delete"
              @click.stop="removeSession(item)"
            >
              删除
            </button>
          </div>

          <div v-if="!sessionItems.length" class="session-empty">
            暂无历史会话，发起一轮对话后会自动沉淀在这里。
          </div>
        </div>
      </div>
    </van-popup>

    <div class="assistant-shell">
      <section class="assistant-hero">
        <p class="hero-kicker">News Assistant Beta</p>
        <h1 class="hero-title">本地新闻检索 + Tavily Web Search</h1>
        <p class="hero-copy">
          当前版本支持本地新闻库、Tavily Web Search、Qdrant 向量检索、LangGraph 工作流、
          LangSmith tracing，以及会话级记忆与摘要记忆。
        </p>
        <div class="hero-meta">
          <span class="hero-pill">Prompt {{ statusState.promptVersion }}</span>
          <span class="hero-pill">检索 {{ retrievalStatusLabel }}</span>
          <span class="hero-pill">联网 {{ webSearchStatusLabel }}</span>
          <span class="hero-pill">Planner {{ plannerStatusLabel }}</span>
          <span class="hero-pill">本地引擎 {{ statusState.localRetrievalLabel }}</span>
          <span class="hero-pill">向量 {{ vectorStatusLabel }}</span>
          <span class="hero-pill">索引 {{ indexPipelineStatusLabel }}</span>
          <span class="hero-pill">Embedding {{ embeddingModeLabel }}</span>
          <span class="hero-pill">本地融合 {{ localHybridStrategyLabel }}</span>
          <span class="hero-pill">双路过滤 {{ dualRouteFilterLabel }}</span>
          <span class="hero-pill">最终排序 {{ finalRerankLabel }}</span>
          <span class="hero-pill">Verifier {{ verifierStatusLabel }}</span>
          <span class="hero-pill">Analysis {{ queryAnalysisLabel }}</span>
          <span class="hero-pill">Formatter {{ responseFormatterLabel }}</span>
          <span class="hero-pill">Workflow {{ workflowStatusDisplayLabel }}</span>
          <span class="hero-pill">Graph {{ graphVisualizationLabel }}</span>
          <span class="hero-pill">Observability {{ observabilityStatusLabel }}</span>
          <span class="hero-pill">Memory {{ memoryStatusLabel }}</span>
          <span v-if="sessionState.sessionId" class="hero-pill">Session {{ shortSessionId }}</span>
          <span v-if="sessionState.messageCount" class="hero-pill">记忆 {{ sessionState.messageCount }} 条</span>
          <span class="hero-pill">LangSmith {{ langsmithStatusLabel }}</span>
          <span v-if="lastRetrievalPlan" class="hero-pill">最近计划 {{ formatRetrievalPlan(lastRetrievalPlan) }}</span>
          <span v-if="lastStrategy" class="hero-pill">最近路径 {{ formatStrategy(lastStrategy) }}</span>
        </div>
      </section>

      <section class="control-card">
        <div class="control-group">
          <p class="control-label">回答模式</p>
          <div class="chip-row">
            <button
              v-for="item in modeOptions"
              :key="item.value"
              type="button"
              class="chip"
              :class="{ active: selectedMode === item.value }"
              @click="selectedMode = item.value"
            >
              {{ item.label }}
            </button>
          </div>
        </div>

        <div class="control-group">
          <p class="control-label">时间范围</p>
          <div class="chip-row">
            <button
              v-for="item in timeRangeOptions"
              :key="item.value"
              type="button"
              class="chip"
              :class="{ active: selectedTimeRange === item.value }"
              @click="selectedTimeRange = item.value"
            >
              {{ item.label }}
            </button>
          </div>
        </div>

        <div class="control-group">
          <p class="control-label">关注主题</p>
          <div class="chip-row">
            <button
              v-for="item in categoryOptions"
              :key="item.value"
              type="button"
              class="chip"
              :class="{ active: selectedCategory === item.value }"
              @click="selectedCategory = item.value"
            >
              {{ item.label }}
            </button>
          </div>
        </div>
      </section>

      <section class="prompt-card">
        <div class="section-head">
          <div>
            <p class="section-kicker">快捷问题</p>
            <h2>直接试双路检索能力</h2>
          </div>
        </div>

        <div class="prompt-grid">
          <button
            v-for="prompt in quickPrompts"
            :key="prompt.title"
            type="button"
            class="prompt-item click-effect"
            @click="sendPresetPrompt(prompt.prompt)"
          >
            <strong>{{ prompt.title }}</strong>
            <span>{{ prompt.description }}</span>
          </button>
        </div>
      </section>

      <section class="chat-card">
        <div class="section-head">
          <div>
            <p class="section-kicker">对话记录</p>
            <h2>新闻助手会话</h2>
          </div>
          <span class="session-badge">
            {{ isLoading ? loadingStageText : `${messageCount} 条消息` }}
          </span>
        </div>

        <div class="assistant-hint">
          当前链路是：问题分析 -> 检索规划 -> 本地/联网检索 -> 双路过滤 ->
          最终排序 -> 回答生成 -> Verifier -> 输出整理。
        </div>

        <div v-if="sessionState.summary" class="assistant-memory">
          当前会话记忆摘要：{{ sessionState.summary }}
        </div>

        <div ref="messagesContainer" class="messages-container">
          <div
            v-for="message in messages"
            :key="message.id"
            :class="['message-row', message.role]"
          >
            <div class="message-bubble" :class="message.role">
              <div v-if="message.role === 'assistant'" class="message-meta">
                <span>{{ message.metaLabel || '新闻助手' }}</span>
              </div>

              <div v-if="message.pending" class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
              <template v-else>
                <div v-html="formatMessage(message.content)"></div>

                <div
                  v-if="message.role === 'assistant' && typeof message.confidence === 'number'"
                  class="answer-confidence"
                >
                  可信度 {{ formatConfidence(message.confidence) }}
                </div>

                <div
                  v-if="message.role === 'assistant' && (message.retrievalPlan || message.strategy)"
                  class="answer-plan"
                >
                  <span v-if="message.retrievalPlan">检索计划：{{ formatRetrievalPlan(message.retrievalPlan) }}</span>
                  <span v-if="message.strategy">执行路径：{{ formatStrategy(message.strategy) }}</span>
                  <p v-if="message.plannerReason">{{ message.plannerReason }}</p>
                </div>

                <div
                  v-if="message.role === 'assistant' && (message.queryIntent || message.analysisReason)"
                  class="answer-analysis"
                >
                  <span v-if="message.queryIntent">意图：{{ formatQueryIntent(message.queryIntent) }}</span>
                  <span v-if="message.freshnessNeed">时效：{{ formatFreshness(message.freshnessNeed) }}</span>
                  <span v-if="message.scopePreference">范围：{{ formatScopePreference(message.scopePreference) }}</span>
                  <p v-if="message.analysisReason">{{ message.analysisReason }}</p>
                </div>

                <div
                  v-if="message.role === 'assistant' && (message.verificationStatus || message.evidenceLevel)"
                  class="answer-verifier"
                >
                  <span v-if="message.verificationStatus">校验：{{ formatVerificationStatus(message.verificationStatus) }}</span>
                  <span v-if="message.evidenceLevel">证据：{{ formatEvidenceLevel(message.evidenceLevel) }}</span>
                  <span v-if="message.guardrailApplied">已触发保护</span>
                  <p v-if="message.verificationReason">{{ message.verificationReason }}</p>
                </div>

                <div
                  v-if="message.role === 'assistant' && message.followUpSuggestions?.length"
                  class="follow-up-list"
                >
                  <button
                    v-for="(suggestion, suggestionIndex) in message.followUpSuggestions"
                    :key="`${message.id}-followup-${suggestionIndex}`"
                    type="button"
                    class="follow-up-chip"
                    @click="sendPresetPrompt(suggestion)"
                  >
                    {{ suggestion }}
                  </button>
                </div>

                <div
                  v-if="message.role === 'assistant' && (message.workflowSummary || message.workflowTrace?.length)"
                  class="answer-workflow"
                >
                  <p v-if="message.traceId || message.runId">
                    Trace {{ message.traceId || '-' }} / Run {{ message.runId || '-' }}
                  </p>
                  <span v-if="message.workflowSummary">工作流：{{ message.workflowSummary }}</span>
                  <p
                    v-for="(traceItem, traceIndex) in message.workflowTrace"
                    :key="`${message.id}-trace-${traceIndex}`"
                  >
                    {{ traceItem.stepIndex }}. {{ formatWorkflowNode(traceItem.node) }} /
                    {{ formatTraceStatus(traceItem.status) }} / {{ traceItem.detail }}
                  </p>
                </div>

                <div
                  v-if="message.role === 'assistant' && message.sources?.length"
                  class="source-list"
                >
                  <button
                    v-for="(source, index) in message.sources"
                    :key="`${message.id}-${source.sourceType}-${source.newsId || source.url || index}`"
                    type="button"
                    class="source-card"
                    @click="openSource(source)"
                  >
                    <span class="source-index">
                      来源 {{ index + 1 }} / {{ formatSourceType(source) }}
                    </span>
                    <strong>{{ source.title }}</strong>
                    <span class="source-meta">
                      {{ formatSourceMeta(source) }}
                    </span>
                    <p>{{ source.snippet }}</p>
                  </button>
                </div>
              </template>
            </div>
          </div>
        </div>
      </section>
    </div>

    <div class="composer-bar">
      <div class="composer-shell">
        <van-field
          v-model="userInput"
          rows="1"
          autosize
          type="textarea"
          placeholder="输入你想总结、梳理或比较的新闻问题..."
          class="chat-input"
          @keypress.enter.prevent="handleEnterPress"
        />
        <button
          type="button"
          class="send-button"
          :disabled="isLoading || !userInput.trim()"
          @click="sendMessage"
        >
          发送
        </button>
      </div>
    </div>

    <tab-bar />
  </div>
</template>

<script setup>
import { computed, nextTick, onActivated, onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import DOMPurify from 'dompurify'
import * as marked from 'marked'
import { showToast } from 'vant'

import TabBar from '../components/TabBar.vue'
import {
  deleteAiSession,
  fetchAiSession,
  fetchAiSessions,
  fetchAiStatus,
  sendAiChat,
  startAiSession,
} from '../api/ai'


const SESSION_STORAGE_KEY = 'agentnews-ai-session-id'

const router = useRouter()

const modeOptions = [
  { value: 'brief', label: '快速总结' },
  { value: 'timeline', label: '事件梳理' },
  { value: 'compare', label: '对比分析' },
]

const timeRangeOptions = [
  { value: 'all', label: '不限时间' },
  { value: '24h', label: '近 24 小时' },
  { value: '7d', label: '近 7 天' },
]

const categoryOptions = [
  { value: 'general', label: '综合' },
  { value: 'technology', label: '科技' },
  { value: 'finance', label: '财经' },
  { value: 'international', label: '国际' },
]

const quickPrompts = [
  {
    title: '本地热点',
    description: '优先用本地新闻库总结近期热点',
    prompt: '帮我总结一下最近值得关注的新闻热点，并说明最值得继续追踪的点。',
  },
  {
    title: '时间线梳理',
    description: '测试事件梳理模式和时间过滤',
    prompt: '请按时间线梳理最近一个重要新闻事件，并说明关键转折。',
  },
  {
    title: '科技观察',
    description: '验证本地来源与 Web 来源能否互补',
    prompt: '最近科技新闻里，哪些变化最可能影响大模型行业？请给我一个结构化分析。',
  },
  {
    title: '国际更新',
    description: '验证最新外部来源补充能力',
    prompt: '请结合最近的国际新闻，告诉我有哪些事件值得重点关注。',
  },
]

const statusState = reactive({
  promptVersion: 'pending',
  retrievalEnabled: true,
  webSearchEnabled: false,
  plannerEnabled: false,
  localRetrievalLabel: 'lexical-baseline',
  vectorRetrievalEnabled: false,
  vectorStoreConfigured: false,
  vectorRetrievalActive: false,
  chunkingReady: false,
  embeddingConfigured: false,
  embeddingConfigMode: 'missing',
  qdrantConfigured: false,
  indexSyncReady: false,
  localHybridStrategy: 'lexical-only',
  dualRouteFilterStrategy: 'basic-filtering',
  finalRerankStrategy: 'default-fusion',
  verifierEnabled: false,
  verifierStrategy: 'disabled',
  queryAnalysisEnabled: false,
  queryAnalysisStrategy: 'disabled',
  responseFormatterEnabled: false,
  responseFormatterStrategy: 'disabled',
  workflowEnabled: false,
  workflowEngine: 'custom',
  workflowStyle: 'disabled',
  graphVisualizationReady: false,
  observabilityEnabled: false,
  observabilityMode: 'disabled',
  memoryEnabled: false,
  memoryBackend: 'disabled',
  memorySummaryStrategy: 'disabled',
  memoryTtlSeconds: 0,
  memoryRecentMessageLimit: 0,
  langsmithReady: false,
  langsmithTracing: false,
  langsmithConfigured: false,
})

const sessionState = reactive({
  sessionId: '',
  title: '新对话',
  preview: '',
  summary: '',
  messageCount: 0,
  updatedAt: '',
})

const messages = ref([])
const userInput = ref('')
const messagesContainer = ref(null)
const isLoading = ref(false)
const loadingStageText = ref('准备回答中...')
const selectedMode = ref('brief')
const selectedTimeRange = ref('all')
const selectedCategory = ref('general')
const lastRetrievalPlan = ref('')
const lastStrategy = ref('')

const showSessionDrawer = ref(false)
const sessionItems = ref([])
const sessionListLoading = ref(false)

let messageId = 0

const createMessage = (message) => ({
  id: ++messageId,
  ...message,
})

const createWelcomeMessage = () =>
  createMessage({
    role: 'assistant',
    kind: 'welcome',
    metaLabel: '新闻助手',
    content:
      '你好，我是 AgentNews 新闻助手。我会优先从本地新闻库检索证据；如果已配置 Tavily，也会补充 Web 搜索来源，并在工作流中做过滤、排序、校验和会话记忆管理。',
    confidence: null,
    sources: [],
    retrievalPlan: '',
    strategy: '',
    plannerReason: '',
    verificationStatus: 'accepted',
    verificationReason: '',
    evidenceLevel: 'none',
    guardrailApplied: false,
    queryIntent: 'fact',
    freshnessNeed: 'low',
    scopePreference: 'hybrid',
    analysisReason: '',
    followUpSuggestions: [],
    traceId: '',
    runId: '',
    workflowSummary: '',
    workflowTrace: [],
  })

messages.value = [createWelcomeMessage()]

const messageCount = computed(() => messages.value.filter((item) => !item.pending).length)
const shortSessionId = computed(() => (sessionState.sessionId ? sessionState.sessionId.slice(0, 8) : ''))
const retrievalStatusLabel = computed(() => (statusState.retrievalEnabled ? '已开启' : '未开启'))
const webSearchStatusLabel = computed(() => (statusState.webSearchEnabled ? 'Tavily 已开启' : 'Tavily 未开启'))
const plannerStatusLabel = computed(() => (statusState.plannerEnabled ? '已开启' : '未开启'))
const vectorStatusLabel = computed(() => {
  if (statusState.vectorRetrievalActive) return '已激活'
  if (statusState.vectorRetrievalEnabled && statusState.vectorStoreConfigured) return '已配置待接入'
  if (statusState.vectorRetrievalEnabled) return '开关已开，索引未配'
  return '未开启'
})
const indexPipelineStatusLabel = computed(() => {
  if (statusState.indexSyncReady) return '可同步'
  if (statusState.chunkingReady && statusState.embeddingConfigured && !statusState.qdrantConfigured) return '缺少 Qdrant'
  if (statusState.chunkingReady && !statusState.embeddingConfigured) return '缺少 Embedding'
  if (statusState.chunkingReady) return '已预留'
  return '未准备'
})
const embeddingModeLabel = computed(() => {
  if (statusState.embeddingConfigMode === 'explicit') return '显式配置'
  if (statusState.embeddingConfigMode === 'llm-fallback') return 'LLM 回退'
  if (statusState.embeddingConfigMode === 'partial') return '配置不完整'
  return '未配置'
})
const localHybridStrategyLabel = computed(() => (
  statusState.localHybridStrategy === 'weighted-rrf' ? 'Weighted RRF' : 'Lexical Only'
))
const dualRouteFilterLabel = computed(() => (
  statusState.dualRouteFilterStrategy === 'route-aware-filtering' ? 'Route-Aware' : 'Basic'
))
const finalRerankLabel = computed(() => (
  statusState.finalRerankStrategy === 'plan-aware-cross-source' ? 'Cross-Source' : 'Default'
))
const verifierStatusLabel = computed(() => {
  if (!statusState.verifierEnabled) return '未开启'
  if (statusState.verifierStrategy === 'rule-based-post-verifier') return 'Rule-Based'
  return 'Enabled'
})
const queryAnalysisLabel = computed(() => {
  if (!statusState.queryAnalysisEnabled) return '未开启'
  if (statusState.queryAnalysisStrategy === 'heuristic-query-analysis') return 'Heuristic'
  return 'Enabled'
})
const responseFormatterLabel = computed(() => {
  if (!statusState.responseFormatterEnabled) return '未开启'
  if (statusState.responseFormatterStrategy === 'evidence-aware-followups') return 'Follow-Ups'
  return 'Enabled'
})
const workflowStatusDisplayLabel = computed(() => {
  if (!statusState.workflowEnabled) return '未开启'
  if (statusState.workflowStyle === 'langgraph-stategraph') return 'LangGraph'
  if (statusState.workflowStyle === 'stateful-node-pipeline') return 'Stateful'
  return 'Enabled'
})
const graphVisualizationLabel = computed(() => {
  if (!statusState.workflowEnabled) return 'Off'
  if (statusState.graphVisualizationReady && statusState.workflowEngine === 'langgraph') return 'Ready'
  return 'Pending'
})
const observabilityStatusLabel = computed(() => {
  if (!statusState.observabilityEnabled) return 'Disabled'
  if (statusState.observabilityMode === 'local-trace-log') return 'Local'
  return 'Enabled'
})
const memoryStatusLabel = computed(() => {
  if (!statusState.memoryEnabled) return 'Off'
  if (statusState.memorySummaryStrategy === 'heuristic-rollup') return 'Redis Session'
  return 'Enabled'
})
const langsmithStatusLabel = computed(() => {
  if (statusState.langsmithConfigured) return 'Configured'
  if (statusState.langsmithReady && statusState.langsmithTracing) return 'Waiting Key'
  if (statusState.langsmithReady) return 'Ready'
  return 'Off'
})

const formatMessage = (content) => {
  if (!content) return ''
  return DOMPurify.sanitize(marked.parse(content))
}

const formatConfidence = (value) => `${Math.round(value * 100)}%`

const formatRetrievalPlan = (value) => ({
  'local-first': 'Local-First',
  hybrid: 'Hybrid',
  'web-first': 'Web-First',
}[value] || value || '未知')

const formatStrategy = (value) => ({
  local_first_answer: '本地优先命中',
  local_first_with_web_fallback_answer: '本地优先 + Web 补充',
  local_first_web_fallback_answer: '本地优先降级到 Web',
  local_first_nohit: '本地优先未命中',
  web_first_answer: 'Web 优先命中',
  web_first_with_local_support_answer: 'Web 优先 + 本地补充',
  web_first_local_fallback_answer: 'Web 优先降级到本地',
  web_first_nohit: 'Web 优先未命中',
  hybrid_local_web_reranked_answer: '双路并行 + 融合排序',
  hybrid_local_only_answer: '混合计划，仅本地命中',
  hybrid_web_only_answer: '混合计划，仅 Web 命中',
  hybrid_nohit: '混合计划未命中',
}[value] || value || '未知')

const formatVerificationStatus = (value) => ({
  accepted: '已通过',
  guarded: '保守回退',
  refused: '拒答',
}[value] || value || '未知')

const formatEvidenceLevel = (value) => ({
  none: '无证据',
  weak: '弱',
  moderate: '中',
  strong: '强',
}[value] || value || '未知')

const formatQueryIntent = (value) => ({
  fact: '事实问答',
  summary: '总结概览',
  timeline: '事件梳理',
  compare: '对比分析',
}[value] || value || '未知')

const formatFreshness = (value) => ({
  low: '低',
  medium: '中',
  high: '高',
}[value] || value || '未知')

const formatScopePreference = (value) => ({
  local: '本地优先',
  hybrid: '本地+Web',
  web: 'Web 优先',
}[value] || value || '未知')

const formatWorkflowNode = (value) => ({
  'query-analysis': '问题分析',
  'retrieval-planner': '检索规划',
  retrieval: '检索执行',
  'route-filter': '双路过滤',
  'final-rerank': '最终排序',
  generator: '回答生成',
  verifier: '回答校验',
  'response-formatter': '输出整理',
  'no-evidence-response': '无证据拒答',
}[value] || value || '未知节点')

const formatTraceStatus = (value) => ({
  completed: '完成',
  guarded: '保护',
  fallback: '回退',
}[value] || value || '未知')

const formatSourceType = (source) => (source.sourceType === 'web' ? 'Web 搜索' : '本地新闻')

const formatSourceMeta = (source) => {
  const publishTime = source.publishTime
    ? new Date(source.publishTime).toLocaleString('zh-CN', {
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
      })
    : '时间未知'

  const domain = source.sourceType === 'web' && source.domain ? ` / ${source.domain}` : ''
  const retrievalTags = source.sourceType === 'local' && source.retrievalTags?.length
    ? ` / ${source.retrievalTags.join('+')}`
    : ''
  const score = typeof source.score === 'number' ? ` / 综合 ${Math.round(source.score * 100) / 100}` : ''
  return `${publishTime}${domain}${retrievalTags}${score}`
}

const formatSessionMeta = (item) => {
  const time = item.updatedAt
    ? new Date(item.updatedAt).toLocaleString('zh-CN', {
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
      })
    : '时间未知'
  return `${time} / ${item.messageCount || 0} 条消息`
}

const buildHistoryMessages = () =>
  messages.value
    .filter((item) => !item.pending && item.kind !== 'welcome')
    .map((item) => ({
      role: item.role,
      content: item.content,
    }))

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const getStoredSessionId = () => window.localStorage.getItem(SESSION_STORAGE_KEY) || ''

const persistSessionId = (value) => {
  if (!value) {
    window.localStorage.removeItem(SESSION_STORAGE_KEY)
    return
  }
  window.localStorage.setItem(SESSION_STORAGE_KEY, value)
}

const createRestoredConversationMessage = (item) =>
  createMessage({
    role: item.role,
    kind: item.role === 'assistant' ? 'reply' : 'user',
    metaLabel: item.role === 'assistant' ? '新闻助手' : '',
    content: item.content,
    confidence: null,
    sources: [],
    retrievalPlan: '',
    strategy: '',
    plannerReason: '',
    verificationStatus: 'accepted',
    verificationReason: '',
    evidenceLevel: 'none',
    guardrailApplied: false,
    queryIntent: 'fact',
    freshnessNeed: 'low',
    scopePreference: 'hybrid',
    analysisReason: '',
    followUpSuggestions: [],
    traceId: '',
    runId: '',
    workflowSummary: '',
    workflowTrace: [],
  })

const restoreSessionMessages = (session) => {
  const restoredMessages = [createWelcomeMessage()]
  const sessionMessages = Array.isArray(session?.recentMessages) ? session.recentMessages : []
  sessionMessages.forEach((item) => {
    if (!item?.role || !item?.content) return
    restoredMessages.push(createRestoredConversationMessage(item))
  })
  messages.value = restoredMessages
}

const applySessionState = (session, { restoreMessages = false } = {}) => {
  sessionState.sessionId = session?.sessionId || ''
  sessionState.title = session?.title || '新对话'
  sessionState.preview = session?.preview || ''
  sessionState.summary = session?.summary || ''
  sessionState.messageCount = typeof session?.messageCount === 'number' ? session.messageCount : 0
  sessionState.updatedAt = session?.updatedAt || ''
  persistSessionId(sessionState.sessionId)

  if (restoreMessages) {
    restoreSessionMessages(session)
  }
}

function syncCurrentSessionMetaFromList() {
  if (!sessionState.sessionId || !sessionItems.value.length) return

  const activeItem = sessionItems.value.find((item) => item.sessionId === sessionState.sessionId)
  if (!activeItem) return

  sessionState.title = activeItem.title || sessionState.title
  sessionState.preview = activeItem.preview || sessionState.preview
  sessionState.messageCount =
    typeof activeItem.messageCount === 'number' ? activeItem.messageCount : sessionState.messageCount
  sessionState.updatedAt = activeItem.updatedAt || sessionState.updatedAt
}

const refreshSessionItems = async () => {
  sessionListLoading.value = true
  try {
    sessionItems.value = await fetchAiSessions({
      limit: 30,
      activeSessionId: sessionState.sessionId,
    })
    syncCurrentSessionMetaFromList()
  } catch (error) {
    console.error('session list fetch error:', error)
  } finally {
    sessionListLoading.value = false
  }
}

const ensureSession = async ({ restoreMessages = false } = {}) => {
  const storedSessionId = getStoredSessionId()
  const session = storedSessionId
    ? await fetchAiSession(storedSessionId)
    : await startAiSession()

  applySessionState(session, { restoreMessages })
  await refreshSessionItems()
  return session
}

const syncAiStatus = async () => {
  try {
    const status = await fetchAiStatus()
    Object.assign(statusState, status)
  } catch (error) {
    console.error('AI status fetch error:', error)
  }
}

const openSource = (source) => {
  if (source.sourceType === 'web' && source.url) {
    window.open(source.url, '_blank', 'noopener')
    return
  }
  if (source.newsId) {
    router.push(`/news/detail/${source.newsId}`)
  }
}

const openSessionDrawer = async () => {
  showSessionDrawer.value = true
  await refreshSessionItems()
}

const switchSession = async (item, { keepDrawerOpen = false } = {}) => {
  if (!item?.sessionId) return
  if (isLoading.value) {
    showToast({
      message: '当前正在生成回答，请稍后再切换会话',
      position: 'bottom',
    })
    return
  }

  try {
    const session = await fetchAiSession(item.sessionId)
    applySessionState(session, { restoreMessages: true })
    await refreshSessionItems()
    if (!keepDrawerOpen) {
      showSessionDrawer.value = false
    }
    await nextTick()
    scrollToBottom()
  } catch (error) {
    showToast({
      message: error.message || '切换会话失败，请稍后重试',
      position: 'bottom',
    })
  }
}

const createNewConversation = async () => {
  if (isLoading.value) {
    showToast({
      message: '当前正在生成回答，请稍后再试',
      position: 'bottom',
    })
    return
  }

  try {
    const currentSessionId = sessionState.sessionId
    const hasConversation = sessionState.messageCount > 0 || messages.value.length > 1
    if (currentSessionId && !hasConversation) {
      await deleteAiSession(currentSessionId)
    }

    const session = await startAiSession()
    messages.value = [createWelcomeMessage()]
    userInput.value = ''
    applySessionState(session)
    await refreshSessionItems()
    showSessionDrawer.value = false
  } catch (error) {
    showToast({
      message: error.message || '新建会话失败，请稍后重试',
      position: 'bottom',
    })
  }
}

const removeSession = async (item) => {
  if (!item?.sessionId) return
  if (isLoading.value && item.sessionId === sessionState.sessionId) {
    showToast({
      message: '当前会话正在生成回答，请稍后删除',
      position: 'bottom',
    })
    return
  }

  try {
    const wasActive = item.sessionId === sessionState.sessionId
    await deleteAiSession(item.sessionId)
    await refreshSessionItems()

    if (wasActive) {
      const fallback = sessionItems.value.find((session) => session.sessionId !== item.sessionId)
      if (fallback) {
        await switchSession(fallback, { keepDrawerOpen: true })
      } else {
        await createNewConversation()
      }
    }
  } catch (error) {
    showToast({
      message: error.message || '删除会话失败，请稍后重试',
      position: 'bottom',
    })
  }
}

const setLoadingStage = async (text) => {
  loadingStageText.value = text
  await nextTick()
}

const sendMessage = async (presetText = '') => {
  const rawInput = (presetText || userInput.value).trim()
  if (!rawInput || isLoading.value) {
    return
  }

  const history = buildHistoryMessages()

  messages.value.push(
    createMessage({
      role: 'user',
      kind: 'user',
      content: rawInput,
    }),
  )

  userInput.value = ''
  messages.value.push(
    createMessage({
      role: 'assistant',
      kind: 'loading',
      content: '',
      pending: true,
      metaLabel: '新闻助手',
      confidence: null,
      sources: [],
      verificationStatus: 'accepted',
      verificationReason: '',
      evidenceLevel: 'none',
      guardrailApplied: false,
      queryIntent: 'fact',
      freshnessNeed: 'low',
      scopePreference: 'hybrid',
      analysisReason: '',
      followUpSuggestions: [],
      traceId: '',
      runId: '',
      workflowSummary: '',
      workflowTrace: [],
    }),
  )

  isLoading.value = true
  await nextTick()
  scrollToBottom()

  try {
    await setLoadingStage('正在执行本地检索与 Web 搜索...')
    const response = await sendAiChat({
      question: rawInput,
      history,
      mode: selectedMode.value,
      timeRange: selectedTimeRange.value,
      category: selectedCategory.value,
      sessionId: sessionState.sessionId || undefined,
    })

    const lastMessage = messages.value[messages.value.length - 1]
    lastMessage.pending = false
    lastMessage.kind = 'reply'
    lastMessage.content = response.reply || '抱歉，我暂时无法生成回复。'
    lastMessage.metaLabel = response.model ? `新闻助手 / ${response.model}` : '新闻助手'
    lastMessage.confidence = response.confidence
    lastMessage.sources = response.sources || []
    lastMessage.retrievalPlan = response.retrievalPlan || ''
    lastMessage.strategy = response.strategy || ''
    lastMessage.plannerReason = response.plannerReason || ''
    lastMessage.queryIntent = response.queryIntent || 'fact'
    lastMessage.freshnessNeed = response.freshnessNeed || 'low'
    lastMessage.scopePreference = response.scopePreference || 'hybrid'
    lastMessage.analysisReason = response.analysisReason || ''
    lastMessage.verificationStatus = response.verificationStatus || 'accepted'
    lastMessage.verificationReason = response.verificationReason || ''
    lastMessage.evidenceLevel = response.evidenceLevel || 'none'
    lastMessage.guardrailApplied = Boolean(response.guardrailApplied)
    lastMessage.followUpSuggestions = response.followUpSuggestions || []
    lastMessage.traceId = response.traceId || ''
    lastMessage.runId = response.runId || ''
    lastMessage.workflowSummary = response.workflowSummary || ''
    lastMessage.workflowTrace = response.workflowTrace || []

    statusState.promptVersion = response.promptVersion || statusState.promptVersion
    statusState.retrievalEnabled = response.retrievalEnabled
    statusState.webSearchEnabled = response.webSearchEnabled
    lastRetrievalPlan.value = response.retrievalPlan || ''
    lastStrategy.value = response.strategy || ''

    sessionState.sessionId = response.sessionId || sessionState.sessionId
    sessionState.summary = response.memorySummary || ''
    sessionState.messageCount = response.memoryMessageCount || sessionState.messageCount
    sessionState.updatedAt = response.memoryUpdatedAt || sessionState.updatedAt
    persistSessionId(sessionState.sessionId)
    await refreshSessionItems()
  } catch (error) {
    console.error('AI response error:', error)
    const lastMessage = messages.value[messages.value.length - 1]
    lastMessage.pending = false
    lastMessage.kind = 'error'
    lastMessage.content = `发生错误：${error.message || '请检查后端 AI 配置后重试。'}`
    lastMessage.metaLabel = '新闻助手'
    showToast({
      message: error.message || 'AI 服务暂时不可用',
      position: 'bottom',
    })
  } finally {
    isLoading.value = false
    loadingStageText.value = '准备回答中...'
    await nextTick()
    scrollToBottom()
  }
}

const sendPresetPrompt = async (prompt) => {
  await sendMessage(prompt)
}

const handleEnterPress = (event) => {
  if (event.shiftKey) return
  sendMessage()
}

watch(
  messages,
  async () => {
    await nextTick()
    scrollToBottom()
  },
  { deep: true },
)

onMounted(async () => {
  await syncAiStatus()
  await ensureSession({ restoreMessages: true })
  scrollToBottom()
})

onActivated(async () => {
  await syncAiStatus()
  if (sessionState.sessionId) {
    const session = await fetchAiSession(sessionState.sessionId)
    applySessionState(session, { restoreMessages: messages.value.length <= 1 })
    await refreshSessionItems()
  } else {
    await ensureSession({ restoreMessages: true })
  }
})
</script>

<style scoped>
.ai-assistant-page {
  min-height: 100vh;
  padding-top: 46px;
  padding-bottom: 154px;
  background:
    radial-gradient(circle at top, rgba(183, 28, 28, 0.08), transparent 28%),
    linear-gradient(180deg, #f6f7fb 0%, #edf1f7 100%);
}

.assistant-shell {
  padding: 16px;
}

.session-popup {
  background: #f8fafc;
}

.session-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 20px 16px;
}

.session-panel-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.session-panel-head h2 {
  margin: 0;
  line-height: 1.35;
}

.session-panel-hint {
  margin-bottom: 16px;
  border-radius: 16px;
  padding: 12px;
  background: rgba(15, 23, 42, 0.05);
  color: #526072;
  font-size: 13px;
  line-height: 1.6;
}

.session-new-button {
  border: 0;
  border-radius: 999px;
  padding: 9px 12px;
  background: #111827;
  color: #fff;
  font-size: 12px;
  font-weight: 700;
}

.session-loading,
.session-empty {
  border-radius: 16px;
  padding: 14px;
  background: rgba(255, 255, 255, 0.94);
  color: #64748b;
  font-size: 13px;
  line-height: 1.6;
}

.session-list {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 10px;
  overflow-y: auto;
}

.session-item {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 10px;
  border-radius: 18px;
  padding: 14px;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.06);
}

.session-item.active {
  border: 1px solid rgba(183, 28, 28, 0.24);
  background: rgba(255, 249, 247, 0.98);
}

.session-item-main {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 6px;
  min-width: 0;
}

.session-item-main strong {
  color: #111827;
  font-size: 14px;
  line-height: 1.5;
}

.session-item-main span {
  color: #5b6472;
  font-size: 12px;
  line-height: 1.6;
}

.session-item-main small {
  color: #94a3b8;
  font-size: 11px;
}

.session-delete {
  border: 0;
  background: transparent;
  color: #8b1e1e;
  font-size: 12px;
  font-weight: 700;
}

.assistant-hero,
.control-card,
.prompt-card,
.chat-card {
  margin-bottom: 16px;
  padding: 18px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 18px 40px rgba(15, 23, 42, 0.08);
}

.assistant-hero {
  color: #fff;
  background:
    radial-gradient(circle at top right, rgba(255, 255, 255, 0.16), transparent 32%),
    linear-gradient(135deg, #0f172a 0%, #1f2937 58%, #7f1d1d 100%);
}

.hero-kicker,
.section-kicker,
.control-label {
  margin: 0 0 8px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.hero-title,
.section-head h2 {
  margin: 0;
  line-height: 1.35;
}

.hero-title {
  max-width: 16em;
  font-size: 28px;
}

.hero-copy {
  margin: 12px 0 0;
  color: rgba(255, 255, 255, 0.82);
  font-size: 14px;
  line-height: 1.8;
}

.hero-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 16px;
}

.hero-pill {
  display: inline-flex;
  align-items: center;
  border: 1px solid rgba(255, 255, 255, 0.22);
  border-radius: 999px;
  padding: 7px 12px;
  background: rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.88);
  font-size: 12px;
  font-weight: 600;
}

.nav-action {
  border: 0;
  background: transparent;
  color: #0f172a;
  font-size: 13px;
  font-weight: 600;
}

.control-group + .control-group {
  margin-top: 16px;
}

.chip-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.chip {
  border: 0;
  border-radius: 999px;
  padding: 9px 12px;
  background: rgba(15, 23, 42, 0.06);
  color: #475569;
  font-size: 13px;
  font-weight: 600;
}

.chip.active {
  background: #b71c1c;
  color: #fff;
}

.section-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}

.session-badge {
  display: inline-flex;
  align-items: center;
  padding: 8px 12px;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.06);
  color: #475569;
  font-size: 12px;
  font-weight: 600;
}

.assistant-hint {
  margin-bottom: 16px;
  border-radius: 16px;
  padding: 12px 14px;
  background: rgba(15, 23, 42, 0.04);
  color: #526072;
  font-size: 13px;
  line-height: 1.6;
}

.assistant-memory {
  margin-bottom: 16px;
  border-radius: 16px;
  padding: 12px 14px;
  background: rgba(183, 28, 28, 0.08);
  color: #8b1e1e;
  font-size: 13px;
  line-height: 1.7;
}

.prompt-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.prompt-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px;
  border: 0;
  border-radius: 20px;
  text-align: left;
  background:
    radial-gradient(circle at top right, rgba(183, 28, 28, 0.1), transparent 38%),
    linear-gradient(180deg, rgba(255, 250, 249, 0.98) 0%, rgba(255, 255, 255, 0.98) 100%);
}

.prompt-item strong {
  color: #111827;
  font-size: 16px;
  line-height: 1.5;
}

.prompt-item span {
  color: #5b6472;
  font-size: 13px;
  line-height: 1.6;
}

.messages-container {
  max-height: 46vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding-right: 2px;
}

.message-row {
  display: flex;
}

.message-row.user {
  justify-content: flex-end;
}

.message-row.assistant {
  justify-content: flex-start;
}

.message-bubble {
  max-width: 88%;
  border-radius: 20px;
  padding: 14px 16px;
  word-break: break-word;
}

.message-bubble.user {
  background: #b71c1c;
  color: #fff;
  border-bottom-right-radius: 8px;
}

.message-bubble.assistant {
  background: rgba(248, 250, 252, 0.96);
  color: #111827;
  border-bottom-left-radius: 8px;
}

.message-meta {
  margin-bottom: 8px;
  color: #7b8794;
  font-size: 12px;
  font-weight: 600;
}

.answer-confidence {
  margin-top: 12px;
  color: #526072;
  font-size: 12px;
  font-weight: 600;
}

.answer-plan,
.answer-workflow {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-top: 10px;
  color: #526072;
  font-size: 12px;
}

.answer-plan p,
.answer-workflow p {
  margin: 0;
  line-height: 1.6;
}

.answer-analysis,
.answer-verifier {
  display: flex;
  flex-wrap: wrap;
  gap: 6px 10px;
  margin-top: 10px;
  color: #526072;
  font-size: 12px;
}

.answer-analysis p,
.answer-verifier p {
  width: 100%;
  margin: 0;
  line-height: 1.6;
}

.follow-up-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.follow-up-chip {
  border: 0;
  border-radius: 999px;
  padding: 8px 12px;
  background: rgba(183, 28, 28, 0.08);
  color: #8b1e1e;
  font-size: 12px;
  font-weight: 600;
  text-align: left;
}

.source-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 14px;
}

.source-card {
  display: flex;
  flex-direction: column;
  gap: 6px;
  width: 100%;
  padding: 12px;
  border: 0;
  border-radius: 16px;
  text-align: left;
  background: rgba(15, 23, 42, 0.05);
}

.source-index {
  color: #8b1e1e;
  font-size: 12px;
  font-weight: 700;
}

.source-card strong {
  color: #111827;
  font-size: 14px;
  line-height: 1.5;
}

.source-meta {
  color: #64748b;
  font-size: 12px;
}

.source-card p {
  margin: 0;
  color: #475569;
  font-size: 13px;
  line-height: 1.6;
}

.composer-bar {
  position: fixed;
  left: 50%;
  right: auto;
  bottom: calc(56px + env(safe-area-inset-bottom));
  width: min(750px, 100%);
  transform: translateX(-50%);
  padding: 0 16px;
  z-index: 9;
}

.composer-shell {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  padding: 12px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 18px 40px rgba(15, 23, 42, 0.14);
}

.chat-input {
  flex: 1;
  padding: 6px 0;
}

.send-button {
  border: 0;
  border-radius: 18px;
  padding: 12px 16px;
  background: #111827;
  color: #fff;
  font-size: 13px;
  font-weight: 700;
}

.send-button:disabled {
  background: #cbd5e1;
  color: #fff;
}

.typing-indicator {
  display: flex;
  padding: 4px 0;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  margin-right: 6px;
  border-radius: 50%;
  background: #94a3b8;
  animation: bounce 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.18s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.36s;
}

@keyframes bounce {
  0%,
  60%,
  100% {
    transform: translateY(0);
  }

  30% {
    transform: translateY(-5px);
  }
}

:deep(.message-bubble p) {
  margin: 8px 0;
}

:deep(.message-bubble ul),
:deep(.message-bubble ol) {
  padding-left: 20px;
}

:deep(.message-bubble pre) {
  padding: 12px;
  border-radius: 12px;
  overflow-x: auto;
  background: rgba(15, 23, 42, 0.06);
}

:deep(.message-bubble code) {
  border-radius: 6px;
  padding: 2px 6px;
  background: rgba(15, 23, 42, 0.06);
}

@media (max-width: 560px) {
  .prompt-grid {
    grid-template-columns: 1fr;
  }

  .hero-title {
    font-size: 24px;
  }

  .messages-container {
    max-height: 42vh;
  }
}
</style>
