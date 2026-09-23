import { useEffect, useMemo, useState } from 'react'
import { getQueries } from '../api/client'
import KpiCard from '../components/ui/KpiCard'
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

  function clearFilters() {
    setSearch('')
    setQueryType('ALL')
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <section className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
          <div className="p-7 lg:p-8">
            <div className="h-3 w-40 animate-pulse rounded-full bg-slate-200" />
            <div className="mt-4 h-9 w-80 animate-pulse rounded-lg bg-slate-200" />
            <div className="mt-3 h-4 w-[32rem] max-w-full animate-pulse rounded-full bg-slate-100" />
          </div>
        </section>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3].map((item) => (
            <div
              key={item}
              className="h-32 animate-pulse rounded-2xl border border-slate-200 bg-white shadow-sm"
            />
          ))}
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
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
        <section className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
          <div className="flex flex-col gap-6 p-7 lg:flex-row lg:items-center lg:justify-between lg:p-8">
            <div>
              <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em] text-blue-600">
                <span className="h-2 w-2 rounded-full bg-blue-500" />
                Query intelligence
              </div>
              <h1 className="mt-3 text-3xl font-bold tracking-tight text-slate-950">
                Query Performance Explorer
              </h1>
              <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
                Explore profiled SQL queries and their execution
                characteristics.
              </p>
            </div>
          </div>
        </section>

        <div className="rounded-2xl border border-rose-200 bg-rose-50 p-6 shadow-sm">
          <p className="text-sm font-semibold text-rose-800">
            Unable to load queries.
          </p>
          <p className="mt-1 text-sm text-rose-700">
            {error}
          </p>
        </div>
      </div>
    )
  }

  const queryTypeCount = Math.max(queryTypes.length - 1, 0)

  return (
    <div className="space-y-7">
      <section className="relative overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
        <div className="absolute right-0 top-0 h-40 w-72 rounded-bl-full bg-gradient-to-br from-blue-50 via-indigo-50 to-transparent" />

        <div className="relative flex flex-col gap-7 p-7 lg:flex-row lg:items-center lg:justify-between lg:p-8">
          <div>
            <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em] text-blue-600">
              <span className="h-2 w-2 rounded-full bg-blue-500" />
              Query intelligence
            </div>

            <h1 className="mt-3 text-3xl font-bold tracking-tight text-slate-950">
              Query Performance Explorer
            </h1>

            <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
              Explore profiled SQL queries, execution characteristics,
              execution plans, and associated recommendations.
            </p>
          </div>

          <div className="relative min-w-[190px] rounded-2xl border border-blue-100 bg-blue-50/70 p-5 shadow-sm">
            <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-blue-500">
              Inventory
            </p>
            <p className="mt-2 text-3xl font-bold tracking-tight text-slate-950">
              {queries.length}
            </p>
            <p className="mt-1 text-xs text-slate-400">
              query profiles available
            </p>
          </div>
        </div>
      </section>

      <section>
        <div className="mb-4">
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em] text-blue-600">
            <span className="h-2 w-2 rounded-full bg-blue-500" />
            Query snapshot
          </div>
          <h2 className="mt-2 text-xl font-bold tracking-tight text-slate-950">
            Profile activity
          </h2>
          <p className="mt-1 text-sm text-slate-500">
            Current query-profile inventory and the active filtered view.
          </p>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <KpiCard
            label="Query Profiles"
            value={queries.length}
            description="Profiles reported by the query API"
            tone="default"
          />

          <KpiCard
            label="Visible Profiles"
            value={filteredQueries.length}
            description="Profiles matching the current filters"
            tone="default"
          />

          <KpiCard
            label="Query Types"
            value={queryTypeCount}
            description="Distinct query types represented"
            tone="default"
          />
        </div>
      </section>

      <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm lg:p-6">
        <div className="flex flex-col gap-1">
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em] text-cyan-600">
            <span className="h-2 w-2 rounded-full bg-cyan-500" />
            Query explorer
          </div>
          <h2 className="text-lg font-bold text-slate-950">
            Find a profiled query
          </h2>
          <p className="text-sm text-slate-500">
            Search by SQL, fingerprint, table, or profile ID.
          </p>
        </div>

        <div className="mt-5 grid gap-4 lg:grid-cols-[minmax(0,1fr)_220px]">
          <div>
            <label
              htmlFor="query-search"
              className="mb-2 block text-[11px] font-semibold uppercase tracking-[0.16em] text-slate-400"
            >
              Search
            </label>

            <div className="relative">
              <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">
                ⌕
              </span>
              <input
                id="query-search"
                type="text"
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                placeholder="Search SQL, fingerprint, table, or profile ID..."
                className="w-full rounded-xl border border-slate-200 bg-slate-50 py-3 pl-9 pr-4 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 hover:border-slate-300 focus:border-blue-400 focus:bg-white focus:ring-4 focus:ring-blue-50"
              />
            </div>
          </div>

          <div>
            <label
              htmlFor="query-type"
              className="mb-2 block text-[11px] font-semibold uppercase tracking-[0.16em] text-slate-400"
            >
              Query Type
            </label>

            <select
              id="query-type"
              value={queryType}
              onChange={(event) => setQueryType(event.target.value)}
              className="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm font-medium text-slate-700 outline-none transition hover:border-slate-300 focus:border-blue-400 focus:bg-white focus:ring-4 focus:ring-blue-50"
            >
              {queryTypes.map((type) => (
                <option key={type} value={type}>
                  {type}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="mt-5 flex flex-col gap-3 border-t border-slate-100 pt-4 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-xs text-slate-400">
            Showing{' '}
            <span className="font-semibold text-slate-600">
              {filteredQueries.length}
            </span>{' '}
            of{' '}
            <span className="font-semibold text-slate-600">
              {queries.length}
            </span>{' '}
            query profiles.
          </p>

          {(search || queryType !== 'ALL') && (
            <button
              type="button"
              onClick={clearFilters}
              className="w-fit rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-slate-600 transition hover:border-blue-200 hover:bg-blue-50 hover:text-blue-700"
            >
              Clear filters
            </button>
          )}
        </div>
      </section>

      <section>
        <div className="mb-4 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em] text-violet-600">
              <span className="h-2 w-2 rounded-full bg-violet-500" />
              Profile register
            </div>
            <h2 className="mt-2 text-xl font-bold tracking-tight text-slate-950">
              Query profiles
            </h2>
            <p className="mt-1 text-sm text-slate-500">
              Select a profile to inspect its execution evidence.
            </p>
          </div>

          <span className="w-fit rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-500 shadow-sm">
            {filteredQueries.length} visible
          </span>
        </div>

        <QueryTable
          queries={filteredQueries}
          selectedFingerprint={selectedFingerprint}
          onSelect={handleSelectQuery}
        />
      </section>

      <QueryDetail
        query={selectedQuery}
        onRecommendationSelect={handleRecommendationSelect}
      />
    </div>
  )
}

export default QueriesPage
