export const LEVELS = [
  { value: 'light', label: '轻度拥挤' },
  { value: 'heavy', label: '重度拥挤' },
  { value: 'severe', label: '严重拥挤' },
]
export const levelLabel = (v) => LEVELS.find((l) => l.value === v)?.label ?? v
export const edgeKey = (a, b) => [a, b].sort().join('—')
