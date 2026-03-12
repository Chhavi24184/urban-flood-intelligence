import { useState, useEffect, useRef, useMemo } from "react";

// Note: Using global L and lucide from index.html CDNs
const API_BASE = "http://127.0.0.1:8000";

// --- Components ---

const Icon = ({ name, className = "w-5 h-5", size = 20 }) => {
  useEffect(() => {
    if (window.lucide) {
      window.lucide.createIcons();
    }
  }, [name]);
  return <i data-lucide={name} className={className} style={{ width: size, height: size }}></i>;
};

const StatBlock = ({ label, value, icon, color }) => (
  <div className="glass neo-card rounded-2xl p-4 flex flex-col gap-1 border border-white/5">
    <div className="flex justify-between items-start">
      <span className="text-[10px] font-black uppercase tracking-widest text-slate-500">{label}</span>
      <div className={`p-1.5 rounded-lg bg-${color}-500/10 text-${color}-400`}>
        <Icon name={icon} size={14} />
      </div>
    </div>
    <div className="text-2xl font-black text-white">{value}</div>
  </div>
);

export default function App() {
  const mapRef = useRef(null);
  const layersRef = useRef([]);
  const [wards, setWards] = useState([]);
  const [metadata, setMetadata] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [simulationRain, setSimulationRain] = useState(0);
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState("checking");
  const [selectedWard, setSelectedWard] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [riskRes, metaRes, recRes] = await Promise.all([
        fetch(`${API_BASE}/flood-risk?level=ward`),
        fetch(`${API_BASE}/wards-metadata`),
        fetch(`${API_BASE}/recommendations`)
      ]);
      const [riskData, metaData, recData] = await Promise.all([
        riskRes.json(), metaRes.json(), recRes.json()
      ]);
      setWards(riskData.wards);
      setMetadata(metaData.wards);
      setRecommendations(recData.recommendations);
      setStatus("connected");
    } catch (err) {
      setStatus("disconnected");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  useEffect(() => {
    if (!mapRef.current && window.L) {
      mapRef.current = window.L.map('map', { zoomControl: false, attributionControl: false }).setView([12.96, 77.60], 13);
      window.L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png').addTo(mapRef.current);
      window.L.control.zoom({ position: 'bottomright' }).addTo(mapRef.current);
    }
  }, []);

  useEffect(() => {
    if (!mapRef.current || !wards.length || !metadata.length || !window.L) return;
    layersRef.current.forEach(layer => mapRef.current.removeLayer(layer));
    layersRef.current = [];

    wards.forEach(ward => {
      const meta = metadata.find(m => m.id === ward.ward_id);
      if (!meta) return;

      const color = ward.category === "high" ? "#ef4444" : ward.category === "medium" ? "#f59e0b" : "#10b981";
      const rect = window.L.rectangle(
        [[meta.min_lat, meta.min_lon], [meta.max_lat, meta.max_lon]],
        { color, weight: 1.5, fillOpacity: 0.35, className: 'ward-polygon' }
      ).addTo(mapRef.current);

      rect.on('click', () => setSelectedWard(ward));
      layersRef.current.push(rect);
    });
  }, [wards, metadata]);

  const handleSimulate = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/simulate-rainfall`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ percent_increase: parseFloat(simulationRain) })
      });
      const data = await res.json();
      setWards(data.wards);
      if (selectedWard) {
        const updated = data.wards.find(w => w.ward_id === selectedWard.ward_id);
        if (updated) setSelectedWard(updated);
      }
    } catch (err) {
      alert("Simulation failed.");
    } finally {
      setLoading(false);
    }
  };

  const selectedWardDetails = useMemo(() => {
    if (!selectedWard) return null;
    const rec = recommendations.find(r => r.ward_id === selectedWard.ward_id);
    return { ...selectedWard, ...rec };
  }, [selectedWard, recommendations]);

  const avgRisk = wards.length ? (wards.reduce((acc, w) => acc + w.score, 0) / wards.length).toFixed(2) : 0;
  const highRiskCount = wards.filter(w => w.category === "high").length;

  return (
    <div className="flex flex-col h-screen w-full bg-[#020617] text-slate-200 overflow-hidden font-sans">
      {/* Navbar */}
      <nav className="glass px-6 py-3 flex justify-between items-center z-[1001] border-b border-white/5">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-brand-600 rounded-xl shadow-lg shadow-brand-600/30">
            <Icon name="shield-check" className="text-white" />
          </div>
          <div>
            <h1 className="text-xl font-black tracking-tight text-white flex items-center gap-2">
              FloodSense <span className="bg-brand-500/20 text-brand-400 text-[10px] px-2 py-0.5 rounded uppercase tracking-widest border border-brand-500/30">v2.0 AI</span>
            </h1>
          </div>
        </div>
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900/50 border border-white/5">
            <div className={`w-2 h-2 rounded-full ${status === 'connected' ? 'bg-emerald-500 shadow-[0_0_8px_#10b981]' : 'bg-red-500 shadow-[0_0_8px_#ef4444]'}`}></div>
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">{status === 'connected' ? 'Live System' : 'System Offline'}</span>
          </div>
        </div>
      </nav>

      <div className="flex flex-1 overflow-hidden p-6 gap-6">
        {/* Sidebar */}
        <aside className="w-80 flex flex-col gap-6 overflow-y-auto pr-2">
          <div className="grid grid-cols-2 gap-4">
            <StatBlock label="Global Risk" value={`${(avgRisk * 100).toFixed(0)}%`} icon="activity" color="brand" />
            <StatBlock label="Alert Zones" value={highRiskCount} icon="alert-triangle" color="red" />
          </div>

          <div className="glass rounded-3xl p-5 space-y-5 border-white/5 shadow-2xl">
            <h3 className="text-xs font-black uppercase tracking-widest text-brand-400 flex items-center gap-2">
              <Icon name="zap" size={14} /> Simulation Engine
            </h3>
            <div className="space-y-4">
              <div className="space-y-3">
                <div className="flex justify-between text-[10px] font-bold uppercase text-slate-500">
                  <span>Rainfall Intensity</span>
                  <span className="text-brand-400">+{simulationRain}%</span>
                </div>
                <input 
                  type="range" min="0" max="100" step="1"
                  value={simulationRain}
                  onChange={(e) => setSimulationRain(e.target.value)}
                  className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-brand-500"
                />
              </div>
              <button 
                onClick={handleSimulate}
                disabled={loading}
                className="w-full py-3 bg-brand-600 hover:bg-brand-500 disabled:bg-slate-800 text-white rounded-xl font-black text-[11px] uppercase tracking-widest transition-all flex items-center justify-center gap-2"
              >
                {loading ? "Loading..." : "Execute Simulation"}
              </button>
            </div>
          </div>

          <div className="glass rounded-3xl p-5 flex-1 overflow-hidden flex flex-col gap-4 border border-white/5">
            <h3 className="text-xs font-black uppercase tracking-widest text-slate-500 flex items-center gap-2">
              <Icon name="navigation" size={14} /> Ward Status
            </h3>
            <div className="flex-1 overflow-y-auto space-y-3 pr-1">
              {wards.sort((a,b) => b.score - a.score).map(w => (
                <div 
                  key={w.ward_id}
                  onClick={() => setSelectedWard(w)}
                  className={`p-3 rounded-2xl cursor-pointer transition-all border border-white/5 flex items-center justify-between ${selectedWard?.ward_id === w.ward_id ? 'bg-brand-500/10 border-brand-500/40 shadow-lg shadow-brand-500/10' : 'hover:bg-white/5'}`}
                >
                  <div className="text-[11px] font-black text-white">{w.ward_name}</div>
                  <div className={`text-[10px] font-black uppercase px-2 py-0.5 rounded ${w.category === 'high' ? 'text-red-400 bg-red-400/10' : w.category === 'medium' ? 'text-amber-400 bg-amber-400/10' : 'text-emerald-400 bg-emerald-400/10'}`}>
                    {(w.score * 100).toFixed(0)}%
                  </div>
                </div>
              ))}
            </div>
          </div>
        </aside>

        {/* Map View */}
        <main className="flex-1 relative">
          <div id="map" className="shadow-[0_20px_50px_rgba(0,0,0,0.5)] border border-white/5 rounded-3xl" />
          
          {selectedWardDetails && (
            <div className="absolute top-6 right-6 w-96 z-[1000] animate-in slide-in-from-right duration-500">
              <div className="glass rounded-[2rem] p-6 shadow-2xl border-brand-500/30 border-2 overflow-hidden">
                <div className="flex justify-between items-start mb-6">
                  <div>
                    <div className="text-[10px] font-black uppercase tracking-[0.2em] text-brand-400 mb-1">Ward Analysis</div>
                    <h2 className="text-3xl font-black text-white tracking-tight">{selectedWardDetails.ward_name}</h2>
                  </div>
                  <button onClick={() => setSelectedWard(null)} className="p-2 hover:bg-white/10 rounded-full transition-colors">
                    <Icon name="x" size={20} className="text-slate-400" />
                  </button>
                </div>

                <div className="grid grid-cols-2 gap-4 mb-8">
                  <div className="bg-white/5 rounded-2xl p-4 border border-white/5">
                    <div className="text-[10px] font-black uppercase tracking-widest text-slate-500 mb-2">Hazard Level</div>
                    <div className={`text-2xl font-black ${selectedWardDetails.category === 'high' ? 'text-red-400' : 'text-emerald-400'}`}>
                      {(selectedWardDetails.score * 100).toFixed(0)}%
                    </div>
                  </div>
                  <div className="bg-white/5 rounded-2xl p-4 border border-white/5">
                    <div className="text-[10px] font-black uppercase tracking-widest text-slate-500 mb-2">Readiness</div>
                    <div className="text-2xl font-black text-brand-400">{selectedWardDetails.readiness_score}%</div>
                  </div>
                </div>

                <div className="space-y-4">
                  <h4 className="text-[10px] font-black uppercase tracking-widest text-slate-400 flex items-center gap-2">
                    <Icon name="alert-circle" size={14} className="text-brand-400" /> AI Recommendations
                  </h4>
                  <div className="space-y-2.5">
                    {selectedWardDetails.actions?.map((action, i) => (
                      <div key={i} className="p-3 rounded-xl flex gap-3 items-center text-[11px] font-bold bg-white/5 hazard-high border-white/5">
                        <Icon name="check-circle" size={12} className="text-brand-400 shrink-0" />
                        <span className="text-slate-200">{action}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
