import { MapPin, Navigation, Building2 } from 'lucide-react';

export function parseHospitals(text) {
  const lines = text.split('\n');
  const hospitals = [];
  let current = null;

  for (const line of lines) {
    const numberedMatch = line.match(
      /^\s*\*?\*?\d+[\.\)]\s*\*?\*?\s*(.+?)(?:\*\*)?$/
    );
    const boldMatch = line.match(/^\s*\*\*(.+?)\*\*/);
    const distMatch = line.match(
      /(?:distance|approximately|about|around|~)?\s*[:\-–]?\s*(\d+(?:\.\d+)?)\s*(?:km|kilometer)/i
    );
    const distMatch2 = line.match(/(\d+(?:\.\d+)?)\s*km/i);

    if (numberedMatch || boldMatch) {
      if (current) hospitals.push(current);
      const rawName = (numberedMatch?.[1] || boldMatch?.[1] || '')
        .replace(/\*+/g, '')
        .replace(/[-–:].*/g, '')
        .trim();
      current = { name: rawName, distance: null };
    }

    if (current && (distMatch || distMatch2)) {
      const d = distMatch ? distMatch[1] : distMatch2[1];
      current.distance = parseFloat(d);
    }
  }

  if (current) hospitals.push(current);

  return hospitals.filter((h) => h.name && h.name.length > 2);
}

export default function HospitalGrid({ text }) {
  const hospitals = parseHospitals(text);

  if (hospitals.length === 0) return null;

  return (
    <div className="mt-3 animate-fade-in-up">
      <div className="flex items-center gap-2 mb-3">
        <Building2 size={15} className="text-emerald-600" />
        <span className="text-xs font-semibold text-text-secondary uppercase tracking-wider">
          Nearby Hospitals ({hospitals.length})
        </span>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {hospitals.map((h, i) => (
          <div
            key={i}
            className="group flex items-start gap-3 p-4 rounded-xl bg-white border border-border hover:border-emerald-200 hover:shadow-md hover:shadow-emerald-500/5 transition-all duration-200"
            style={{ animationDelay: `${i * 80}ms` }}
          >
            <div className="w-9 h-9 rounded-lg bg-emerald-50 flex items-center justify-center flex-shrink-0 group-hover:bg-emerald-100 transition-colors">
              <MapPin size={16} className="text-emerald-600" />
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-sm font-semibold text-text-primary truncate">
                {h.name}
              </p>
              {h.distance !== null && (
                <div className="flex items-center gap-1.5 mt-1.5">
                  <Navigation size={11} className="text-text-muted" />
                  <span className="text-xs text-text-muted">
                    {h.distance} km away
                  </span>
                </div>
              )}
            </div>
            {h.distance !== null && (
              <span
                className={`inline-flex items-center px-2 py-0.5 rounded-md text-[11px] font-bold flex-shrink-0 ${
                  h.distance <= 2
                    ? 'bg-emerald-50 text-emerald-700'
                    : h.distance <= 5
                    ? 'bg-amber-50 text-amber-700'
                    : 'bg-slate-100 text-slate-600'
                }`}
              >
                {h.distance} km
              </span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
