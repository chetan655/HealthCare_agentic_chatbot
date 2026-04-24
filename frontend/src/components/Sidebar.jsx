import {
  Plus,
  HeartPulse,
  Brain,
  MapPin,
  ScanLine,
  Activity,
  MessageSquareText,
} from 'lucide-react';

export default function Sidebar({ onNewChat, messageCount }) {
  return (
    <aside className="hidden lg:flex flex-col w-72 h-full bg-white border-r border-border">
      <div className="p-6 border-b border-border">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-brand to-brand-dark flex items-center justify-center shadow-lg shadow-brand/20">
            <HeartPulse size={22} className="text-white" />
          </div>
          <div>
            <h1 className="text-base font-bold text-text-primary tracking-tight">
              Acharya
            </h1>
            <p className="text-[11px] text-text-muted font-medium">
              Medical AI Assistant
            </p>
          </div>
        </div>
      </div>

      <div className="p-4">
        <button
          onClick={onNewChat}
          className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-brand text-white text-sm font-semibold hover:bg-brand-dark transition-all duration-200 shadow-md shadow-brand/20 hover:shadow-lg hover:shadow-brand/30 active:scale-[0.97] cursor-pointer"
        >
          <Plus size={16} strokeWidth={2.5} />
          New Conversation
        </button>
      </div>

      <div className="flex-1 px-4 py-2">
        <p className="text-[11px] font-semibold text-text-muted uppercase tracking-wider mb-3 px-2">
          Agent Network
        </p>
        <div className="space-y-1">
          <AgentItem
            icon={Brain}
            label="Query Classifier"
            desc="Routes your questions"
            color="text-brand"
            bg="bg-brand-50"
          />
          <AgentItem
            icon={Activity}
            label="Medical Agent"
            desc="Health & wellness Q&A"
            color="text-emerald-600"
            bg="bg-emerald-50"
          />
          <AgentItem
            icon={MapPin}
            label="Hospital Finder"
            desc="Nearby medical facilities"
            color="text-amber-600"
            bg="bg-amber-50"
          />
          <AgentItem
            icon={ScanLine}
            label="OCR Agent"
            desc="Medicine image analysis"
            color="text-violet-600"
            bg="bg-violet-50"
          />
        </div>
      </div>

      <div className="p-4 border-t border-border">
        <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-surface-alt">
          <MessageSquareText size={14} className="text-text-muted" />
          <span className="text-xs text-text-secondary">
            {messageCount > 0
              ? `${messageCount} message${messageCount !== 1 ? 's' : ''} in session`
              : 'Start a new conversation'}
          </span>
        </div>
      </div>
    </aside>
  );
}

function AgentItem({ icon: Icon, label, desc, color, bg }) {
  return (
    <div className="flex items-center gap-3 px-3 py-2.5 rounded-xl hover:bg-surface-alt transition-colors duration-150 group">
      <div
        className={`w-8 h-8 rounded-lg ${bg} flex items-center justify-center transition-transform duration-200 group-hover:scale-105`}
      >
        <Icon size={16} className={color} />
      </div>
      <div className="min-w-0">
        <p className="text-sm font-medium text-text-primary truncate">
          {label}
        </p>
        <p className="text-[11px] text-text-muted truncate">{desc}</p>
      </div>
    </div>
  );
}
