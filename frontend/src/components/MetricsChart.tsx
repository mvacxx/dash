import { ResponsiveContainer, AreaChart, CartesianGrid, XAxis, YAxis, Tooltip, Area } from 'recharts'
import { formatCurrency, formatPercentage } from '../services/formatters'

export type ChartMetric = {
  metricDate: string
  spend: number
  revenue: number
  roi: number
}

type Props = {
  metrics: ChartMetric[]
  isLoading: boolean
}

export function MetricsChart({ metrics, isLoading }: Props) {
  if (isLoading) {
    return <p>Carregando gráfico...</p>
  }

  if (!metrics.length) {
    return <p>Nenhum dado encontrado para o período selecionado.</p>
  }

  const chartData = metrics.map((metric) => ({
    date: metric.metricDate,
    spend: metric.spend,
    revenue: metric.revenue,
    roi: metric.roi * 100,
  }))

  return (
    <ResponsiveContainer width="100%" height={360}>
      <AreaChart data={chartData} margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
        <defs>
          <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#4CAF50" stopOpacity={0.8} />
            <stop offset="95%" stopColor="#4CAF50" stopOpacity={0} />
          </linearGradient>
          <linearGradient id="colorSpend" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#2196F3" stopOpacity={0.8} />
            <stop offset="95%" stopColor="#2196F3" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
        <XAxis dataKey="date" stroke="#9e9e9e" />
        <YAxis yAxisId="left" stroke="#9e9e9e" tickFormatter={(value) => formatCurrency(value)} />
        <YAxis yAxisId="right" orientation="right" stroke="#9e9e9e" tickFormatter={(value) => `${value}%`} />
        <Tooltip
          formatter={(value: number, name: string) => {
            if (name === 'roi') {
              return [formatPercentage(value / 100), 'ROI']
            }
            return [formatCurrency(value), name === 'revenue' ? 'Receita' : 'Investimento']
          }}
        />
        <Area type="monotone" dataKey="revenue" stroke="#4CAF50" fillOpacity={1} fill="url(#colorRevenue)" yAxisId="left" name="revenue" />
        <Area type="monotone" dataKey="spend" stroke="#2196F3" fillOpacity={1} fill="url(#colorSpend)" yAxisId="left" name="spend" />
        <Area type="monotone" dataKey="roi" stroke="#FF9800" fillOpacity={0.2} fill="#FF9800" yAxisId="right" name="roi" />
      </AreaChart>
    </ResponsiveContainer>
  )
}
