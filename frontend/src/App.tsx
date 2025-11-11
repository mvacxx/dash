import { FormEvent, useCallback, useEffect, useMemo, useState } from 'react'
import { differenceInCalendarDays, format, parseISO } from 'date-fns'
import { MetricsChart } from './components/MetricsChart'
import { MetricsSummary } from './components/MetricsSummary'
import { useMetrics } from './hooks/useMetrics'
import { IntegrationForm } from './components/IntegrationForm'
import { login, registerUser, setAuthToken, listIntegrations } from './services/api'
import { User } from './types/user'
import { Integration } from './types/integration'

const DEFAULT_RANGE = {
  start: format(new Date(), 'yyyy-MM-01'),
  end: format(new Date(), 'yyyy-MM-dd'),
}

export default function App() {
  const [authUser, setAuthUser] = useState<User | null>(null)
  const [token, setToken] = useState<string>('')
  const [loginError, setLoginError] = useState<string>('')
  const [loginForm, setLoginForm] = useState({ email: '', password: '' })
  const [registerForm, setRegisterForm] = useState({ name: '', email: '', password: '' })
  const [isAuthenticating, setIsAuthenticating] = useState(false)
  const [integrations, setIntegrations] = useState<Integration[]>([])
  const [startDate, setStartDate] = useState<string>(DEFAULT_RANGE.start)
  const [endDate, setEndDate] = useState<string>(DEFAULT_RANGE.end)

  const { data, isLoading, error, refetch } = useMetrics({
    startDate,
    endDate,
    enabled: !!token,
  })

  const onRefresh = useCallback(() => {
    refetch()
  }, [refetch])

  const handleLogin = useCallback(
    async (event: FormEvent<HTMLFormElement>) => {
      event.preventDefault()
      setIsAuthenticating(true)
      setLoginError('')
      try {
        const response = await login({ email: loginForm.email, password: loginForm.password })
        setToken(response.accessToken)
        setAuthUser(response.user)
        setLoginForm({ email: '', password: '' })
      } catch (err) {
        console.error(err)
        setLoginError('Falha no login. Verifique suas credenciais.')
      } finally {
        setIsAuthenticating(false)
      }
    },
    [loginForm]
  )

  const handleRegister = useCallback(
    async (event: FormEvent<HTMLFormElement>) => {
      event.preventDefault()
      setIsAuthenticating(true)
      setLoginError('')
      try {
        await registerUser(registerForm)
        const response = await login({ email: registerForm.email, password: registerForm.password })
        setToken(response.accessToken)
        setAuthUser(response.user)
        setRegisterForm({ name: '', email: '', password: '' })
      } catch (err) {
        console.error(err)
        setLoginError('Não foi possível registrar. Email já utilizado?')
      } finally {
        setIsAuthenticating(false)
      }
    },
    [registerForm]
  )

  const handleLogout = useCallback(() => {
    setAuthToken(null)
    setToken('')
    setAuthUser(null)
    setIntegrations([])
  }, [])

  useEffect(() => {
    if (!token) {
      return
    }
    const loadIntegrations = async () => {
      try {
        const response = await listIntegrations()
        setIntegrations(response)
      } catch (err) {
        console.error(err)
      }
    }
    loadIntegrations()
  }, [token])

  const rangeLabel = useMemo(() => {
    const days = differenceInCalendarDays(parseISO(endDate), parseISO(startDate)) + 1
    return `${startDate} até ${endDate} (${days} dias)`
  }, [startDate, endDate])

  if (!authUser || !token) {
    return (
      <div className="app-container">
        <header className="header">
          <div>
            <h1>Marketing Insights Dashboard</h1>
            <p>Autentique-se para acessar seu painel personalizado.</p>
          </div>
        </header>
        <main className="layout single-column">
          <section className="panel">
            <h2>Entrar</h2>
            <form className="integration-card" onSubmit={handleLogin}>
              <label>
                Email
                <input
                  required
                  type="email"
                  value={loginForm.email}
                  onChange={(event) => setLoginForm({ ...loginForm, email: event.target.value })}
                />
              </label>
              <label>
                Senha
                <input
                  required
                  type="password"
                  value={loginForm.password}
                  onChange={(event) => setLoginForm({ ...loginForm, password: event.target.value })}
                />
              </label>
              <button className="primary" type="submit" disabled={isAuthenticating}>
                Entrar
              </button>
            </form>
          </section>
          <section className="panel">
            <h2>Registrar</h2>
            <form className="integration-card" onSubmit={handleRegister}>
              <label>
                Nome
                <input
                  required
                  value={registerForm.name}
                  onChange={(event) => setRegisterForm({ ...registerForm, name: event.target.value })}
                />
              </label>
              <label>
                Email
                <input
                  required
                  type="email"
                  value={registerForm.email}
                  onChange={(event) => setRegisterForm({ ...registerForm, email: event.target.value })}
                />
              </label>
              <label>
                Senha
                <input
                  required
                  type="password"
                  value={registerForm.password}
                  onChange={(event) => setRegisterForm({ ...registerForm, password: event.target.value })}
                />
              </label>
              <button className="primary" type="submit" disabled={isAuthenticating}>
                Criar conta
              </button>
            </form>
          </section>
          {loginError && <p className="error">{loginError}</p>}
        </main>
      </div>
    )
  }

  return (
    <div className="app-container">
      <header className="header">
        <div>
          <h1>Marketing Insights Dashboard</h1>
          <p>Conecte suas contas do Facebook Ads e Google AdSense para visualizar ROI diário.</p>
        </div>
        <div className="user-selector">
          <p>Autenticado como {authUser.name}</p>
          <button onClick={handleLogout}>Sair</button>
        </div>
      </header>

      <main className="layout">
        <section className="panel">
          <h2>Integrações</h2>
          <IntegrationForm onConnected={() => {
            onRefresh()
            listIntegrations().then(setIntegrations).catch(console.error)
          }} />
          {integrations.length > 0 && (
            <div className="integration-list">
              <h3>Conexões ativas</h3>
              <ul>
                {integrations.map((integration) => (
                  <li key={integration.id}>
                    {integration.type === 'facebook_ads' ? 'Facebook Ads' : 'Google AdSense'}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </section>

        <section className="panel">
          <h2>Resumo</h2>
          <div className="range-controls">
            <div>
              <label htmlFor="startDate">Data inicial</label>
              <input
                id="startDate"
                type="date"
                value={startDate}
                onChange={(event) => setStartDate(event.target.value)}
              />
            </div>
            <div>
              <label htmlFor="endDate">Data final</label>
              <input
                id="endDate"
                type="date"
                value={endDate}
                onChange={(event) => setEndDate(event.target.value)}
              />
            </div>
            <button className="primary" onClick={onRefresh} disabled={isLoading}>
              Atualizar
            </button>
          </div>
          <p className="range-label">{rangeLabel}</p>

          {error && <p className="error">{error}</p>}

          <MetricsSummary
            isLoading={isLoading}
            totalRevenue={data?.totalRevenue ?? 0}
            totalSpend={data?.totalSpend ?? 0}
            averageRoi={data?.averageRoi ?? 0}
          />
        </section>

        <section className="panel full-width">
          <h2>ROI diário</h2>
          <MetricsChart metrics={data?.metrics ?? []} isLoading={isLoading} />
        </section>
      </main>
    </div>
  )
}
