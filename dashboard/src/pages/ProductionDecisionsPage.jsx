import { useEffect, useMemo, useState } from "react";

import {
  getProductionDecision,
  getProductionDecisions,
} from "../api/client";

const DECISION_STATES = [
  "ALL",
  "RECOMMEND",
  "REVIEW",
  "REJECT",
  "INSUFFICIENT_EVIDENCE",
];

const EVIDENCE_STATES = [
  "ALL",
  "COMPLETE",
  "PARTIAL",
  "INSUFFICIENT",
];

const GUARDRAIL_STATES = [
  "ALL",
  "PASS",
  "BLOCK",
  "INSUFFICIENT_EVIDENCE",
];

const DECISION_META = {
  RECOMMEND: {
    label: "Recommend",
    shortLabel: "Recommend",
    description: "M19 decision state",
    dot: "bg-emerald-500",
    text: "text-emerald-700",
    border: "border-emerald-200",
    soft: "bg-emerald-50",
    ring: "ring-emerald-100",
  },
  REVIEW: {
    label: "Review",
    shortLabel: "Review",
    description: "Requires engineering review",
    dot: "bg-amber-500",
    text: "text-amber-700",
    border: "border-amber-200",
    soft: "bg-amber-50",
    ring: "ring-amber-100",
  },
  REJECT: {
    label: "Reject",
    shortLabel: "Reject",
    description: "M19 decision state",
    dot: "bg-rose-500",
    text: "text-rose-700",
    border: "border-rose-200",
    soft: "bg-rose-50",
    ring: "ring-rose-100",
  },
  INSUFFICIENT_EVIDENCE: {
    label: "Insufficient Evidence",
    shortLabel: "Insufficient",
    description: "Evidence is incomplete",
    dot: "bg-slate-400",
    text: "text-slate-600",
    border: "border-slate-200",
    soft: "bg-slate-50",
    ring: "ring-slate-100",
  },
};

const STATUS_META = {
  PASS: {
    label: "Pass",
    dot: "bg-emerald-500",
    text: "text-emerald-700",
    border: "border-emerald-200",
    soft: "bg-emerald-50",
  },
  BLOCK: {
    label: "Block",
    dot: "bg-rose-500",
    text: "text-rose-700",
    border: "border-rose-200",
    soft: "bg-rose-50",
  },
  COMPLETE: {
    label: "Complete",
    dot: "bg-emerald-500",
    text: "text-emerald-700",
    border: "border-emerald-200",
    soft: "bg-emerald-50",
  },
  PARTIAL: {
    label: "Partial",
    dot: "bg-amber-500",
    text: "text-amber-700",
    border: "border-amber-200",
    soft: "bg-amber-50",
  },
  INSUFFICIENT: {
    label: "Insufficient",
    dot: "bg-slate-400",
    text: "text-slate-600",
    border: "border-slate-200",
    soft: "bg-slate-50",
  },
  INSUFFICIENT_EVIDENCE: {
    label: "Insufficient Evidence",
    dot: "bg-slate-400",
    text: "text-slate-600",
    border: "border-slate-200",
    soft: "bg-slate-50",
  },
};

