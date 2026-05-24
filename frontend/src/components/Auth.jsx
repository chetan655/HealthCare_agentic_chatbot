import { useState } from 'react';
import { loginUser, signupUser } from '../api/api';
import { HeartPulse, Loader2 } from 'lucide-react';

export default function Auth({ onLogin }) {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isLogin) {
        const data = await loginUser(email, password);
        onLogin(data);
      } else {
        await signupUser(email, fullName, password);
        // After successful signup, automatically log the user in
        const data = await loginUser(email, password);
        onLogin(data);
      }
    } catch (err) {
      setError(err.message || 'An error occurred during authentication.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-surface px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8 bg-white p-8 rounded-2xl shadow-xl border border-border animate-fade-in-up">
        <div className="text-center">
          <div className="mx-auto w-12 h-12 rounded-xl bg-gradient-to-br from-brand to-brand-dark flex items-center justify-center">
            <HeartPulse size={24} className="text-white" />
          </div>
          <h2 className="mt-6 text-3xl font-extrabold text-text-primary">
            {isLogin ? 'Welcome Back' : 'Create Account'}
          </h2>
          <p className="mt-2 text-sm text-text-secondary">
            {isLogin ? 'Sign in to continue to Acharya' : 'Join Acharya for intelligent medical assistance'}
          </p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="bg-red-50 text-red-500 p-3 rounded-lg text-sm text-center border border-red-100 animate-fade-in">
              {error}
            </div>
          )}
          
          <div className="rounded-md shadow-sm space-y-4">
            {!isLogin && (
              <div className="animate-fade-in">
                <label className="block text-sm font-medium text-text-secondary mb-1">Full Name</label>
                <input
                  type="text"
                  required
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="appearance-none rounded-lg relative block w-full px-3 py-2 border border-border placeholder-text-muted text-text-primary focus:outline-none focus:ring-2 focus:ring-brand focus:border-transparent sm:text-sm bg-surface-alt transition-shadow"
                  placeholder="John Doe"
                />
              </div>
            )}
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">Email Address</label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="appearance-none rounded-lg relative block w-full px-3 py-2 border border-border placeholder-text-muted text-text-primary focus:outline-none focus:ring-2 focus:ring-brand focus:border-transparent sm:text-sm bg-surface-alt transition-shadow"
                placeholder="you@example.com"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">Password</label>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="appearance-none rounded-lg relative block w-full px-3 py-2 border border-border placeholder-text-muted text-text-primary focus:outline-none focus:ring-2 focus:ring-brand focus:border-transparent sm:text-sm bg-surface-alt transition-shadow"
                placeholder="••••••••"
              />
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={loading}
              className="group relative w-full flex justify-center py-2.5 px-4 border border-transparent text-sm font-medium rounded-lg text-white bg-brand hover:bg-brand-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-brand transition-all disabled:opacity-70 cursor-pointer shadow-md hover:shadow-lg"
            >
              {loading ? (
                <Loader2 className="animate-spin" size={20} />
              ) : (
                isLogin ? 'Sign In' : 'Create Account'
              )}
            </button>
          </div>
        </form>
        
        <div className="text-center mt-6">
          <button
            type="button"
            onClick={() => {
              setIsLogin(!isLogin);
              setError('');
            }}
            className="text-sm font-medium text-brand hover:text-brand-dark transition-colors cursor-pointer"
          >
            {isLogin ? "Don't have an account? Sign up" : 'Already have an account? Sign in'}
          </button>
        </div>
      </div>
    </div>
  );
}
