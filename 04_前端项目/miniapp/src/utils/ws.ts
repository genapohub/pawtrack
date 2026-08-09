/**
 * 宠迹 PawTrack — WebSocket 封装（uni.connectSocket）
 *
 * 协议与后端 /ws/v1 一致：
 *   发送：{action: 'subscribe'|'unsubscribe'|'ping', channel: 'location'|'alarm', pet_id?}
 *   接收：{type: 'connected'|'location'|'alarm'|'pong'|'error', ...}
 */
import { WS_BASE } from './config'
import { getAccessToken } from './auth'

type MsgHandler = (msg: any) => void

class PawSocket {
  private task: UniApp.SocketTask | null = null
  private handlers: Record<string, MsgHandler[]> = {}
  private reconnectTimer: number | null = null
  private heartbeatTimer: number | null = null
  private manualClose = false
  private pending: any[] = [] // 未连接时缓存订阅消息

  /** 建立连接（token 为空则跳过） */
  connect(): void {
    const token = getAccessToken()
    if (!token) return

    this.manualClose = false
    const url = `${WS_BASE}?token=${token}`

    this.task = uni.connectSocket({
      url,
      complete: () => {},
    })

    this.task.onOpen(() => {
      console.log('[WS] 已连接')
      // 补发缓存消息
      while (this.pending.length) {
        const msg = this.pending.shift()
        this.send(msg)
      }
      this.startHeartbeat()
    })

    this.task.onMessage((res: any) => {
      try {
        const msg = typeof res.data === 'string' ? JSON.parse(res.data) : res.data
        this.dispatch(msg)
      } catch (e) {
        console.error('[WS] 消息解析失败', e)
      }
    })

    this.task.onClose(() => {
      console.log('[WS] 连接关闭')
      this.stopHeartbeat()
      if (!this.manualClose) this.scheduleReconnect()
    })

    this.task.onError((err: any) => {
      console.error('[WS] 错误', err)
      if (!this.manualClose) this.scheduleReconnect()
    })
  }

  /** 订阅频道 */
  subscribe(channel: string, petId?: number): void {
    this.send({ action: 'subscribe', channel, pet_id: petId })
  }

  unsubscribe(channel: string, petId?: number): void {
    this.send({ action: 'unsubscribe', channel, pet_id: petId })
  }

  /** 注册消息类型处理器 */
  on(type: string, handler: MsgHandler): void {
    if (!this.handlers[type]) this.handlers[type] = []
    this.handlers[type].push(handler)
  }

  /** 发送消息（未连接则缓存） */
  send(msg: any): void {
    if (this.task && this.manualClose === false) {
      this.task.send({ data: JSON.stringify(msg) })
    } else {
      this.pending.push(msg)
    }
  }

  close(): void {
    this.manualClose = true
    this.stopHeartbeat()
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
    this.task?.close({ code: 1000, reason: 'manual' })
    this.task = null
  }

  /** 自动重连（指数退避 1s → 2s → 4s ... 上限 30s） */
  private scheduleReconnect(): void {
    if (this.reconnectTimer) return
    const delay = 1000
    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null
      console.log('[WS] 重新连接...')
      this.connect()
    }, delay)
  }

  /** 心跳：30s ping 一次 */
  private startHeartbeat(): void {
    this.stopHeartbeat()
    this.heartbeatTimer = setInterval(() => {
      this.send({ action: 'ping' })
    }, 30000) as unknown as number
  }

  private stopHeartbeat(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer)
      this.heartbeatTimer = null
    }
  }

  private dispatch(msg: any): void {
    const handlers = this.handlers[msg.type]
    if (handlers) {
      handlers.forEach((h) => h(msg))
    }
  }
}

/** 全局单例 */
export const pawSocket = new PawSocket()
