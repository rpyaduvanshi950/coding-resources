'use client';

import { useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { httpsCallable } from 'firebase/functions';
import {
  collection,
  doc,
  getDoc,
  getDocs,
  orderBy,
  query,
  where
} from 'firebase/firestore';
import { signOut, onAuthStateChanged, User } from 'firebase/auth';
import { auth, db, fns } from '@/lib/firebase';

interface Candidate {
  id: string;
  name: string;
  bio?: string;
  imageUrl?: string;
}

interface Post {
  id: string;
  name: string;
  order: number;
  candidates: Candidate[];
}

interface RankedState {
  [postId: string]: {
    [candidateId: string]: number | null;
  };
}

export default function VotePage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [posts, setPosts] = useState<Post[]>([]);
  const [rankings, setRankings] = useState<RankedState>({});
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (authUser) => {
      if (!authUser) {
        router.replace('/login');
        return;
      }

      const userSnap = await getDoc(doc(db, 'users', authUser.uid));
      const hasVoted = userSnap.exists() && userSnap.data()?.hasVoted === true;
      if (hasVoted) {
        await signOut(auth);
        router.replace('/login?locked=1');
        return;
      }

      setUser(authUser);
    });

    return () => unsubscribe();
  }, [router]);

  useEffect(() => {
    if (!user) {
      return;
    }

    const load = async () => {
      setLoading(true);
      try {
        const postsQuery = query(
          collection(db, 'posts'),
          where('isActive', '==', true),
          orderBy('order', 'asc')
        );
        const postSnapshots = await getDocs(postsQuery);
        const fetchedPosts: Post[] = [];
        for (const snapshot of postSnapshots.docs) {
          const postData = snapshot.data();
          const candidatesQuery = query(
            collection(db, 'candidates'),
            where('postId', '==', snapshot.id)
          );
          const candidateSnapshots = await getDocs(candidatesQuery);
          const candidates: Candidate[] = candidateSnapshots.docs.map((docSnap) => ({
            id: docSnap.id,
            name: docSnap.get('name'),
            bio: docSnap.get('bio') ?? undefined,
            imageUrl: docSnap.get('imageUrl') ?? undefined
          }));
          fetchedPosts.push({
            id: snapshot.id,
            name: postData.name,
            order: postData.order,
            candidates
          });
        }
        fetchedPosts.sort((a, b) => a.order - b.order);
        setPosts(fetchedPosts);
        const initialRankings: RankedState = {};
        fetchedPosts.forEach((post) => {
          initialRankings[post.id] = Object.fromEntries(
            post.candidates.map((candidate) => [candidate.id, null])
          );
        });
        setRankings(initialRankings);
        setCurrentIndex(0);
      } catch (err) {
        console.error(err);
        setError('Failed to load ballot. Please refresh.');
      } finally {
        setLoading(false);
      }
    };

    load();
  }, [user]);

  const handleRankChange = (postId: string, candidateId: string, rawValue: string) => {
    setRankings((prev) => {
      const next = { ...prev };
      const postRanks = { ...(next[postId] ?? {}) };
      if (rawValue === '') {
        postRanks[candidateId] = null;
        next[postId] = postRanks;
        return next;
      }
      const value = Number(rawValue);
      Object.entries(postRanks).forEach(([id, rank]) => {
        if (id !== candidateId && rank === value) {
          postRanks[id] = null;
        }
      });
      postRanks[candidateId] = value;
      next[postId] = postRanks;
      return next;
    });
  };

  const isPostComplete = (post: Post) => {
    const ranks = rankings[post.id];
    if (!ranks) return false;
    const values = post.candidates.map((candidate) => ranks[candidate.id]);
    if (values.some((value) => typeof value !== 'number')) {
      return false;
    }
    const expected = new Set<number>();
    for (let i = 1; i <= post.candidates.length; i += 1) {
      expected.add(i);
    }
    values.forEach((value) => {
      if (typeof value === 'number') {
        expected.delete(value);
      }
    });
    return expected.size === 0;
  };

  const allPostsComplete = useMemo(() => posts.every(isPostComplete), [posts, rankings]);

  const goNext = () => {
    setCurrentIndex((prev) => Math.min(prev + 1, posts.length - 1));
  };

  const goBack = () => {
    setCurrentIndex((prev) => Math.max(prev - 1, 0));
  };

  const handleSubmit = async () => {
    if (!user) return;
    setError('');
    setSubmitting(true);

    try {
      const choices = posts.map((post) => {
        const ranks = rankings[post.id];
        const sorted = [...post.candidates].sort((a, b) => {
          const rankA = ranks[a.id] ?? 0;
          const rankB = ranks[b.id] ?? 0;
          return rankA - rankB;
        });
        return {
          postId: post.id,
          preferences: sorted.map((candidate) => candidate.id)
        };
      });

      const submit = httpsCallable<{ choices: { postId: string; preferences: string[] }[] }, { ok: boolean }>(
        fns,
        'submitBallot'
      );
      await submit({ choices });
      await signOut(auth);
      router.replace('/thank-you');
    } catch (err) {
      console.error(err);
      setError('Unable to submit your ballot. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return <p>Loading ballot…</p>;
  }

  if (!posts.length) {
    return <p>No active posts are available right now.</p>;
  }

  const currentPost = posts[currentIndex];
  const currentRanks = rankings[currentPost.id] ?? {};

  return (
    <div className="card">
      <div className="mb-4 flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Cast your ballot</h1>
        <span className="text-sm text-gray-600">
          Post {currentIndex + 1} of {posts.length}
        </span>
      </div>
      <h2 className="mb-4 text-xl font-semibold">{currentPost.name}</h2>
      <div className="space-y-4">
        {currentPost.candidates.map((candidate) => (
          <div key={candidate.id} className="rounded-md border border-gray-200 p-4">
            <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="text-lg font-medium">{candidate.name}</p>
                {candidate.bio && <p className="text-sm text-gray-600">{candidate.bio}</p>}
              </div>
              <div className="sm:w-32">
                <label htmlFor={`rank-${candidate.id}`} className="text-sm text-gray-600">
                  Rank
                </label>
                <select
                  id={`rank-${candidate.id}`}
                  className="input mt-1"
                  value={currentRanks[candidate.id] ?? ''}
                  onChange={(event) => handleRankChange(currentPost.id, candidate.id, event.target.value)}
                >
                  <option value="">Select…</option>
                  {Array.from({ length: currentPost.candidates.length }, (_, index) => index + 1).map((rank) => (
                    <option key={rank} value={rank}>
                      {rank}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>
        ))}
      </div>
      {error && <p className="error mt-4">{error}</p>}
      <div className="mt-6 flex items-center justify-between gap-2">
        <button className="btn" onClick={goBack} disabled={currentIndex === 0}>
          Back
        </button>
        {currentIndex < posts.length - 1 ? (
          <button className="btn" onClick={goNext} disabled={!isPostComplete(currentPost)}>
            Next
          </button>
        ) : (
          <button className="btn" onClick={handleSubmit} disabled={!allPostsComplete || submitting}>
            {submitting ? 'Submitting…' : 'Submit Ballot'}
          </button>
        )}
      </div>
    </div>
  );
}
