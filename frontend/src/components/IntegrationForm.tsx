import { FormEvent, useState } from 'react'
import { connectAdSense, connectFacebook } from '../services/api'

type Props = {
  userId: number
  onConnected: () => void
}

type FacebookForm = {
  accountId: string
  accessToken: string
  businessId?: string
}

type GoogleForm = {
  accountId: string
  accessToken: string
  clientId: string
  clientSecret: string
  refreshToken: string
}

const initialFacebook: FacebookForm = {
  accountId: '',
  accessToken: '',
  businessId: '',
}

const initialGoogle: GoogleForm = {
  accountId: '',
  accessToken: '',
  clientId: '',
  clientSecret: '',
  refreshToken: '',
}

export function IntegrationForm({ userId, onConnected }: Props) {
  const [facebookForm, setFacebookForm] = useState<FacebookForm>(initialFacebook)
  const [googleForm, setGoogleForm] = useState<GoogleForm>(initialGoogle)
  const [feedback, setFeedback] = useState<string>('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleFacebookSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setIsSubmitting(true)
    try {
      await connectFacebook(userId, facebookForm)
      setFeedback('Conta do Facebook Ads conectada com sucesso!')
      setFacebookForm(initialFacebook)
      onConnected()
    } catch (error) {
      console.error(error)
      setFeedback('Erro ao conectar Facebook Ads. Verifique o token e tente novamente.')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleGoogleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setIsSubmitting(true)
    try {
      await connectAdSense(userId, googleForm)
      setFeedback('Conta do Google AdSense conectada com sucesso!')
      setGoogleForm(initialGoogle)
      onConnected()
    } catch (error) {
      console.error(error)
      setFeedback('Erro ao conectar Google AdSense. Verifique as credenciais e tente novamente.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="integration-grid">
      <form className="integration-card" onSubmit={handleFacebookSubmit}>
        <h3>Facebook Ads</h3>
        <label>
          ID da conta de anúncios
          <input
            required
            value={facebookForm.accountId}
            onChange={(event) => setFacebookForm({ ...facebookForm, accountId: event.target.value })}
            placeholder="ex: 1234567890"
          />
        </label>
        <label>
          Access token
          <input
            required
            value={facebookForm.accessToken}
            onChange={(event) => setFacebookForm({ ...facebookForm, accessToken: event.target.value })}
            placeholder="Token válido com acesso a insights"
          />
        </label>
        <label>
          Business ID (opcional)
          <input
            value={facebookForm.businessId}
            onChange={(event) => setFacebookForm({ ...facebookForm, businessId: event.target.value })}
            placeholder="ex: 987654321"
          />
        </label>
        <button className="primary" type="submit" disabled={isSubmitting}>
          Conectar Facebook Ads
        </button>
      </form>

      <form className="integration-card" onSubmit={handleGoogleSubmit}>
        <h3>Google AdSense</h3>
        <label>
          Nome do recurso da conta
          <input
            required
            value={googleForm.accountId}
            onChange={(event) => setGoogleForm({ ...googleForm, accountId: event.target.value })}
            placeholder="accounts/pub-XXXXXXXXXXXXXXX"
          />
        </label>
        <label>
          Access token
          <input
            required
            value={googleForm.accessToken}
            onChange={(event) => setGoogleForm({ ...googleForm, accessToken: event.target.value })}
            placeholder="Token de acesso OAuth 2.0"
          />
        </label>
        <label>
          Refresh token
          <input
            required
            value={googleForm.refreshToken}
            onChange={(event) => setGoogleForm({ ...googleForm, refreshToken: event.target.value })}
          />
        </label>
        <label>
          Client ID
          <input
            required
            value={googleForm.clientId}
            onChange={(event) => setGoogleForm({ ...googleForm, clientId: event.target.value })}
          />
        </label>
        <label>
          Client secret
          <input
            required
            value={googleForm.clientSecret}
            onChange={(event) => setGoogleForm({ ...googleForm, clientSecret: event.target.value })}
          />
        </label>
        <button className="primary" type="submit" disabled={isSubmitting}>
          Conectar Google AdSense
        </button>
      </form>

      {feedback && <p className="feedback">{feedback}</p>}
    </div>
  )
}
