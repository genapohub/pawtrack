/**
 * Pawtrack Tokens — official collection values.
 * Keep in sync with styles/tokens.css. UI code should import from here
 * instead of writing palette hex literals.
 */
export const PT = {
  bg: '#F6F3EE',
  surface: '#FFFCF8',
  bgMuted: '#EFEBE6',
  border: '#E4DFD8',
  borderStrong: '#C9C2B8',
  fg: '#2A2622',
  fg2: '#6B645C',
  fg3: '#746C64',
  fgInv: '#F6F3EE',
  accent: '#3E5470',
  accentHover: '#32445C',
  accentSubtle: '#E8EDF1',
  mock: '#6F6250',
  mockBg: '#F3EEE6',
  mockBorder: '#E4D9C8',
  success: '#4A635E',
  successSubtle: '#E8EEEC',
  warning: '#8F6240',
  warningSubtle: '#F4EDE4',
  danger: '#9A5848',
  dangerSubtle: '#F3E8E4',
  map: '#E6E4DE',
  mapLine: '#C2BDB4',
  pin: '#3E5470',
  sidebar: '#2A2724',
  sidebarLine: '#3A3531',
  sidebarMuted: '#A39A90',
  sidebarLink: '#D8D2CA',
  sidebarOff: '#7A736C',
  dogTagBg: '#EDE6DC',
  dogTagFg: '#6A5240',
  stage: '#E8E4DE',
  radiusMd: 14,
  radiusSm: 12,
  accentSoft: 'rgba(62, 84, 112, 0.10)',
  fgScrim: 'rgba(42, 38, 34, 0.72)',
  font: '"PingFang SC", -apple-system, BlinkMacSystemFont, "Helvetica Neue", sans-serif',
} as const

export type PawtrackToken = typeof PT
