import ReactMarkdown from 'react-markdown';
import { User, Sparkles } from 'lucide-react';
import HospitalGrid, { parseHospitals } from './HospitalGrid';

export default function MessageBubble({ message }) {
  const isUser = message.role === 'user';

  if (isUser) {
    return (
      <div className="flex justify-end gap-3 animate-fade-in-up">
        <div className="max-w-[75%]">
          <div className="px-4 py-3 rounded-2xl rounded-br-md bg-brand text-white text-sm leading-relaxed shadow-md shadow-brand/15">
            {message.content}
          </div>
          {message.imageName && (
            <div className="mt-2 flex justify-end">
              <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-brand-50 text-brand text-xs font-medium">
                📎 {message.imageName}
              </span>
            </div>
          )}
        </div>
        <div className="w-8 h-8 rounded-full bg-brand-100 flex items-center justify-center flex-shrink-0">
          <User size={15} className="text-brand" />
        </div>
      </div>
    );
  }

  const hasHospitals = parseHospitals(message.content).length > 0;

  return (
    <div className="flex gap-3 animate-slide-in-left">
      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-brand to-brand-dark flex items-center justify-center flex-shrink-0 shadow-md shadow-brand/15">
        <Sparkles size={14} className="text-white" />
      </div>
      <div className="max-w-[80%] min-w-0">
        <div className="px-4 py-3 rounded-2xl rounded-bl-md bg-white border border-border text-sm text-text-primary shadow-sm">
          <div className="prose-medical">
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>
          {hasHospitals && <HospitalGrid text={message.content} />}
        </div>
      </div>
    </div>
  );
}
