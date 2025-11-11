import { formatCurrency, formatPercentage } from '../services/formatters'

type Props = {
  isLoading: boolean
  totalSpend: number
  totalRevenue: number
  averageRoi: number
}

export function MetricsSummary({ isLoading, totalSpend, totalRevenue, averageRoi }: Props) {
  return (
    <div className="summary-grid">
      <div className="summary-card">
        <span className="summary-label">Investimento</span>
        <strong>{isLoading ? '...' : formatCurrency(totalSpend)}</strong>
      </div>
      <div className="summary-card">
        <span className="summary-label">Receita</span>
        <strong>{isLoading ? '...' : formatCurrency(totalRevenue)}</strong>
      </div>
      <div className="summary-card">
        <span className="summary-label">ROI médio</span>
        <strong>{isLoading ? '...' : formatPercentage(averageRoi)}</strong>
      </div>
    </div>
  )
}
