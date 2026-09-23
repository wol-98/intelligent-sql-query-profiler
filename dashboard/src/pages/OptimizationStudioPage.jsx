import { useState } from 'react'

import { postOptimizationBlueprint } from '../api/client'

const DEFAULT_SCHEMA = 'public'

function formatLabel(value) {
  return String(value)
    .replaceAll('_', ' ')
    .replace(/\b\w/g, (letter) => letter.toUpperCase())
}

function isCodeField(key) {
  return /sql|ddl|query|statement/i.test(key)
}

function renderValue(value, key = '') {
  if (value === null || value === undefined) {
    return <span className="text-slate-400">Not available</span>
  }

  if (typeof value === 'boolean') {
    return (
      <span className={value ? 'text-emerald-700' : 'text-slate-600'}>
        {value ? 'Yes' : 'No'}
      </span>
    )
  }

  if (typeof value === 'string' || typeof value === 'number') {
    if (isCodeField(key) && typeof value === 'string') {
      return (
        <pre className="mt-2 overflow-x-auto rounded-xl bg-slate-950 p-4 text-xs leading-6 text-slate-100">
          <code>{value}</code>
        </pre>
      )
    }

    return (
      <span className="break-words text-sm leading-6 text-slate-700">
        {String(value)}
      </span>
    )
  }

  if (Array.isArray(value)) {
    if (value.length === 0) {
      return <span className="text-slate-400">None</span>
    }

    return (
      <div className="mt-2 space-y-2">
        {value.map((item, index) => (
          <div
            key={`${key}-${index}`}
            className="rounded-lg border border-slate-200 bg-slate-50 p-3"
          >
            {typeof item === 'object' && item !== null
              ? renderObject(item)
              : renderValue(item, key)}
          </div>
        ))}
      </div>
    )
  }

  if (typeof value === 'object') {
    return renderObject(value)
  }

  return <span className="text-sm text-slate-700">{String(value)}</span>
}

function renderObject(value) {
  return (
    <div className="space-y-3">
      {Object.entries(value).map(([key, nestedValue]) => (
        <div key={key}>
          <p className="text-[0.66rem] font-bold uppercase tracking-[0.08em] text-slate-400">
            {formatLabel(key)}
          </p>
          <div className="mt-1">{renderValue(nestedValue, key)}</div>
        </div>
      ))}
    </div>
  )
}

