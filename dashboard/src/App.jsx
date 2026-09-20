import { useState } from 'react'
import CostBenefitPage from './pages/CostBenefitPage'
import CompositeIndexesPage from './pages/CompositeIndexesPage'
import ProductionDecisionsPage from './pages/ProductionDecisionsPage'
import QueriesPage from './pages/QueriesPage'
import BenchmarksPage from './pages/BenchmarksPage'
import EvidenceProvenancePage from './pages/EvidenceProvenancePage'

import AppShell from './components/layout/AppShell'
import OverviewPage from './pages/OverviewPage'
import RecommendationDetailPage from './pages/RecommendationDetailPage'
import RecommendationsPage from './pages/RecommendationsPage'
import WorkloadsPage from './pages/WorkloadsPage'

function App() {
  const [activePage, setActivePage] = useState('overview')
  const [selectedRecommendationId, setSelectedRecommendationId] =
    useState(null)
  const [recommendationSourcePage, setRecommendationSourcePage] =
    useState(null)

  function navigate(page) {
    setActivePage(page)
    setSelectedRecommendationId(null)
    setRecommendationSourcePage(null)
  }

  function openRecommendation(recommendationId, sourcePage = activePage) {
    setSelectedRecommendationId(recommendationId)
    setRecommendationSourcePage(sourcePage)
  }

  function closeRecommendation() {
    setSelectedRecommendationId(null)
    setRecommendationSourcePage(null)
  }

  function renderPage() {
    if (selectedRecommendationId !== null) {
      return (
        <RecommendationDetailPage
         recommendationId={selectedRecommendationId}
         sourcePage={recommendationSourcePage}
         onBack={closeRecommendation}
         onViewBenchmark={() => {
           setActivePage('benchmarks')
           setSelectedRecommendationId(null)
           setRecommendationSourcePage(null)
        }}
      />
    )
  }

  // existing page routing continues...

    if (activePage === 'workloads') {
      return (
        <WorkloadsPage
          onSelectRecommendation={(recommendationId) =>
            openRecommendation(recommendationId, 'workloads')
          }
        />
      )
    }

    if (activePage === 'cost-benefit') {
      return <CostBenefitPage />
    }

    if (activePage === 'composite-indexes') {
      return <CompositeIndexesPage />
    }

    if (activePage === 'production-decisions') {
      return <ProductionDecisionsPage />
    }
    if (activePage === 'queries') {
      return (
       <QueriesPage
         onNavigateToRecommendation={(recommendationId) => {
           setActivePage('recommendations')
           setSelectedRecommendationId(recommendationId)
      }}
    />
  )
}
    if (activePage === 'benchmarks') {
  return (
    <BenchmarksPage
      onNavigateToRecommendation={(recommendationId) => {
        setActivePage('recommendations')
        setSelectedRecommendationId(recommendationId)
      }}
    />
  )
}
    if (activePage === 'provenance') {
      return <EvidenceProvenancePage />
}
    if (activePage === 'recommendations') {
      return (
        <RecommendationsPage
          onSelectRecommendation={(recommendationId) =>
            openRecommendation(recommendationId, 'recommendations')
          }
        />
      )
    }

    return <OverviewPage />
  }

  return (
    <AppShell activePage={activePage} onNavigate={navigate}>
      {renderPage()}
    </AppShell>
  )
}

export default App
