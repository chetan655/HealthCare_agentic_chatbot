import { Activity, MapPin, ScanLine, Brain } from 'lucide-react';

const AGENTS = {
  general: {
    label: 'Medical Assistant',
    icon: Brain,
    bg: 'bg-brand-50',
    text: 'text-brand',
    ring: 'ring-brand/20',
    dot: 'bg-brand',
  },
  hospital: {
    label: 'Hospital Finder',
    icon: MapPin,
    bg: 'bg-emerald-50',
    text: 'text-emerald-600',
    ring: 'ring-emerald-500/20',
    dot: 'bg-emerald-500',
  },
  ocr: {
    label: 'Medicine Scanner',
    icon: ScanLine,
    bg: 'bg-violet-50',
    text: 'text-violet-600',
    ring: 'ring-violet-500/20',
    dot: 'bg-violet-500',
  },
};

export default function AgentBadge({ agent }) {
  const config = AGENTS[agent] || AGENTS.general;
  const Icon = config.icon;

  return (
    <div
      className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold ${config.bg} ${config.text} ring-1 ${config.ring} animate-fade-in`}
    >
      <span className="relative flex h-2 w-2">
        <span
          className={`absolute inline-flex h-full w-full rounded-full ${config.dot} opacity-40 animate-ping`}
        />
        <span
          className={`relative inline-flex h-2 w-2 rounded-full ${config.dot}`}
        />
      </span>
      <Icon size={13} strokeWidth={2.2} />
      <span>{config.label}</span>
    </div>
  );
}
