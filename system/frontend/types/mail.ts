
export type MailAccountModel = {
  id: string | null
  name: string
  snd_host: string
  snd_port: number
  rcv_host: string
  rcv_port: number
  use_imap: boolean
  use_tls: boolean
  username: string
  password: string
}
