import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Legend,
} from "recharts";
import {
  FileText,
  Scale,
  BookOpen,
  Gavel,
  X,
  User,
  Calendar,
  Building2,
  Hash,
  CheckCircle2,
  AlertTriangle,
  MessageCircle,
} from "lucide-react";

const COLORS = ["#6c63ff", "#34d399", "#f87171", "#fbbf24", "#60a5fa", "#a78bfa"];

const TOOLTIP_STYLE = {
  background: "#1a1d27",
  border: "1px solid #2d3144",
  borderRadius: 8,
  color: "#e4e6ef",
};

function ChartCard({ title, icon, children }) {
  return (
    <div className="insight-card">
      <h3 className="insight-card-title">
        {icon} {title}
      </h3>
      {children}
    </div>
  );
}

function MetaRow({ icon, label, value }) {
  if (!value || (Array.isArray(value) && value.length === 0)) return null;
  return (
    <div className="meta-row">
      <span className="meta-label">{icon} {label}</span>
      <span className="meta-value">
        {Array.isArray(value) ? value.join(", ") : value}
      </span>
    </div>
  );
}

function ArgumentList({ title, icon, items }) {
  if (!items || items.length === 0) return null;
  return (
    <div className="args-section">
      <h4 className="args-title">{icon} {title}</h4>
      <ul className="args-list">
        {items.map((arg, i) => (
          <li key={i}>{arg}</li>
        ))}
      </ul>
    </div>
  );
}

