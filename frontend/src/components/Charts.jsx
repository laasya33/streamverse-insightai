import React, { useEffect, useState } from "react";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend, RadarChart, Radar, PolarGrid,
  PolarAngleAxis
} from "recharts";

const API = process.env.REACT_APP_API_URL || "http://localhost:8000";
const COLORS = ["#3b82f6","#8b5cf6","#10b981","#f59e0b","#ef4444","#06b6d4","#ec4899","#84cc16"];

function Card({ title, children }) {
  return (
    <div style={{ background:"#1e293b", border:"1px solid #334155", borderRadius:12, padding:16, marginBottom:16 }}>
      <div style={{ fontSize:12, fontWeight:700, color:"#64748b", marginBottom:12, textTransform:"uppercase", letterSpacing:1 }}>{title}</div>
      {children}
    </div>
  );
}

export default function Charts() {
  const [genres, setGenres]       = useState([]);
  const [cities, setCities]       = useState([]);
  const [titles, setTitles]       = useState([]);
  const [platforms, setPlatforms] = useState([]);
  const [tab, setTab]             = useState("genres");

  useEffect(() => {
    fetch(`${API}/api/analytics/genre-performance`).then(r=>r.json()).then(d=>setGenres(d.rows||[]));
    fetch(`${API}/api/analytics/city-engagement`).then(r=>r.json()).then(d=>setCities(d.rows||[]));
    fetch(`${API}/api/analytics/top-titles`).then(r=>r.json()).then(d=>setTitles(d.rows||[]));
    fetch(`${API}/api/analytics/platform-stats`).then(r=>r.json()).then(d=>setPlatforms(d.rows||[]));
  }, []);

  const tabs = ["genres","cities","titles","platforms"];

  return (
    <div style={{ height:"100%", overflowY:"auto", padding:"0 4px" }}>
      <div style={{ display:"flex", gap:6, marginBottom:14, flexWrap:"wrap" }}>
        {tabs.map(t => (
          <button key={t} onClick={()=>setTab(t)} style={{
            padding:"5px 12px", borderRadius:8, fontSize:11, fontWeight:600, cursor:"pointer",
            background: tab===t ? "#3b82f6" : "#0f172a",
            color: tab===t ? "white" : "#64748b",
            border: `1px solid ${tab===t ? "#3b82f6" : "#334155"}`,
            textTransform:"capitalize"
          }}>{t}</button>
        ))}
      </div>

      {tab === "genres" && (
        <>
          <Card title="Revenue by Genre (USD)">
            <ResponsiveContainer width="100%" height={180}>
              <BarChart data={genres}>
                <XAxis dataKey="genre" tick={{fontSize:10,fill:"#94a3b8"}} />
                <YAxis tick={{fontSize:9,fill:"#94a3b8"}} tickFormatter={v=>`$${(v/1e6).toFixed(0)}M`} />
                <Tooltip formatter={v=>`$${(v/1e6).toFixed(1)}M`} contentStyle={{background:"#0f172a",border:"1px solid #334155",borderRadius:8}} />
                <Bar dataKey="total_revenue" radius={[4,4,0,0]}>
                  {genres.map((_,i)=><Cell key={i} fill={COLORS[i%COLORS.length]}/>)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </Card>
          <Card title="Avg Completion % by Genre">
            <ResponsiveContainer width="100%" height={180}>
              <RadarChart data={genres}>
                <PolarGrid stroke="#334155" />
                <PolarAngleAxis dataKey="genre" tick={{fontSize:9,fill:"#94a3b8"}} />
                <Radar dataKey="avg_completion" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.3} />
              </RadarChart>
            </ResponsiveContainer>
          </Card>
        </>
      )}

      {tab === "cities" && (
        <Card title="Top Cities by Total Views">
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={cities.slice(0,8)} layout="vertical">
              <XAxis type="number" tick={{fontSize:9,fill:"#94a3b8"}} tickFormatter={v=>`${(v/1000).toFixed(0)}K`} />
              <YAxis type="category" dataKey="city" tick={{fontSize:10,fill:"#94a3b8"}} width={70} />
              <Tooltip contentStyle={{background:"#0f172a",border:"1px solid #334155",borderRadius:8}} />
              <Bar dataKey="total_views" radius={[0,4,4,0]}>
                {cities.slice(0,8).map((_,i)=><Cell key={i} fill={COLORS[i%COLORS.length]}/>)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </Card>
      )}

      {tab === "titles" && (
        <Card title="Top Titles by Views">
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={titles.slice(0,8)} layout="vertical">
              <XAxis type="number" tick={{fontSize:9,fill:"#94a3b8"}} />
              <YAxis type="category" dataKey="title" tick={{fontSize:9,fill:"#94a3b8"}} width={90} />
              <Tooltip contentStyle={{background:"#0f172a",border:"1px solid #334155",borderRadius:8}} />
              <Bar dataKey="total_views" fill="#8b5cf6" radius={[0,4,4,0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      )}

      {tab === "platforms" && (
        <Card title="Sessions by Platform">
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie data={platforms} dataKey="sessions" nameKey="platform" cx="50%" cy="50%" outerRadius={80} label={({platform,percent})=>`${platform} ${(percent*100).toFixed(0)}%`} labelLine={false}>
                {platforms.map((_,i)=><Cell key={i} fill={COLORS[i%COLORS.length]}/>)}
              </Pie>
              <Tooltip contentStyle={{background:"#0f172a",border:"1px solid #334155",borderRadius:8}} />
            </PieChart>
          </ResponsiveContainer>
        </Card>
      )}
    </div>
  );
}
