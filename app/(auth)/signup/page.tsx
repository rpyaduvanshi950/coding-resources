'use client';

import { FormEvent, useState } from 'react';
import { useRouter } from 'next/navigation';
import { httpsCallable } from 'firebase/functions';
import { fns } from '@/lib/firebase';

export default function SignupPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError('');
    setMessage('');

    const trimmedEmail = email.trim();
    if (!trimmedEmail) {
      setError('Please enter an email address.');
      return;
    }

    try {
      setLoading(true);
      const callRequest = httpsCallable<{ email: string }, { ok: boolean; ttlMinutes: number }>(
        fns,
        'requestSignupCode'
      );
      const response = await callRequest({ email: trimmedEmail });
      if (response.data.ok) {
        setMessage(`Verification code sent! It expires in ${response.data.ttlMinutes} minutes.`);
        router.push(`/verify?email=${encodeURIComponent(trimmedEmail)}`);
      }
    } catch (err) {
      console.error(err);
      setError('Failed to send verification code. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h1 className="mb-6 text-2xl font-semibold">Create your voting account</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="email">Email</label>
          <input
            id="email"
            type="email"
            required
            className="input mt-1"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
          />
        </div>
        <button type="submit" className="btn w-full" disabled={loading}>
          {loading ? 'Sending code…' : 'Send verification code'}
        </button>
        {error && <p className="error">{error}</p>}
        {message && <p className="mt-2 text-sm text-green-600">{message}</p>}
      </form>
    </div>
  );
}