function formatLabel(value) {
  if (!value) {
    return "Not available";
  }

  return value
    .replaceAll("_", " ")
    .toLowerCase()
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function DecisionBadge({ value }) {
  const meta = DECISION_META[value] || {
    label: formatLabel(value),
    dot: "bg-slate-400",
    text: "text-slate-600",
    border: "border-slate-200",
    soft: "bg-slate-50",
  };

  return (
    <span
      className={`inline-flex items-center gap-2 rounded-full border px-3 py-1.5 text-xs font-semibold ${meta.soft} ${meta.text} ${meta.border}`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${meta.dot}`} />
      {meta.label}
    </span>
  );
}

function StatusBadge({ value }) {
  const meta = STATUS_META[value] || {
    label: formatLabel(value),
    dot: "bg-slate-400",
    text: "text-slate-600",
    border: "border-slate-200",
    soft: "bg-slate-50",
  };

  return (
    <span
      className={`inline-flex items-center gap-2 rounded-full border px-3 py-1.5 text-xs font-semibold ${meta.soft} ${meta.text} ${meta.border}`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${meta.dot}`} />
      {meta.label}
    </span>
  );
}

function MetricCard({
  label,
  value,
  description,
  accent = "blue",
}) {
  const accents = {
    blue: {
      border: "border-blue-200",
      dot: "bg-blue-500",
      value: "text-slate-950",
    },
    green: {
      border: "border-emerald-200",
      dot: "bg-emerald-500",
      value: "text-emerald-700",
    },
    amber: {
      border: "border-amber-200",
      dot: "bg-amber-500",
      value: "text-amber-700",
    },
    rose: {
      border: "border-rose-200",
      dot: "bg-rose-500",
      value: "text-rose-700",
    },
    slate: {
      border: "border-slate-200",
      dot: "bg-slate-400",
      value: "text-slate-700",
    },
  };

  const meta = accents[accent] || accents.blue;

  return (
    <div
      className={`relative overflow-hidden rounded-2xl border bg-white p-5 shadow-[0_8px_24px_rgba(15,23,42,0.05)] ${meta.border}`}
    >
      <div className="absolute right-5 top-5">
        <span className={`block h-2.5 w-2.5 rounded-full ${meta.dot}`} />
      </div>

      <p className="text-[10px] font-bold uppercase tracking-[0.18em] text-slate-400">
        {label}
      </p>

      <p
        className={`mt-3 text-3xl font-bold tracking-tight ${meta.value}`}
      >
        {value}
      </p>

      <p className="mt-1 text-xs text-slate-400">
        {description}
      </p>
    </div>
  );
}

function DistributionBar({
  label,
  value,
  total,
  color,
  description,
}) {
  const percentage =
    total > 0 ? Math.max((value / total) * 100, value > 0 ? 3 : 0) : 0;

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4">
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <span className={`h-2 w-2 rounded-full ${color}`} />
          <span className="text-sm font-semibold text-slate-800">
            {label}
          </span>
        </div>

        <span className="text-sm font-bold text-slate-900">
          {value}
        </span>
      </div>

      <div className="mt-3 h-2 overflow-hidden rounded-full bg-slate-100">
        <div
          className={`h-full rounded-full transition-all duration-500 ${color}`}
          style={{ width: `${percentage}%` }}
        />
      </div>

      <p className="mt-2 text-[11px] text-slate-400">
        {description}
      </p>
    </div>
  );
}

function GuardrailChecks({ checks }) {
  if (!checks?.length) {
    return (
      <div className="rounded-xl border border-dashed border-slate-200 bg-slate-50 px-4 py-6 text-center">
        <p className="text-sm font-medium text-slate-600">
          No guardrail checks are available.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {checks.map((check) => (
        <div
          key={check.name}
          className="flex items-center justify-between gap-4 rounded-xl border border-slate-200 bg-white px-4 py-3"
        >
          <div className="min-w-0">
            <p className="text-sm font-semibold text-slate-800">
              {formatLabel(check.name)}
            </p>

            {check.detail && (
              <p className="mt-1 text-xs leading-5 text-slate-500">
                {check.detail}
              </p>
            )}
          </div>

          <div className="shrink-0">
            <StatusBadge value={check.status} />
          </div>
        </div>
      ))}
    </div>
  );
}

function DetailMetric({ label, children }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50/70 p-4">
      <p className="text-[10px] font-bold uppercase tracking-[0.16em] text-slate-400">
        {label}
      </p>

      <div className="mt-2 text-sm font-semibold text-slate-800">
        {children}
      </div>
    </div>
  );
}

