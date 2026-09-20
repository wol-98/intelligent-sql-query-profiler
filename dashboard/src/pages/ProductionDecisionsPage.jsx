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

function formatLabel(value) {
  if (!value) return "Not available";

  return value
    .replaceAll("_", " ")
    .toLowerCase()
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function DecisionBadge({ value }) {
  const classes = {
    RECOMMEND: "bg-emerald-100 text-emerald-700",
    REVIEW: "bg-amber-100 text-amber-700",
    REJECT: "bg-red-100 text-red-700",
    INSUFFICIENT_EVIDENCE: "bg-slate-100 text-slate-700",
  };

  return (
    <span
      className={`inline-flex rounded-full px-2.5 py-1 text-xs font-semibold ${
        classes[value] || "bg-slate-100 text-slate-700"
      }`}
    >
      {formatLabel(value)}
    </span>
  );
}

function StatusBadge({ value }) {
  const classes = {
    PASS: "bg-emerald-100 text-emerald-700",
    BLOCK: "bg-red-100 text-red-700",
    COMPLETE: "bg-emerald-100 text-emerald-700",
    PARTIAL: "bg-amber-100 text-amber-700",
    INSUFFICIENT: "bg-slate-100 text-slate-700",
    INSUFFICIENT_EVIDENCE: "bg-slate-100 text-slate-700",
  };

  return (
    <span
      className={`inline-flex rounded-full px-2.5 py-1 text-xs font-semibold ${
        classes[value] || "bg-slate-100 text-slate-700"
      }`}
    >
      {formatLabel(value)}
    </span>
  );
}

function SummaryCard({ label, value, description }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <p className="text-sm font-medium text-slate-500">{label}</p>

      <p className="mt-2 text-3xl font-bold text-slate-900">
        {value}
      </p>

      {description && (
        <p className="mt-1 text-xs text-slate-500">
          {description}
        </p>
      )}
    </div>
  );
}

function GuardrailChecks({ checks }) {
  if (!checks?.length) {
    return (
      <p className="text-sm text-slate-500">
        No guardrail checks are available.
      </p>
    );
  }

  return (
    <div className="space-y-2">
      {checks.map((check) => (
        <div
          key={check.name}
          className="flex items-center justify-between rounded-lg border border-slate-200 px-4 py-3"
        >
          <div>
            <p className="text-sm font-medium text-slate-800">
              {formatLabel(check.name)}
            </p>

            {check.detail && (
              <p className="mt-1 text-xs text-slate-500">
                {check.detail}
              </p>
            )}
          </div>

          <StatusBadge value={check.status} />
        </div>
      ))}
    </div>
  );
}

