
export type MailAccountModel = {
  id: string | null
  name: string
  sndHost: string
  sndPort: number
  rcvHost: string
  rcvPort: number
  useImap: boolean
  useTls: boolean
  username: string
  password: string
}
