import { request } from './http'

const AI_STATUS_TIMEOUT_MS = 5000
const AI_CHAT_TIMEOUT_MS = 90000


function normalizeSource(item = {}) {
  return {
    sourceType: item.sourceType || 'local',
    newsId: item.newsId ?? null,
    title: item.title || '',
    snippet: item.snippet || '',
    url: item.url || '',
    domain: item.domain || '',
    categoryId: item.categoryId ?? null,
    publishTime: item.publishTime || '',
    retrievalTags: Array.isArray(item.retrievalTags) ? item.retrievalTags : [],
    score: typeof item.score === 'number' ? item.score : 0,
  }
}


export async function fetchAiStatus() {
  const data = await request({
    url: '/api/ai/status',
    method: 'get',
    silent: true,
    timeout: AI_STATUS_TIMEOUT_MS,
  })

  return {
    promptVersion: data?.promptVersion || '',
    retrievalEnabled: Boolean(data?.retrievalEnabled),
    webSearchEnabled: Boolean(data?.webSearchEnabled),
    plannerEnabled: Boolean(data?.plannerEnabled),
    supportedRetrievalPlans: Array.isArray(data?.supportedRetrievalPlans) ? data.supportedRetrievalPlans : [],
    localRetrievalEngine: data?.localRetrievalEngine || 'lexical',
    localRetrievalLabel: data?.localRetrievalLabel || 'lexical-baseline',
    vectorRetrievalEnabled: Boolean(data?.vectorRetrievalEnabled),
    vectorStoreConfigured: Boolean(data?.vectorStoreConfigured),
    vectorRetrievalActive: Boolean(data?.vectorRetrievalActive),
    vectorBackend: data?.vectorBackend || 'qdrant-reserved',
    chunkingReady: Boolean(data?.chunkingReady),
    embeddingConfigured: Boolean(data?.embeddingConfigured),
    embeddingConfigMode: data?.embeddingConfigMode || 'missing',
    qdrantConfigured: Boolean(data?.qdrantConfigured),
    indexSyncReady: Boolean(data?.indexSyncReady),
    localHybridStrategy: data?.localHybridStrategy || 'lexical-only',
    dualRouteFilterStrategy: data?.dualRouteFilterStrategy || 'basic-filtering',
    finalRerankStrategy: data?.finalRerankStrategy || 'default-fusion',
    verifierEnabled: Boolean(data?.verifierEnabled),
    verifierStrategy: data?.verifierStrategy || 'disabled',
    queryAnalysisEnabled: Boolean(data?.queryAnalysisEnabled),
    queryAnalysisStrategy: data?.queryAnalysisStrategy || 'disabled',
    responseFormatterEnabled: Boolean(data?.responseFormatterEnabled),
    responseFormatterStrategy: data?.responseFormatterStrategy || 'disabled',
    workflowEnabled: Boolean(data?.workflowEnabled),
    workflowEngine: data?.workflowEngine || 'custom',
    workflowStyle: data?.workflowStyle || 'disabled',
    graphVisualizationReady: Boolean(data?.graphVisualizationReady),
    workflowNodes: Array.isArray(data?.workflowNodes) ? data.workflowNodes : [],
    observabilityEnabled: Boolean(data?.observabilityEnabled),
    observabilityMode: data?.observabilityMode || 'disabled',
    runLoggingEnabled: Boolean(data?.runLoggingEnabled),
    runLogPath: data?.runLogPath || '',
    memoryEnabled: Boolean(data?.memoryEnabled),
    memoryBackend: data?.memoryBackend || 'disabled',
    memorySummaryStrategy: data?.memorySummaryStrategy || 'disabled',
    memoryTtlSeconds: typeof data?.memoryTtlSeconds === 'number' ? data.memoryTtlSeconds : 0,
    memoryRecentMessageLimit: typeof data?.memoryRecentMessageLimit === 'number' ? data.memoryRecentMessageLimit : 0,
    langsmithReady: Boolean(data?.langsmithReady),
    langsmithTracing: Boolean(data?.langsmithTracing),
    langsmithConfigured: Boolean(data?.langsmithConfigured),
    langsmithProject: data?.langsmithProject || '',
    langsmithEndpoint: data?.langsmithEndpoint || '',
  }
}


