import { useState, useRef } from 'react';
import { SendHorizonal, Paperclip, X, Image as ImageIcon } from 'lucide-react';

export default function ChatInput({ onSend, disabled }) {
  const [text, setText] = useState('');
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const fileRef = useRef(null);
  const inputRef = useRef(null);

  const handleImageChange = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setImageFile(file);
    const reader = new FileReader();
    reader.onload = (ev) => setImagePreview(ev.target.result);
    reader.readAsDataURL(file);
  };

  const removeImage = () => {
    setImageFile(null);
    setImagePreview(null);
    if (fileRef.current) fileRef.current.value = '';
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const trimmed = text.trim();
    if (!trimmed && !imageFile) return;
    onSend(trimmed || (imageFile ? 'Analyze this medicine image' : ''), imageFile);
    setText('');
    removeImage();
    inputRef.current?.focus();
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const canSend = (text.trim().length > 0 || imageFile) && !disabled;

  return (
    <div className="border-t border-border bg-white/80 backdrop-blur-lg px-4 py-3 sm:px-6">
      {imagePreview && (
        <div className="mb-3 animate-fade-in-up">
          <div className="inline-flex items-center gap-3 p-2 pr-3 rounded-xl bg-surface-alt border border-border">
            <div className="relative">
              <img
                src={imagePreview}
                alt="Upload preview"
                className="w-14 h-14 rounded-lg object-cover"
              />
              <div className="absolute inset-0 rounded-lg bg-black/5" />
            </div>
            <div className="min-w-0">
              <p className="text-xs font-semibold text-text-primary truncate max-w-[160px]">
                {imageFile?.name}
              </p>
              <p className="text-[11px] text-text-muted">
                {(imageFile?.size / 1024).toFixed(0)} KB
              </p>
            </div>
            <button
              onClick={removeImage}
              className="w-6 h-6 rounded-full bg-red-50 hover:bg-red-100 flex items-center justify-center transition-colors cursor-pointer"
            >
              <X size={12} className="text-red-500" />
            </button>
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="flex items-end gap-2">
        <input
          ref={fileRef}
          type="file"
          accept="image/*"
          onChange={handleImageChange}
          className="hidden"
          id="image-upload"
        />

        <button
          type="button"
          onClick={() => fileRef.current?.click()}
          disabled={disabled}
          className="flex-shrink-0 w-10 h-10 rounded-xl bg-surface-alt hover:bg-brand-50 border border-border hover:border-brand/30 flex items-center justify-center transition-all duration-200 disabled:opacity-40 cursor-pointer"
          title="Upload medicine image"
        >
          {imageFile ? (
            <ImageIcon size={18} className="text-brand" />
          ) : (
            <Paperclip size={18} className="text-text-muted" />
          )}
        </button>

        <div className="flex-1 relative">
          <textarea
            ref={inputRef}
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about symptoms, medicines, or find hospitals..."
            disabled={disabled}
            rows={1}
            className="w-full resize-none rounded-xl border border-border bg-surface-alt px-4 py-2.5 text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-brand/20 focus:border-brand/40 disabled:opacity-50 transition-all duration-200"
            style={{ minHeight: '42px', maxHeight: '120px' }}
            onInput={(e) => {
              e.target.style.height = 'auto';
              e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px';
            }}
          />
        </div>

        <button
          type="submit"
          disabled={!canSend}
          className="flex-shrink-0 w-10 h-10 rounded-xl bg-brand hover:bg-brand-dark text-white flex items-center justify-center transition-all duration-200 shadow-md shadow-brand/20 disabled:opacity-40 disabled:shadow-none active:scale-95 cursor-pointer"
        >
          <SendHorizonal size={18} />
        </button>
      </form>
    </div>
  );
}
