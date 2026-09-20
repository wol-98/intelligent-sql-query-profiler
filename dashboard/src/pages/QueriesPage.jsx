import { useEffect, useMemo, useState } from 'react'
import { getQueries } from '../api/client'
import QueryTable from '../components/queries/QueryTable'
import QueryDetail from '../components/queries/QueryDetail'

function QueriesPage({ onNavigateToRecommendation }) {
  const [queries, setQueries] = useState([])
  const [selectedFingerprint, setSelectedFingerprint] = useState(null)
  const [search, setSearch] = useState('')
  const [queryType, setQueryType] = useState('ALL')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false

    async function loadQueries() {
      try {
        setLoading(true)
        setError(null)

        const data = await getQueries()

        if (!cancelled) {
          setQueries(data)

          if (data.length > 0) {
            setSelectedFingerprint(data[0].fingerprint)
          }
        }
      } catch (err) {
        if (!cancelled) {
          setError(err.message || 'Failed to load queries.')
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    loadQueries()

    return () => {
      cancelled = true
    }
  }, [])

  const queryTypes = useMemo(() => {
    return [
      'ALL',
      ...Array.from(
        new Set(queries.map((query) => query.query_type))
      ).sort(),
    ]
  }, [queries])

  const filteredQueries = useMemo(() => {
    const normalizedSearch = search.trim().toLowerCase()

    return queries.filter((query) => {
      const matchesType =
        queryType === 'ALL' ||
        query.query_type === queryType

      if (!normalizedSearch) {
        return matchesType
      }

      const searchable = [
        query.template,
        query.query_text,
        query.fingerprint,
        query.table_name,
        String(query.query_profile_id),
      ]
        .filter(Boolean)
        .join(' ')
        .toLowerCase()

      return matchesType && searchable.includes(normalizedSearch)
    })
  }, [queries, search, queryType])

  const selectedQuery = useMemo(() => {
    return (
      queries.find(
        (query) => query.fingerprint === selectedFingerprint
      ) || null
    )
  }, [queries, selectedFingerprint])

  function handleSelectQuery(query) {
    setSelectedFingerprint(query.fingerprint)
  }

  function handleRecommendationSelect(recommendationId) {
    if (onNavigateToRecommendation) {
      onNavigateToRecommendation(recommendationId)
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">
            Queries
          </h1>
          <p className="mt-1 text-sm text-slate-500">
            Loading profiled SQL queries...
          </p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-8">
          <p className="text-sm text-slate-500">
            Loading query profiles...
          </p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">
            Queries
          </h1>
          <p className="mt-1 text-sm text-slate-500">
            Explore profiled SQL queries and execution characteristics.
          </p>
        </div>

        <div className="rounded-xl border border-red-200 bg-red-50 p-6">
          <p className="text-sm font-medium text-red-800">
            Unable to load queries.
          </p>
          <p className="mt-1 text-sm text-red-700">
            {error}
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900">
          Queries
        </h1>
        <p className="mt-1 text-sm text-slate-500">
          Explore profiled SQL queries and execution characteristics.
        </p>
      </div>

      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <div className="rounded-xl border border-slate-200 bg-white p-5">
          <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
            Query Profiles
          </p>
          <p className="mt-2 text-2xl font-semibold text-slate-900">
            {queries.length}
          </p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-5">
          <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
            Visible Profiles
          </p>
          <p className="mt-2 text-2xl font-semibold text-slate-900">
            {filteredQueries.length}
          </p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-5">
          <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
            Query Types
          </p>
          <p className="mt-2 text-2xl font-semibold text-slate-900">
            {Math.max(queryTypes.length - 1, 0)}
          </p>
        </div>
      </section>

      <section className="rounded-xl border border-slate-200 bg-white p-5">
        <div className="flex flex-col gap-4 md:flex-row">
          <div className="flex-1">
            <label
              htmlFor="query-search"
              className="mb-2 block text-xs font-medium uppercase tracking-wide text-slate-500"
            >
              Search
            </label>

            <input
              id="query-search"
              type="text"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search SQL, fingerprint, table, or profile ID..."
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-900 outline-none transition focus:border-slate-500 focus:ring-1 focus:ring-slate-500"
            />
          </div>

          <div className="md:w-48">
            <label
              htmlFor="query-type"
              className="mb-2 block text-xs font-medium uppercase tracking-wide text-slate-500"
            >
              Query Type
            </label>

            <select
              id="query-type"
              value={queryType}
              onChange={(event) => setQueryType(event.target.value)}
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 outline-none transition focus:border-slate-500 focus:ring-1 focus:ring-slate-500"
            >
              {queryTypes.map((type) => (
                <option key={type} value={type}>
                  {type}
                </option>
              ))}
            </select>
          </div>
        </div>
      </section>

      <QueryTable
        queries={filteredQueries}
        selectedFingerprint={selectedFingerprint}
        onSelect={handleSelectQuery}
      />

      <QueryDetail
        query={selectedQuery}
        onRecommendationSelect={handleRecommendationSelect}
      />
    </div>
  )
}

export default QueriesPage
