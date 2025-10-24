'use client';

import { FormEvent, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { httpsCallable } from 'firebase/functions';
import { fns } from '@/lib/firebase';

export default function VerifyPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const email = searchParams.get('email') ?? '';
  const [code, setCode] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError('');

    if (!email) {
      setError('Missing email. Please restart the signup process.');
      return;
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters long.');
      return;
    }

    try {
      setLoading(true);
      const callVerify = httpsCallable<
        { email: string; code: string; password: string },
        { ok: boolean; uid: string }
      >(fns, 'verifyCodeAndCreateUser');
      const response = await callVerify({ email, code: code.trim(), password });
      if (response.data.ok) {
        router.replace('/login?verified=1');
      }
    } catch (err) {
      console.error(err);
      setError('Verification failed. Please confirm your code and try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h1 className="mb-6 text-2xl font-semibold">Verify your email</h1>
      <p className="mb-4 text-sm text-gray-600">A six-digit code was sent to {email || 'your email'}.</p>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="code">Verification code</label>
          <input
            id="code"
            type="text"
            inputMode="numeric"
            pattern="[0-9]{6}"
            maxLength={6}
            required
            className="input mt-1 tracking-widest"
            value={code}
            onChange={(event) => setCode(event.target.value.replace(/\D/g, ''))}
          />
        </div>
        <div>
          <label htmlFor="password">Create password</label>
          <input
            id="password"
            type="password"
            required
            className="input mt-1"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
        </div>
        <button type="submit" className="btn w-full" disabled={loading}>
          {loading ? 'Verifying…' : 'Verify & Create Account'}
        </button>
        {error && <p className="error">{error}</p>}
      </form>
    </div>
  );
}
