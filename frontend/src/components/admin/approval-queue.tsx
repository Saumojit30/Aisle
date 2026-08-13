"use client";

import { useEffect, useState } from "react";
import { Check, X, ShieldAlert, RefreshCw } from "lucide-react";

interface PendingApproval {
  id: str;
  thread_id: string;
  session_id: string;
  customer_id: string;
  action_type: string;
  payload: Record<string, any>;
  status: string;
  created_at: string;
}

export function ApprovalQueue() {
  const [approvals, setApprovals] = useState<PendingApproval[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [submittingId, setSubmittingId] = useState<string | null>(null);

  const fetchApprovals = async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/admin/approvals");
      if (res.ok) {
        const data = await res.json();
        setApprovals(data);
      }
    } catch (e) {
      console.error("Failed to fetch pending approvals", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchApprovals();
    const interval = setInterval(fetchApprovals, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleRespond = async (id: string, action: "approved" | "rejected") => {
    setSubmittingId(id);
    try {
      const res = await fetch(`/api/admin/approvals/${id}/respond`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action }),
      });
      if (res.ok) {
        setApprovals((prev) => prev.filter((a) => a.id !== id));
      }
    } catch (e) {
      console.error("Failed to respond to approval", e);
    } finally {
      setSubmittingId(null);
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 text-white">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <ShieldAlert className="w-5 h-5 text-amber-400" />
          <h3 className="text-lg font-semibold">Human Approval Queue (HITL)</h3>
        </div>
        <button
          onClick={fetchApprovals}
          className="p-1.5 hover:bg-slate-800 rounded-lg text-slate-400 hover:text-white transition"
          title="Refresh"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
        </button>
      </div>

      {loading && approvals.length === 0 ? (
        <div className="py-6 text-center text-slate-400 text-sm">Loading pending requests...</div>
      ) : approvals.length === 0 ? (
        <div className="py-6 text-center text-slate-400 text-sm">
          No pending manager approvals. High-risk actions are monitored in real-time.
        </div>
      ) : (
        <div className="space-y-3">
          {approvals.map((appr) => (
            <div
              key={appr.id}
              className="bg-slate-800/80 border border-amber-500/30 rounded-lg p-4 flex flex-col md:flex-row md:items-center justify-between gap-4"
            >
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="bg-amber-500/20 text-amber-300 text-xs font-mono px-2 py-0.5 rounded">
                    {appr.action_type}
                  </span>
                  <span className="text-xs text-slate-400 font-mono">ID: {appr.id}</span>
                </div>
                <p className="text-sm text-slate-200">
                  Customer <span className="font-semibold text-white">{appr.customer_id}</span> requested{" "}
                  <span className="text-amber-300">{appr.action_type}</span>.
                </p>
                {appr.payload && (
                  <pre className="mt-1 text-xs text-slate-400 bg-slate-900/60 p-2 rounded font-mono overflow-x-auto">
                    {JSON.stringify(appr.payload, null, 2)}
                  </pre>
                )}
              </div>

              <div className="flex items-center gap-2 shrink-0">
                <button
                  disabled={submittingId === appr.id}
                  onClick={() => handleRespond(appr.id, "approved")}
                  className="flex items-center gap-1 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-medium px-3 py-2 rounded-lg transition disabled:opacity-50"
                >
                  <Check className="w-4 h-4" /> Approve
                </button>
                <button
                  disabled={submittingId === appr.id}
                  onClick={() => handleRespond(appr.id, "rejected")}
                  className="flex items-center gap-1 bg-rose-600 hover:bg-rose-500 text-white text-xs font-medium px-3 py-2 rounded-lg transition disabled:opacity-50"
                >
                  <X className="w-4 h-4" /> Reject
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