export default function ProductionDecisionsPage() {
  const [decisions, setDecisions] = useState([]);
  const [selectedId, setSelectedId] = useState(null);

  const [decisionFilter, setDecisionFilter] = useState("ALL");
  const [evidenceFilter, setEvidenceFilter] = useState("ALL");
  const [guardrailFilter, setGuardrailFilter] = useState("ALL");

  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);

  const [error, setError] = useState(null);
  const [detailError, setDetailError] = useState(null);

  const [selectedDecision, setSelectedDecision] = useState(null);

  /*
   * Load the complete production-decision portfolio.
   *
   * The M19 decision layer remains the authority. The dashboard
   * only retrieves and displays its results.
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

      guardrailPass: decisions.filter(
        (item) => item.guardrail_status === "PASS",
      ).length,
    };
  }, [decisions]);

  const filteredDecisions = useMemo(() => {
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

      return (
        matchesDecision &&
        matchesEvidence &&
        matchesGuardrail
      );
    });
  }, [
    decisions,
    decisionFilter,
    evidenceFilter,
    guardrailFilter,
  ]);

  /*
   * The effective selection is derived from the currently visible
   * records instead of being pushed into state by an effect.
   *
   * This avoids React's set-state-in-effect lint rule and ensures
   * that filtering can never leave the detail panel pointing at a
   * recommendation that is no longer visible.
   */
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

  /*
   * Load the detail for the effective selection.
   *
   * No synchronous state updates occur when there is no selection.
   * An old request is cancelled logically so that a late response
   * cannot overwrite the currently selected recommendation.
   */
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
        <p className="text-sm text-slate-500">
          Loading production decisions...
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-xl border border-red-200 bg-red-50 p-6">
        <h2 className="text-lg font-semibold text-red-800">
          Unable to load production decisions
        </h2>

        <p className="mt-2 text-sm text-red-700">
          {error}
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">
          Production Decisions
        </h1>

        <p className="mt-1 text-sm text-slate-500">
          M19 production decision and guardrail outcomes reported
          from validated project evidence.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-6">
        <SummaryCard
          label="Total Decisions"
          value={summary.total}
          description="All recommendations"
        />

        <SummaryCard
          label="Recommend"
          value={summary.recommend}
          description="M19 decision state"
        />

        <SummaryCard
          label="Review"
          value={summary.review}
          description="Engineering review"
        />

        <SummaryCard
          label="Reject"
          value={summary.reject}
          description="M19 decision state"
        />

        <SummaryCard
          label="Insufficient Evidence"
          value={summary.insufficient}
          description="Evidence incomplete"
        />

        <SummaryCard
          label="Complete Evidence"
          value={summary.complete}
          description={`${summary.guardrailPass} guardrail-pass records`}
        />
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end">
          <div className="flex-1">
            <label
              htmlFor="decision-filter"
              className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500"
            >
              Decision
            </label>

            <select
              id="decision-filter"
              value={decisionFilter}
              onChange={(event) =>
                setDecisionFilter(event.target.value)
              }
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-700 outline-none focus:border-slate-500"
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

          <div className="flex-1">
            <label
              htmlFor="evidence-filter"
              className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500"
            >
              Evidence
            </label>

            <select
              id="evidence-filter"
              value={evidenceFilter}
              onChange={(event) =>
                setEvidenceFilter(event.target.value)
              }
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-700 outline-none focus:border-slate-500"
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

          <div className="flex-1">
            <label
              htmlFor="guardrail-filter"
              className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500"
            >
              Guardrails
            </label>

            <select
              id="guardrail-filter"
              value={guardrailFilter}
              onChange={(event) =>
                setGuardrailFilter(event.target.value)
              }
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-700 outline-none focus:border-slate-500"
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

          <div className="text-sm text-slate-500">
            Showing{" "}
            <span className="font-semibold text-slate-800">
              {filteredDecisions.length}
            </span>{" "}
            of {decisions.length}
          </div>
        </div>
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
        <div className="rounded-xl border border-slate-200 bg-white shadow-sm">
          <div className="border-b border-slate-200 px-5 py-4">
            <h2 className="font-semibold text-slate-900">
              Decision Explorer
            </h2>

            <p className="mt-1 text-xs text-slate-500">
              Select a recommendation to inspect its production
              decision.
            </p>
          </div>

          <div className="divide-y divide-slate-100">
            {filteredDecisions.length === 0 ? (
              <div className="px-5 py-10 text-center text-sm text-slate-500">
                No decisions match the selected filters.
              </div>
            ) : (
              filteredDecisions.map((item) => {
                const selected =
                  item.recommendation_id ===
                  effectiveSelectedId;

                return (
                  <button
                    key={item.recommendation_id}
                    type="button"
                    onClick={() =>
                      setSelectedId(item.recommendation_id)
                    }
                    className={`w-full px-5 py-4 text-left transition ${
                      selected
                        ? "bg-slate-50"
                        : "hover:bg-slate-50"
                    }`}
                  >
                    <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                      <div>
                        <p className="text-sm font-semibold text-slate-900">
                          Recommendation #
                          {item.recommendation_id}
                        </p>

                        <div className="mt-2 flex flex-wrap gap-2">
                          <DecisionBadge value={item.state} />
                          <StatusBadge
                            value={item.evidence_status}
                          />
                          <StatusBadge
                            value={item.guardrail_status}
                          />
                        </div>
                      </div>

                      <span className="text-xs text-slate-400">
                        View details →
                      </span>
                    </div>

                    <p className="mt-3 line-clamp-2 text-sm text-slate-600">
                      {item.reason ||
                        "No decision explanation available."}
                    </p>
                  </button>
                );
              })
            )}
          </div>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white shadow-sm">
          <div className="border-b border-slate-200 px-5 py-4">
            <h2 className="font-semibold text-slate-900">
              Decision Detail
            </h2>

            <p className="mt-1 text-xs text-slate-500">
              Reported decision evidence and guardrail results.
            </p>
          </div>

          {detailLoading ? (
            <div className="p-6 text-sm text-slate-500">
              Loading decision details...
            </div>
          ) : detailError ? (
            <div className="p-6 text-sm text-red-700">
              {detailError}
            </div>
          ) : selectedDecision &&
            selectedDecision.recommendation_id ===
              effectiveSelectedId ? (
            <div className="space-y-6 p-5">
              <div>
                <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                  Recommendation
                </p>

                <p className="mt-1 text-xl font-bold text-slate-900">
                  #{selectedDecision.recommendation_id}
                </p>
              </div>

              <div className="flex flex-wrap gap-2">
                <DecisionBadge
                  value={selectedDecision.state}
                />

                <StatusBadge
                  value={selectedDecision.evidence_status}
                />

                <StatusBadge
                  value={selectedDecision.guardrail_status}
                />
              </div>

              <div>
                <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                  Decision Reason
                </p>

                <div className="mt-2 rounded-lg bg-slate-50 p-4">
                  <p className="text-sm leading-6 text-slate-700">
                    {selectedDecision.reason ||
                      "No decision explanation available."}
                  </p>
                </div>
              </div>

              <div>
                <div className="mb-3">
                  <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                    Guardrail Checks
                  </p>

                  <p className="mt-1 text-xs text-slate-500">
                    Six production guardrails reported by the M19
                    decision layer.
                  </p>
                </div>

                <GuardrailChecks
                  checks={selectedDecision.guardrail_checks}
                />
              </div>
            </div>
          ) : (
            <div className="p-6 text-sm text-slate-500">
              Select a recommendation to view its decision.
            </div>
          )}
        </div>
      </div>

      <div className="rounded-xl border border-slate-200 bg-slate-50 p-5">
        <p className="text-sm font-semibold text-slate-800">
          Reporting boundary
        </p>

        <p className="mt-1 text-sm leading-6 text-slate-600">
          This dashboard reports the production decisions produced
          by the validated M19 decision and guardrail layers. It does
          not recalculate recommendation scores, cost-benefit
          outcomes, evidence linkage, or guardrail status.
        </p>
      </div>
    </div>
  );
}
