export type SyncNotification = {
  id: number
  level: 'info' | 'warning' | 'error'
  message: string
  is_read: boolean
  created_at: string
}