export async function sendAiChat(payload) {
  const data = await request({
    url: '/api/ai/chat',
    method: 'post',
    data: payload,
    timeout: AI_CHAT_TIMEOUT_MS,
  })

  return {
    reply: data?.reply || '',
    model: data?.model || '',
    promptVersion: data?.promptVersion || '',
    traceId: data?.traceId || '',
    runId: data?.runId || '',
    workflowSummary: data?.workflowSummary || '',
    strategy: data?.strategy || '',
    retrievalPlan: data?.retrievalPlan || 'hybrid',
    plannerReason: data?.plannerReason || '',
    queryIntent: data?.queryIntent || 'fact',
    freshnessNeed: data?.freshnessNeed || 'low',
    scopePreference: data?.scopePreference || 'hybrid',
    analysisReason: data?.analysisReason || '',
    confidence: typeof data?.confidence === 'number' ? data.confidence : 0,
    verificationStatus: data?.verificationStatus || 'accepted',
    verificationReason: data?.verificationReason || '',
    evidenceLevel: data?.evidenceLevel || 'none',
    guardrailApplied: Boolean(data?.guardrailApplied),
    followUpSuggestions: Array.isArray(data?.followUpSuggestions) ? data.followUpSuggestions : [],
    workflowTrace: Array.isArray(data?.workflowTrace) ? data.workflowTrace : [],
    sources: Array.isArray(data?.sources) ? data.sources.map(normalizeSource) : [],
    retrievalEnabled: Boolean(data?.retrievalEnabled),
    webSearchEnabled: Boolean(data?.webSearchEnabled),
    sessionId: data?.sessionId || '',
    memoryEnabled: Boolean(data?.memoryEnabled),
    memorySummary: data?.memorySummary || '',
    memoryMessageCount: typeof data?.memoryMessageCount === 'number' ? data.memoryMessageCount : 0,
    memoryUpdatedAt: data?.memoryUpdatedAt || '',
  }
}


function normalizeSessionState(data = {}) {
  return {
    sessionId: data?.sessionId || '',
    title: data?.title || '新对话',
    preview: data?.preview || '',
    summary: data?.summary || '',
    messageCount: typeof data?.messageCount === 'number' ? data.messageCount : 0,
    updatedAt: data?.updatedAt || '',
    recentMessages: Array.isArray(data?.recentMessages) ? data.recentMessages : [],
    memoryEnabled: Boolean(data?.memoryEnabled),
    backend: data?.backend || 'redis-session-memory',
  }
}


function normalizeSessionListItem(data = {}) {
  return {
    sessionId: data?.sessionId || '',
    title: data?.title || '新对话',
    preview: data?.preview || '',
    messageCount: typeof data?.messageCount === 'number' ? data.messageCount : 0,
    updatedAt: data?.updatedAt || '',
    active: Boolean(data?.active),
  }
}


export async function startAiSession() {
  const data = await request({
    url: '/api/ai/session/start',
    method: 'post',
    timeout: AI_STATUS_TIMEOUT_MS,
  })

  return normalizeSessionState(data)
}


export async function fetchAiSession(sessionId) {
  const data = await request({
    url: `/api/ai/session/${sessionId}`,
    method: 'get',
    timeout: AI_STATUS_TIMEOUT_MS,
    silent: true,
  })

  return normalizeSessionState(data)
}


export async function fetchAiSessions(params = {}) {
  const query = new URLSearchParams()
  if (params.limit) query.set('limit', params.limit)
  if (params.activeSessionId) query.set('active_session_id', params.activeSessionId)

  const suffix = query.toString() ? `?${query.toString()}` : ''
  const data = await request({
    url: `/api/ai/sessions${suffix}`,
    method: 'get',
    timeout: AI_STATUS_TIMEOUT_MS,
    silent: true,
  })

  return Array.isArray(data) ? data.map(normalizeSessionListItem) : []
}


export async function deleteAiSession(sessionId) {
  const data = await request({
    url: `/api/ai/session/${sessionId}`,
    method: 'delete',
    timeout: AI_STATUS_TIMEOUT_MS,
  })

  return {
    sessionId: data?.sessionId || sessionId,
    deleted: Boolean(data?.deleted),
  }
}
