/**
 * 宠迹 PawTrack — Toast 工具
 */
let toastEl: HTMLElement | null = null

export function showToast(message: string, duration = 2500) {
  if (toastEl) toastEl.remove()

  toastEl = document.createElement('div')
  toastEl.className = 'toast'
  toastEl.textContent = message
  document.body.appendChild(toastEl)

  setTimeout(() => {
    if (toastEl) {
      toastEl.remove()
      toastEl = null
    }
  }, duration)
}
