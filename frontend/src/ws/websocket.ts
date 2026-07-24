/**
 * 宠迹 PawTrack — WebSocket 客户端
 * 实时接收位置更新和报警推送
 */
import { getToken } from '../api/client'

export type WsMessage =
  | { type: 'connected'; user_id: number; ts: number }
  | { type: 'location'; pet_id: number; device_id: number; lat: number; lng: number; accuracy: number | null; source: string; battery: number; ts: number }
  | { type: 'alarm'; alarm_id: number; pet_id: number; alarm_type: string; severity: string; lat: number; lng: number; ts: number }
  | { type: 'pong'; ts: number }
  | { type: 'ack'; action: string; channel: string; pet_id?: number; ts: number }
  | { type: 'error'; code: number; message: string }

type MessageHandler = (msg: WsMessage) => void

export class PawTrackWebSocket {
  private ws: WebSocket | null = null
  private heartbeatTimer: number | null = null
  private reconnectTimer: number | null = null
  private handlers: Set<MessageHandler> = new Set()
  private subscribedPets: Set<number> = new Set()
  private isConnecting = false

  connect() {
    if (this.ws?.readyState === WebSocket.OPEN || this.isConnecting) return
    this.isConnecting = true

    const token = getToken()
    if (!token) {
      console.warn('[WS] 无 Token，跳过连接')
      this.isConnecting = false
      return
    }

    const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = location.host
    const wsUrl = `${protocol}//${host}/ws/v1?token=${token}`

    console.log('[WS] 连接中...', wsUrl)
    this.ws = new WebSocket(wsUrl)

    this.ws.onopen = () => {
      this.isConnecting = false
      console.log('[WS] 连接已建立')
      this.startHeartbeat()
      // 重新订阅之前的 pet
      this.subscribedPets.forEach(petId => this._subscribe('location', petId))
      this._subscribe('alarm')
    }

    this.ws.onmessage = (event) => {
      try {
        const msg: WsMessage = JSON.parse(event.data)
        this.handlers.forEach(h => h(msg))
      } catch (e) {
        console.error('[WS] 消息解析失败', e)
      }
    }

    this.ws.onclose = (event) => {
      this.isConnecting = false
      console.log('[WS] 连接关闭', event.code, event.reason)
      this.stopHeartbeat()
      if (event.code !== 4001 && event.code !== 4002) {
        // 非鉴权失败，尝试重连
        this.scheduleReconnect()
      }
    }

    this.ws.onerror = (error) => {
      console.error('[WS] 连接错误', error)
    }
  }

  disconnect() {
    this.stopHeartbeat()
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
    this.subscribedPets.clear()
    if (this.ws) {
      this.ws.onclose = null
      this.ws.close()
      this.ws = null
    }
  }

  // ── 订阅管理 ────────────────────────────────

  subscribeLocation(petId: number) {
    this.subscribedPets.add(petId)
    this._subscribe('location', petId)
  }

  unsubscribeLocation(petId: number) {
    this.subscribedPets.delete(petId)
    this._send({ action: 'unsubscribe', channel: 'location', pet_id: petId })
  }

  subscribeAlarm() {
    this._subscribe('alarm')
  }

  private _subscribe(channel: string, petId?: number) {
    this._send({ action: 'subscribe', channel, pet_id: petId })
  }

  private _send(msg: any) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(msg))
    }
  }

  // ── 心跳 ────────────────────────────────

  private startHeartbeat() {
    this.stopHeartbeat()
    this.heartbeatTimer = window.setInterval(() => {
      this._send({ action: 'ping' })
    }, 60_000) // 每60秒发一次心跳
  }

  private stopHeartbeat() {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer)
      this.heartbeatTimer = null
    }
  }

  // ── 重连 ────────────────────────────────

  private scheduleReconnect() {
    if (this.reconnectTimer) return
    this.reconnectTimer = window.setTimeout(() => {
      this.reconnectTimer = null
      console.log('[WS] 尝试重连...')
      this.connect()
    }, 3_000)
  }

  // ── 事件监听 ────────────────────────────────

  onMessage(handler: MessageHandler): () => void {
    this.handlers.add(handler)
    return () => this.handlers.delete(handler)
  }
}

// 全局单例
export const wsClient = new PawTrackWebSocket()
