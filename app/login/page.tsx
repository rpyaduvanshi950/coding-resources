'use client';

import { FormEvent, useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { signInWithEmailAndPassword, signOut } from 'firebase/auth';
import { doc, getDoc } from 'firebase/firestore';
import { auth, db } from '@/lib/firebase';

export default function LoginPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const verified = searchParams.get('verified');
  const locked = searchParams.get('locked');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [info, setInfo] = useState(() => {
    if (verified) {
      return 'Email verified! You can now log in.';
    }
    if (locked) {
      return 'Your ballot has been submitted and the account is locked.';
    }
    return '';
  });
  const [error, setError] = useState('');

  useEffect(() => {
    const unsubscribe = auth.onAuthStateChanged(async (user) => {
      if (!user) {
        return;
      }
      const profileSnap = await getDoc(doc(db, 'users', user.uid));
      if (!profileSnap.exists()) {
        setError('Account setup incomplete. Please contact support.');
        await signOut(auth);
        return;
      }
      const data = profileSnap.data() as { hasVoted?: boolean };
      if (data.hasVoted) {
        setError('Your ballot has already been submitted and the account is locked.');
        await signOut(auth);
        return;
      }
      router.push('/vote');
    });

    return () => unsubscribe();
  }, [router]);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError('');
    setInfo('');

    try {
      setLoading(true);
      const credentials = await signInWithEmailAndPassword(auth, email.trim(), password);
      const profileSnap = await getDoc(doc(db, 'users', credentials.user.uid));
      if (!profileSnap.exists()) {
        throw new Error('missing-profile');
      }
      const data = profileSnap.data() as { hasVoted?: boolean };
      if (data.hasVoted) {
        setError('Your ballot has already been submitted and the account is locked.');
        await signOut(auth);
        return;
      }
      router.push('/vote');
    } catch (err: any) {
      console.error(err);
      const code = err?.code ?? err?.message;
      if (code === 'auth/user-disabled') {
        setError('Your ballot has already been submitted and the account is locked.');
      } else if (code === 'auth/invalid-login-credentials' || code === 'auth/wrong-password') {
        setError('Incorrect email or password.');
      } else {
        setError('Unable to log in. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h1 className="mb-6 text-2xl font-semibold">Log in to vote</h1>
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
        <div>
          <label htmlFor="password">Password</label>
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
          {loading ? 'Signing in…' : 'Log in'}
        </button>
        {info && <p className="mt-2 text-sm text-green-600">{info}</p>}
        {error && <p className="error">{error}</p>}
      </form>
      <p className="mt-6 text-sm text-gray-600">
        Need an account? <a href="/signup">Request a verification code</a>.
      </p>
    </div>
  );
}
