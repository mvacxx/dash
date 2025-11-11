import { useCallback, useMemo, useState } from 'react'
import { differenceInCalendarDays, format, parseISO } from 'date-fns'
import { MetricsChart } from './components/MetricsChart'
import { MetricsSummary } from './components/MetricsSummary'
import { useMetrics } from './hooks/useMetrics'
import { IntegrationForm } from './components/IntegrationForm'

const DEFAULT_RANGE = {
  start: format(new Date(), 'yyyy-MM-01'),
  end: format(new Date(), 'yyyy-MM-dd'),
}

export default function App() {
  const [userId, setUserId] = useState<number>(1)
  const [startDate, setStartDate] = useState<string>(DEFAULT_RANGE.start)
  const [endDate, setEndDate] = useState<string>(DEFAULT_RANGE.end)

  const { data, isLoading, error, refetch } = useMetrics({
    userId,
    startDate,
    endDate,
  })

  const onRefresh = useCallback(() => {
    refetch()
  }, [refetch])

  const rangeLabel = useMemo(() => {
    const days = differenceInCalendarDays(parseISO(endDate), parseISO(startDate)) + 1
    return `${startDate} até ${endDate} (${days} dias)`
  }, [startDate, endDate])

  return (
    <div className="app-container">
      <header className="header">
        <div>
          <h1>Marketing Insights Dashboard</h1>
          <p>Conecte suas contas do Facebook Ads e Google AdSense para visualizar ROI diário.</p>
        </div>
        <div className="user-selector">
          <label htmlFor="userId">Usuário</label>
          <input
            id="userId"
            type="number"
            min={1}
            value={userId}
            onChange={(event) => setUserId(Number(event.target.value))}
          />
        </div>
      </header>

      <main className="layout">
        <section className="panel">
          <h2>Integrações</h2>
          <IntegrationForm userId={userId} onConnected={onRefresh} />
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