export default function ProductionDecisionsPage() {
  const [decisions, setDecisions] = useState([]);
  const [selectedId, setSelectedId] = useState(null);

  const [decisionFilter, setDecisionFilter] = useState("ALL");
  const [evidenceFilter, setEvidenceFilter] = useState("ALL");
  const [guardrailFilter, setGuardrailFilter] = useState("ALL");
  const [search, setSearch] = useState("");

  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);

  const [error, setError] = useState(null);
  const [detailError, setDetailError] = useState(null);

  const [selectedDecision, setSelectedDecision] = useState(null);

  /*
   * The M19 decision layer remains the authority.
   * This page only retrieves and presents its results.
   */
  useEffect(() => {
    let cancelled = false;

    async function loadDecisions() {
      try {
        setLoading(true);
        setError(null);

        const data = await getProductionDecisions();

        if (!cancelled) {
          setDecisions(data);

          if (data.length > 0) {
            setSelectedId(data[0].recommendation_id);
          }
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err.message ||
              "Failed to load production decisions.",
          );
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadDecisions();

    return () => {
      cancelled = true;
    };
  }, []);

  const summary = useMemo(() => {
    return {
      total: decisions.length,

      recommend: decisions.filter(
        (item) => item.state === "RECOMMEND",
      ).length,

      review: decisions.filter(
        (item) => item.state === "REVIEW",
      ).length,

      reject: decisions.filter(
        (item) => item.state === "REJECT",
      ).length,

      insufficient: decisions.filter(
        (item) => item.state === "INSUFFICIENT_EVIDENCE",
      ).length,

      complete: decisions.filter(
        (item) => item.evidence_status === "COMPLETE",
      ).length,

      partial: decisions.filter(
        (item) => item.evidence_status === "PARTIAL",
      ).length,

      insufficientEvidence: decisions.filter(
        (item) => item.evidence_status === "INSUFFICIENT",
      ).length,

      guardrailPass: decisions.filter(
        (item) => item.guardrail_status === "PASS",
      ).length,

      guardrailBlock: decisions.filter(
        (item) => item.guardrail_status === "BLOCK",
      ).length,
    };
  }, [decisions]);

  const filteredDecisions = useMemo(() => {
    const normalizedSearch = search.trim().toLowerCase();

    return decisions.filter((item) => {
      const matchesDecision =
        decisionFilter === "ALL" ||
        item.state === decisionFilter;

      const matchesEvidence =
        evidenceFilter === "ALL" ||
        item.evidence_status === evidenceFilter;

      const matchesGuardrail =
        guardrailFilter === "ALL" ||
        item.guardrail_status === guardrailFilter;

      const searchableText = [
        item.recommendation_id,
        item.state,
        item.evidence_status,
        item.guardrail_status,
        item.reason,
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();

      const matchesSearch =
        !normalizedSearch ||
        searchableText.includes(normalizedSearch);

      return (
        matchesDecision &&
        matchesEvidence &&
        matchesGuardrail &&
        matchesSearch
      );
    });
  }, [
    decisions,
    decisionFilter,
    evidenceFilter,
    guardrailFilter,
    search,
  ]);

  const effectiveSelectedId = useMemo(() => {
    if (filteredDecisions.length === 0) {
      return null;
    }

    const selectedStillVisible = filteredDecisions.some(
      (item) => item.recommendation_id === selectedId,
    );

    if (selectedStillVisible) {
      return selectedId;
    }

    return filteredDecisions[0].recommendation_id;
  }, [filteredDecisions, selectedId]);

  useEffect(() => {
    if (effectiveSelectedId === null) {
      return;
    }

    let cancelled = false;

    async function loadDecision() {
      try {
        setDetailLoading(true);
        setDetailError(null);

        const data = await getProductionDecision(
          effectiveSelectedId,
        );

        if (!cancelled) {
          setSelectedDecision(data);
        }
      } catch (err) {
        if (!cancelled) {
          setDetailError(
            err.message ||
              "Failed to load decision details.",
          );
          setSelectedDecision(null);
        }
      } finally {
        if (!cancelled) {
          setDetailLoading(false);
        }
      }
    }

    loadDecision();

    return () => {
      cancelled = true;
    };
  }, [effectiveSelectedId]);

  if (loading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="text-center">
          <div className="mx-auto h-10 w-10 animate-pulse rounded-full bg-blue-100" />
          <p className="mt-4 text-sm font-medium text-slate-500">
            Loading production decisions...
          </p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-2xl border border-rose-200 bg-rose-50 p-6">
        <div className="flex items-start gap-4">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-rose-100 text-rose-600">
            !
          </div>

          <div>
            <h2 className="text-lg font-bold text-rose-900">
              Unable to load production decisions
            </h2>

            <p className="mt-1 text-sm text-rose-700">
              {error}
            </p>
          </div>
        </div>
      </div>
    );
  }

  const selectedMeta =
    selectedDecision?.state &&
    DECISION_META[selectedDecision.state]
      ? DECISION_META[selectedDecision.state]
      : DECISION_META.INSUFFICIENT_EVIDENCE;

  return (
    <div className="space-y-7 pb-10">
      {/* ---------------------------------------------------------
          HERO
      --------------------------------------------------------- */}
      <section className="relative overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-[0_12px_32px_rgba(15,23,42,0.06)]">
        <div className="absolute right-0 top-0 h-40 w-40 rounded-full bg-blue-50 blur-3xl" />
        <div className="absolute bottom-0 right-24 h-28 w-28 rounded-full bg-violet-50 blur-3xl" />

        <div className="relative flex flex-col gap-6 p-7 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <div className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-orange-500" />

              <span className="text-[10px] font-bold uppercase tracking-[0.2em] text-slate-400">
                Decision intelligence
              </span>
            </div>

            <h1 className="mt-3 text-3xl font-bold tracking-tight text-slate-950 sm:text-4xl">
              Production Decision Framework
            </h1>

            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-500">
              M19 decision and guardrail outcomes reported from the
              project's validated evidence framework.
            </p>
          </div>

          <div className="relative shrink-0 rounded-2xl border border-orange-200 bg-orange-50/70 px-6 py-5">
            <p className="text-[10px] font-bold uppercase tracking-[0.18em] text-orange-600">
              Decision register
            </p>

            <p className="mt-2 text-4xl font-bold tracking-tight text-slate-950">
              {summary.total}
            </p>

            <p className="mt-1 text-xs text-slate-500">
              recommendations evaluated by M19
            </p>
          </div>
        </div>
      </section>

      {/* ---------------------------------------------------------
          PORTFOLIO SNAPSHOT
      --------------------------------------------------------- */}
      <section>
        <div className="mb-4">
          <div className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-blue-500" />

            <span className="text-[10px] font-bold uppercase tracking-[0.2em] text-slate-400">
              Decision portfolio
            </span>
          </div>

          <h2 className="mt-2 text-xl font-bold text-slate-950">
            Decision snapshot
          </h2>

          <p className="mt-1 text-sm text-slate-500">
            Current distribution of the stored M19 decision outcomes.
          </p>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-6">
          <MetricCard
            label="Total decisions"
            value={summary.total}
            description="All recommendations"
            accent="blue"
          />

          <MetricCard
            label="Recommend"
            value={summary.recommend}
            description="M19 decision state"
            accent="green"
          />

          <MetricCard
            label="Review"
            value={summary.review}
            description="Requires review"
            accent="amber"
          />

          <MetricCard
            label="Reject"
            value={summary.reject}
            description="M19 decision state"
            accent="rose"
          />

          <MetricCard
            label="Insufficient"
            value={summary.insufficient}
            description="Evidence incomplete"
            accent="slate"
          />

          <MetricCard
            label="Complete evidence"
            value={summary.complete}
            description={`${summary.guardrailPass} guardrail-pass records`}
            accent="green"
          />
        </div>
      </section>

      {/* ---------------------------------------------------------
          DISTRIBUTION
      --------------------------------------------------------- */}
      <section className="grid gap-6 lg:grid-cols-[1.15fr_0.85fr]">
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-[0_8px_24px_rgba(15,23,42,0.04)]">
          <div className="flex items-start justify-between gap-4">
            <div>
              <div className="flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-violet-500" />

                <span className="text-[10px] font-bold uppercase tracking-[0.18em] text-slate-400">
                  Decision composition
                </span>
              </div>

              <h2 className="mt-2 text-lg font-bold text-slate-950">
                Decision outcome mix
              </h2>

              <p className="mt-1 text-sm text-slate-500">
                Distribution of the existing M19 decision states.
              </p>
            </div>

            <span className="rounded-full bg-slate-50 px-3 py-1.5 text-xs font-semibold text-slate-500">
              {summary.total} total
            </span>
          </div>

          <div className="mt-6 space-y-3">
            <DistributionBar
              label="Recommend"
              value={summary.recommend}
              total={summary.total}
              color="bg-emerald-500"
              description="M19 recommendation state"
            />

            <DistributionBar
              label="Review"
              value={summary.review}
              total={summary.total}
              color="bg-amber-500"
              description="Engineering review state"
            />

            <DistributionBar
              label="Reject"
              value={summary.reject}
              total={summary.total}
              color="bg-rose-500"
              description="M19 rejection state"
            />

            <DistributionBar
              label="Insufficient evidence"
              value={summary.insufficient}
              total={summary.total}
              color="bg-slate-400"
              description="Evidence is not complete enough for a production decision"
            />
          </div>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-[0_8px_24px_rgba(15,23,42,0.04)]">
          <div className="flex items-start gap-3">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
              <span className="h-2.5 w-2.5 rounded-full bg-blue-500" />
            </div>

            <div>
              <p className="text-[10px] font-bold uppercase tracking-[0.18em] text-slate-400">
                Evidence readiness
              </p>

              <h2 className="mt-2 text-lg font-bold text-slate-950">
                Evidence and guardrails
              </h2>

              <p className="mt-1 text-sm leading-6 text-slate-500">
                A separate view of evidence completeness and guardrail
                outcomes.
              </p>
            </div>
          </div>

          <div className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-1">
            <DetailMetric label="Complete evidence">
              {summary.complete}
            </DetailMetric>

            <DetailMetric label="Partial evidence">
              {summary.partial}
            </DetailMetric>

            <DetailMetric label="Insufficient evidence">
              {summary.insufficientEvidence}
            </DetailMetric>

            <DetailMetric label="Guardrail pass">
              <span className="text-emerald-700">
                {summary.guardrailPass}
              </span>
            </DetailMetric>

            <DetailMetric label="Guardrail block">
              <span className="text-rose-700">
                {summary.guardrailBlock}
              </span>
            </DetailMetric>
          </div>
        </div>
      </section>

      {/* ---------------------------------------------------------
          FILTERS
      --------------------------------------------------------- */}
      <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-[0_8px_24px_rgba(15,23,42,0.04)]">
        <div className="flex flex-col gap-5">
          <div className="flex flex-col gap-2 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <div className="flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-cyan-500" />

                <span className="text-[10px] font-bold uppercase tracking-[0.18em] text-slate-400">
                  Decision register
                </span>
              </div>

              <h2 className="mt-2 text-lg font-bold text-slate-950">
                Explore decisions
              </h2>
            </div>

            <p className="text-xs text-slate-400">
              Showing{" "}
              <span className="font-bold text-slate-700">
                {filteredDecisions.length}
              </span>{" "}
              of{" "}
              <span className="font-bold text-slate-700">
                {decisions.length}
              </span>{" "}
              decisions
            </p>
          </div>

          <div className="grid gap-3 lg:grid-cols-[1.4fr_1fr_1fr_1fr]">
            <div>
              <label
                htmlFor="decision-search"
                className="mb-1.5 block text-[10px] font-bold uppercase tracking-[0.16em] text-slate-400"
              >
                Search
              </label>

              <div className="relative">
                <input
                  id="decision-search"
                  type="search"
                  value={search}
                  onChange={(event) =>
                    setSearch(event.target.value)
                  }
                  placeholder="Recommendation ID, state, reason..."
                  className="w-full rounded-xl border border-slate-200 bg-slate-50/70 px-4 py-3 text-sm text-slate-700 outline-none transition placeholder:text-slate-400 focus:border-blue-300 focus:bg-white focus:ring-4 focus:ring-blue-50"
                />
              </div>
            </div>

            <div>
              <label
                htmlFor="decision-filter"
                className="mb-1.5 block text-[10px] font-bold uppercase tracking-[0.16em] text-slate-400"
              >
                Decision
              </label>

              <select
                id="decision-filter"
                value={decisionFilter}
                onChange={(event) =>
                  setDecisionFilter(event.target.value)
                }
                className="w-full rounded-xl border border-slate-200 bg-slate-50/70 px-4 py-3 text-sm text-slate-700 outline-none transition focus:border-blue-300 focus:bg-white focus:ring-4 focus:ring-blue-50"
              >
                {DECISION_STATES.map((state) => (
                  <option key={state} value={state}>
                    {state === "ALL"
                      ? "All decisions"
                      : formatLabel(state)}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label
                htmlFor="evidence-filter"
                className="mb-1.5 block text-[10px] font-bold uppercase tracking-[0.16em] text-slate-400"
              >
                Evidence
              </label>

              <select
                id="evidence-filter"
                value={evidenceFilter}
                onChange={(event) =>
                  setEvidenceFilter(event.target.value)
                }
                className="w-full rounded-xl border border-slate-200 bg-slate-50/70 px-4 py-3 text-sm text-slate-700 outline-none transition focus:border-blue-300 focus:bg-white focus:ring-4 focus:ring-blue-50"
              >
                {EVIDENCE_STATES.map((state) => (
                  <option key={state} value={state}>
                    {state === "ALL"
                      ? "All evidence states"
                      : formatLabel(state)}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label
                htmlFor="guardrail-filter"
                className="mb-1.5 block text-[10px] font-bold uppercase tracking-[0.16em] text-slate-400"
              >
                Guardrail
              </label>

              <select
                id="guardrail-filter"
                value={guardrailFilter}
                onChange={(event) =>
                  setGuardrailFilter(event.target.value)
                }
                className="w-full rounded-xl border border-slate-200 bg-slate-50/70 px-4 py-3 text-sm text-slate-700 outline-none transition focus:border-blue-300 focus:bg-white focus:ring-4 focus:ring-blue-50"
              >
                {GUARDRAIL_STATES.map((state) => (
                  <option key={state} value={state}>
                    {state === "ALL"
                      ? "All guardrail states"
                      : formatLabel(state)}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </section>

      {/* ---------------------------------------------------------
          EXPLORER + DETAIL
      --------------------------------------------------------- */}
      <section className="grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
        {/* Decision register */}
        <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-[0_8px_24px_rgba(15,23,42,0.04)]">
          <div className="border-b border-slate-200 px-5 py-5">
            <div className="flex items-center justify-between gap-3">
              <div>
                <p className="text-[10px] font-bold uppercase tracking-[0.18em] text-slate-400">
                  Decision register
                </p>

                <h2 className="mt-1 text-lg font-bold text-slate-950">
                  Recommendations
                </h2>
              </div>

              <span className="rounded-full bg-slate-100 px-3 py-1.5 text-xs font-bold text-slate-500">
                {filteredDecisions.length}
              </span>
            </div>
          </div>

          <div className="max-h-[720px] overflow-y-auto">
            {filteredDecisions.length === 0 ? (
              <div className="px-6 py-16 text-center">
                <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-100">
                  <span className="h-2.5 w-2.5 rounded-full bg-slate-400" />
                </div>

                <p className="mt-4 text-sm font-semibold text-slate-700">
                  No decisions match the current filters.
                </p>

                <p className="mt-1 text-xs text-slate-400">
                  Adjust the search or filter values to continue.
                </p>
              </div>
            ) : (
              <div className="divide-y divide-slate-100">
                {filteredDecisions.map((item) => {
                  const selected =
                    item.recommendation_id ===
                    effectiveSelectedId;

                  const meta =
                    DECISION_META[item.state] ||
                    DECISION_META.INSUFFICIENT_EVIDENCE;

                  return (
                    <button
                      key={item.recommendation_id}
                      type="button"
                      onClick={() =>
                        setSelectedId(item.recommendation_id)
                      }
                      className={`group relative w-full px-5 py-4 text-left transition ${
                        selected
                          ? "bg-blue-50/70"
                          : "hover:bg-slate-50"
                      }`}
                    >
                      {selected && (
                        <span className="absolute bottom-0 left-0 top-0 w-1 bg-blue-500" />
                      )}

                      <div className="flex items-start justify-between gap-4">
                        <div className="min-w-0">
                          <div className="flex items-center gap-2">
                            <span className="text-sm font-bold text-slate-900">
                              #{item.recommendation_id}
                            </span>

                            <DecisionBadge value={item.state} />
                          </div>

                          <p className="mt-2 text-xs text-slate-500">
                            Evidence{" "}
                            <span className="font-semibold text-slate-700">
                              {formatLabel(
                                item.evidence_status,
                              )}
                            </span>
                          </p>
                        </div>

                        <span
                          className={`mt-1 h-2 w-2 shrink-0 rounded-full ${meta.dot}`}
                        />
                      </div>

                      <div className="mt-3 grid grid-cols-2 gap-2">
                        <div className="rounded-lg bg-white/70 px-3 py-2">
                          <p className="text-[9px] font-bold uppercase tracking-[0.14em] text-slate-400">
                            Guardrail
                          </p>

                          <p className="mt-1 text-xs font-semibold text-slate-700">
                            {formatLabel(
                              item.guardrail_status,
                            )}
                          </p>
                        </div>

                        <div className="rounded-lg bg-white/70 px-3 py-2">
                          <p className="text-[9px] font-bold uppercase tracking-[0.14em] text-slate-400">
                            Record
                          </p>

                          <p className="mt-1 text-xs font-semibold text-slate-700">
                            #{item.recommendation_id}
                          </p>
                        </div>
                      </div>
                    </button>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* Decision detail */}
        <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-[0_8px_24px_rgba(15,23,42,0.04)]">
          <div
            className={`border-b px-6 py-6 ${selectedMeta.soft} ${selectedMeta.border}`}
          >
            {detailLoading ? (
              <div className="animate-pulse">
                <div className="h-3 w-32 rounded bg-white/80" />
                <div className="mt-3 h-7 w-64 rounded bg-white/80" />
                <div className="mt-2 h-4 w-96 max-w-full rounded bg-white/80" />
              </div>
            ) : selectedDecision ? (
              <>
                <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                  <div>
                    <p className="text-[10px] font-bold uppercase tracking-[0.18em] text-slate-400">
                      Selected decision
                    </p>

                    <h2 className="mt-2 text-2xl font-bold tracking-tight text-slate-950">
                      Recommendation #
                      {selectedDecision.recommendation_id}
                    </h2>

                    <p className="mt-1 text-sm text-slate-500">
                      Decision produced by the M19 production
                      optimization framework.
                    </p>
                  </div>

                  <DecisionBadge
                    value={selectedDecision.state}
                  />
                </div>
              </>
            ) : (
              <div>
                <p className="text-sm text-slate-500">
                  Select a decision to inspect its evidence.
                </p>
              </div>
            )}
          </div>

          {detailError && (
            <div className="m-5 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3">
              <p className="text-sm font-semibold text-rose-800">
                Unable to load decision details
              </p>

              <p className="mt-1 text-xs text-rose-700">
                {detailError}
              </p>
            </div>
          )}

          {selectedDecision && !detailLoading && (
            <div className="space-y-6 p-6">
              {/* Decision status */}
              <div>
                <p className="text-[10px] font-bold uppercase tracking-[0.18em] text-slate-400">
                  Decision status
                </p>

                <div className="mt-3 grid gap-3 sm:grid-cols-3">
                  <DetailMetric label="Decision">
                    <DecisionBadge
                      value={selectedDecision.state}
                    />
                  </DetailMetric>

                  <DetailMetric label="Evidence">
                    <StatusBadge
                      value={selectedDecision.evidence_status}
                    />
                  </DetailMetric>

                  <DetailMetric label="Guardrail">
                    <StatusBadge
                      value={selectedDecision.guardrail_status}
                    />
                  </DetailMetric>
                </div>
              </div>

              {/* Reason */}
              <div>
                <p className="text-[10px] font-bold uppercase tracking-[0.18em] text-slate-400">
                  Decision rationale
                </p>

                <div className="mt-3 rounded-xl border border-slate-200 bg-slate-50/70 p-5">
                  {selectedDecision.reason ? (
                    <p className="text-sm leading-6 text-slate-600">
                      {selectedDecision.reason}
                    </p>
                  ) : (
                    <p className="text-sm italic text-slate-400">
                      No decision rationale is available in the
                      reporting response.
                    </p>
                  )}
                </div>
              </div>

              {/* Guardrail checks */}
              <div>
                <div className="flex flex-col gap-1 sm:flex-row sm:items-end sm:justify-between">
                  <div>
                    <p className="text-[10px] font-bold uppercase tracking-[0.18em] text-slate-400">
                      Safety guardrails
                    </p>

                    <h3 className="mt-1 text-base font-bold text-slate-950">
                      Guardrail verification
                    </h3>
                  </div>

                  <StatusBadge
                    value={selectedDecision.guardrail_status}
                  />
                </div>

                <div className="mt-4">
                  <GuardrailChecks
                    checks={selectedDecision.guardrail_checks}
                  />
                </div>
              </div>

              {/* Evidence boundary */}
              <div className="rounded-xl border border-orange-200 bg-orange-50/60 p-5">
                <div className="flex items-start gap-3">
                  <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-orange-100">
                    <span className="h-2 w-2 rounded-full bg-orange-500" />
                  </div>

                  <div>
                    <p className="text-[10px] font-bold uppercase tracking-[0.18em] text-orange-600">
                      Evidence boundary
                    </p>

                    <h3 className="mt-1 text-sm font-bold text-slate-900">
                      Reporting framework
                    </h3>

                    <p className="mt-2 text-xs leading-5 text-slate-600">
                      This interface reports the existing M19
                      decision and guardrail results. It does not
                      create or remove database indexes, rerun
                      experiments, or modify production systems.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