export default function InsightsPanel({ data, onClose }) {
  if (!data) return null;

  const { sections, precedents, outcomes, similar_cases, case_meta } = data;

  const hasSections = sections && sections.length > 0;
  const hasPrecedents = precedents && precedents.length > 0;
  const hasOutcomes = outcomes && outcomes.length > 0;
  const hasSimilar = similar_cases && similar_cases.length > 0;
  const meta = case_meta || {};

  const verdictClass =
    meta.verdict === "Convicted" || meta.verdict === "Dismissed"
      ? "verdict-negative"
      : meta.verdict === "Acquitted" || meta.verdict === "Allowed"
      ? "verdict-positive"
      : "verdict-neutral";

  return (
    <div className="insights-panel">
      <div className="insights-header">
        <h2><Scale size={20} /> Case Analysis & Insights</h2>
        <button className="insights-close" onClick={onClose}>
          <X size={20} />
        </button>
      </div>

      {/* ===== Case Summary Card (full width) ===== */}
      <div className="case-summary-card">
        <div className="summary-top">
          <div className="summary-title-row">
            <h3 className="case-title">
              <Gavel size={18} />
              {meta.case_title || "Case Details"}
            </h3>
            {meta.verdict && (
              <span className={`verdict-badge ${verdictClass}`}>
                {meta.verdict}
              </span>
            )}
          </div>
          {meta.summary && (
            <p className="case-summary-text">{meta.summary}</p>
          )}
        </div>

        <div className="meta-grid">
          <MetaRow icon={<Building2 size={14} />} label="Court" value={meta.court} />
          <MetaRow icon={<Calendar size={14} />} label="Year" value={meta.year} />
          <MetaRow icon={<Hash size={14} />} label="Case No." value={meta.case_number} />
          <MetaRow icon={<User size={14} />} label="Petitioner" value={meta.petitioner} />
          <MetaRow icon={<User size={14} />} label="Respondent" value={meta.respondent} />
          <MetaRow icon={<CheckCircle2 size={14} />} label="Verdict" value={meta.verdict} />
          <MetaRow icon={<BookOpen size={14} />} label="Total Citations" value={meta.total_citations?.toString()} />
          <MetaRow icon={<Gavel size={14} />} label="Sections Cited" value={meta.sections_cited} />
        </div>

        {meta.issues && meta.issues.length > 0 && (
          <div className="issues-section">
            <h4 className="issues-title"><AlertTriangle size={14} /> Key Issues</h4>
            <ul className="issues-list">
              {meta.issues.map((issue, i) => (
                <li key={i}>{issue}</li>
              ))}
            </ul>
          </div>
        )}

        <div className="arguments-grid">
          <ArgumentList
            title="Petitioner Arguments"
            icon={<MessageCircle size={14} />}
            items={meta.petitioner_arguments}
          />
          <ArgumentList
            title="Respondent Arguments"
            icon={<MessageCircle size={14} />}
            items={meta.respondent_arguments}
          />
        </div>
      </div>

      {/* ===== 4 Charts in 2x2 Grid ===== */}
      <div className="charts-grid">
        {/* 1. IPC Sections Bar Chart */}
        <ChartCard title="Law Sections Distribution" icon={<Gavel size={16} />}>
          {hasSections ? (
            <div className="chart-container">
              <ResponsiveContainer width="100%" height={260}>
                <BarChart data={sections} margin={{ top: 10, right: 20, left: 0, bottom: 40 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#2d3144" />
                  <XAxis dataKey="section" tick={{ fill: "#8b8fa3", fontSize: 11 }} angle={-35} textAnchor="end" />
                  <YAxis tick={{ fill: "#8b8fa3", fontSize: 12 }} allowDecimals={false} />
                  <Tooltip contentStyle={TOOLTIP_STYLE} />
                  <Bar dataKey="count" fill="#6c63ff" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <p className="no-chart-data">No section data found</p>
          )}
        </ChartCard>

        {/* 2. Outcome Patterns Pie Chart */}
        <ChartCard title="Outcome Patterns" icon={<Scale size={16} />}>
          {hasOutcomes ? (
            <div className="chart-container">
              <ResponsiveContainer width="100%" height={260}>
                <PieChart>
                  <Pie
                    data={outcomes}
                    cx="50%"
                    cy="50%"
                    innerRadius={55}
                    outerRadius={90}
                    paddingAngle={3}
                    dataKey="value"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    labelLine={{ stroke: "#8b8fa3" }}
                  >
                    {outcomes.map((_, i) => (
                      <Cell key={i} fill={COLORS[i % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={TOOLTIP_STYLE} />
                  <Legend wrapperStyle={{ fontSize: 12, color: "#8b8fa3" }} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <p className="no-chart-data">No outcome data found</p>
          )}
        </ChartCard>

        {/* 3. Precedent Citations Bar Chart */}
        <ChartCard title="Precedent Citation Frequency" icon={<BookOpen size={16} />}>
          {hasPrecedents ? (
            <div className="chart-container">
              <ResponsiveContainer width="100%" height={260}>
                <BarChart data={precedents} layout="vertical" margin={{ top: 10, right: 20, left: 10, bottom: 10 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#2d3144" />
                  <XAxis type="number" tick={{ fill: "#8b8fa3", fontSize: 12 }} allowDecimals={false} />
                  <YAxis dataKey="name" type="category" width={150} tick={{ fill: "#8b8fa3", fontSize: 11 }} />
                  <Tooltip contentStyle={TOOLTIP_STYLE} />
                  <Bar dataKey="count" fill="#34d399" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <p className="no-chart-data">No citation data found</p>
          )}
        </ChartCard>

        {/* 4. Similar Cases Table */}
        <ChartCard title="Similar Cases Comparison" icon={<FileText size={16} />}>
          {hasSimilar ? (
            <div className="similar-table-wrap">
              <table className="similar-table">
                <thead>
                  <tr>
                    <th>Case</th>
                    <th>Similarity</th>
                    <th>Snippet</th>
                  </tr>
                </thead>
                <tbody>
                  {similar_cases.map((c, i) => (
                    <tr key={i}>
                      <td className="case-name-cell">{c.case_name}</td>
                      <td>
                        <div className="similarity-bar-wrap">
                          <div className="similarity-bar" style={{ width: `${c.similarity}%` }} />
                          <span className="similarity-label">{c.similarity}%</span>
                        </div>
                      </td>
                      <td className="snippet-cell">{c.snippet}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="no-chart-data">No similar cases found</p>
          )}
        </ChartCard>
      </div>
    </div>
  );
}