function SectionCard({ section, index }) {
  const { section: title, ...content } = section

  return (
    <section className="dashboard-card overflow-hidden">
      <div className="border-b border-slate-200 bg-slate-50/70 px-5 py-4">
        <div className="flex flex-wrap items-center gap-3">
          <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-blue-600 text-xs font-bold text-white">
            {index + 1}
          </span>

          <h3 className="text-sm font-bold tracking-tight text-slate-900">
            {title}
          </h3>
        </div>
      </div>

      <div className="space-y-5 p-5">
        {Object.entries(content).map(([key, value]) => (
          <div key={key}>
            <p className="text-[0.66rem] font-bold uppercase tracking-[0.08em] text-slate-400">
              {formatLabel(key)}
            </p>

            <div className="mt-1">
              {renderValue(value, key)}
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}

function OptimizationStudioPage() {
  const [sql, setSql] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  async function handleSubmit(event) {
    event.preventDefault()

    const normalizedSql = sql.trim()

    if (!normalizedSql) {
      setError('Enter a SQL query before starting the analysis.')
      setResult(null)
      return
    }

    try {
      setLoading(true)
      setError(null)

      const data = await postOptimizationBlueprint({
        raw_sql: normalizedSql,
        target_schema: DEFAULT_SCHEMA,
        enforce_safety_guardrails: true,
      })

      setResult(data)
    } catch (requestError) {
      setResult(null)
      setError(requestError.message)
    } finally {
      setLoading(false)
    }
  }

  function clearStudio() {
    setSql('')
    setResult(null)
    setError(null)
  }

  const sections = result?.sections ?? []

  return (
    <div className="space-y-6">
      <section className="dashboard-page-header mb-0">
        <div className="relative z-10">
          <div className="mb-2 flex flex-wrap items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-cyan-500 shadow-[0_0_0_4px_rgba(6,182,212,0.10)]" />

            <span className="text-[0.68rem] font-bold uppercase tracking-[0.12em] text-cyan-700">
              M21.16 · Interactive SQL Optimization
            </span>
          </div>

          <h2 className="text-[1.7rem] font-bold tracking-[-0.03em] text-slate-950">
            SQL Optimization Studio
          </h2>

          <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-500">
            Submit PostgreSQL SQL for structural analysis, candidate generation,
            evidence-aware benchmarking, and the five-section optimization report.
          </p>
        </div>
      </section>

      <section className="dashboard-card overflow-hidden">
        <form onSubmit={handleSubmit}>
          <div className="border-b border-slate-200 px-5 py-4">
            <div className="flex flex-wrap items-end justify-between gap-4">
              <div>
                <h3 className="dashboard-section-title">
                  SQL input
                </h3>

                <p className="dashboard-section-description">
                  The current studio submits the query through the existing M21
                  validation and optimization pipeline.
                </p>
              </div>

              <div className="rounded-xl border border-slate-200 bg-slate-50 px-3 py-2">
                <p className="text-[0.62rem] font-bold uppercase tracking-[0.1em] text-slate-400">
                  Target schema
                </p>

                <p className="mt-0.5 text-xs font-semibold text-slate-700">
                  {DEFAULT_SCHEMA}
                </p>
              </div>
            </div>
          </div>

          <div className="p-5">
            <textarea
              value={sql}
              onChange={(event) => setSql(event.target.value)}
              className="min-h-[260px] w-full resize-y rounded-2xl border border-slate-200 bg-slate-950 p-5 font-mono text-sm leading-6 text-slate-100 shadow-inner outline-none transition focus:border-blue-400 focus:ring-4 focus:ring-blue-100"
              placeholder={`SELECT *
FROM products
WHERE price > 100;`}
              spellCheck="false"
              aria-label="SQL query"
            />

            <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
              <p className="text-xs leading-5 text-slate-400">
                Safety guardrails are enforced for this studio request.
              </p>

              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={clearStudio}
                  disabled={loading && !result}
                  className="rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-xs font-semibold text-slate-600 shadow-sm hover:bg-slate-50 disabled:opacity-50"
                >
                  Clear
                </button>

                <button
                  type="submit"
                  disabled={loading || sql.trim().length === 0}
                  className="rounded-xl bg-blue-600 px-5 py-2.5 text-xs font-semibold text-white shadow-sm hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {loading ? 'Analyzing SQL…' : 'Analyze SQL'}
                </button>
              </div>
            </div>
          </div>
        </form>
      </section>

      {error && (
        <section className="rounded-2xl border border-rose-200 bg-white p-5 shadow-sm">
          <div className="flex items-start gap-3">
            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-rose-50 font-bold text-rose-600">
              !
            </div>

            <div>
              <h3 className="text-sm font-bold text-slate-900">
                SQL optimization request failed
              </h3>

              <p className="mt-1 text-sm leading-6 text-rose-700">
                {error}
              </p>
            </div>
          </div>
        </section>
      )}

      {loading && (
        <section className="dashboard-card p-6">
          <div className="flex items-center gap-3">
            <span className="h-2 w-2 animate-pulse rounded-full bg-blue-500" />

            <p className="text-sm font-medium text-slate-500">
              Running the M21 optimization pipeline…
            </p>
          </div>
        </section>
      )}

      {result && !loading && (
        <>
          <section className="dashboard-card p-5">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div>
                <h3 className="dashboard-section-title">
                  Optimization report
                </h3>

                <p className="dashboard-section-description">
                  Evidence and candidate status are shown exactly as returned by
                  the optimization pipeline.
                </p>
              </div>

              <div className="rounded-full border border-slate-200 bg-slate-50 px-3 py-1.5 text-[0.68rem] font-semibold text-slate-600">
                {sections.length} sections
              </div>
            </div>
          </section>

          <div className="space-y-5">
            {sections.map((section, index) => (
              <SectionCard
                key={section.section || index}
                section={section}
                index={index}
              />
            ))}
          </div>
        </>
      )}
    </div>
  )
}

export default OptimizationStudioPage
