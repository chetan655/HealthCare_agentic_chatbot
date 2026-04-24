import {
  Stethoscope,
  MapPin,
  ScanLine,
  ArrowRight,
  Sparkles,
} from 'lucide-react';

const SUGGESTIONS = [
  {
    icon: Stethoscope,
    title: 'Ask about symptoms',
    desc: 'Get general health insights',
    prompt: 'I have been experiencing headaches and fatigue lately. What could be the cause?',
    gradient: 'from-blue-500 to-cyan-400',
  },
  {
    icon: MapPin,
    title: 'Find nearby hospitals',
    desc: 'Locate medical facilities',
    prompt: 'Find hospitals near me',
    gradient: 'from-emerald-500 to-teal-400',
  },
  {
    icon: ScanLine,
    title: 'Scan a medicine',
    desc: 'Upload a medicine image',
    prompt: null,
    gradient: 'from-violet-500 to-purple-400',
  },
];

export default function WelcomeScreen({ onSuggestionClick, onImageTrigger }) {
  return (
    <div className="flex-1 flex flex-col items-center justify-center px-6 animate-fade-in">
      <div className="relative mb-8">
        <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-brand to-brand-dark flex items-center justify-center shadow-xl shadow-brand/25">
          <Sparkles size={36} className="text-white" />
        </div>
        <div className="absolute -top-1 -right-1 w-6 h-6 rounded-full bg-emerald-400 border-[3px] border-white flex items-center justify-center">
          <span className="block w-2 h-2 rounded-full bg-white" />
        </div>
      </div>

      <h2 className="text-2xl sm:text-3xl font-bold text-text-primary mb-2 tracking-tight text-center">
        Hello, I'm Acharya
      </h2>
      <p className="text-text-secondary text-center max-w-md mb-10 text-sm sm:text-base leading-relaxed">
        Your intelligent medical assistant. Ask me about symptoms, find nearby
        hospitals, or scan medicine labels for instant insights.
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 w-full max-w-2xl">
        {SUGGESTIONS.map((item, i) => {
          const Icon = item.icon;
          return (
            <button
              key={i}
              onClick={() => {
                if (item.prompt === null) {
                  onImageTrigger?.();
                } else {
                  onSuggestionClick?.(item.prompt);
                }
              }}
              className="group relative flex flex-col items-start p-5 rounded-2xl bg-white border border-border hover:border-brand/30 hover:shadow-lg hover:shadow-brand/5 transition-all duration-300 text-left cursor-pointer active:scale-[0.97]"
            >
              <div
                className={`w-10 h-10 rounded-xl bg-gradient-to-br ${item.gradient} flex items-center justify-center mb-4 shadow-md transition-transform duration-300 group-hover:scale-110`}
              >
                <Icon size={20} className="text-white" />
              </div>
              <p className="text-sm font-semibold text-text-primary mb-1">
                {item.title}
              </p>
              <p className="text-xs text-text-muted mb-3">{item.desc}</p>
              <div className="flex items-center gap-1 text-brand text-xs font-medium opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                <span>Try it</span>
                <ArrowRight size={12} />
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
