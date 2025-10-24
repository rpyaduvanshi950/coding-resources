import * as functions from 'firebase-functions';
import * as admin from 'firebase-admin';
import sgMail from '@sendgrid/mail';

admin.initializeApp();

const db = admin.firestore();
const auth = admin.auth();
const SENDGRID_KEY = functions.config().sendgrid?.key as string | undefined;

if (SENDGRID_KEY) {
  sgMail.setApiKey(SENDGRID_KEY);
} else {
  functions.logger.warn('SendGrid API key is not configured. Emails will fail.');
}

const CODE_TTL_MINUTES = 15;

const normalizeEmail = (email: string): string => email.trim().toLowerCase();

export const requestSignupCode = functions.https.onCall(async (data) => {
  const emailRaw = data?.email;
  if (!emailRaw || typeof emailRaw !== 'string') {
    throw new functions.https.HttpsError('invalid-argument', 'Email is required.');
  }

  const email = normalizeEmail(emailRaw);
  const code = Math.floor(100000 + Math.random() * 900000).toString();
  const expiresAt = admin.firestore.Timestamp.fromMillis(
    Date.now() + CODE_TTL_MINUTES * 60 * 1000
  );

  const verificationRef = db.collection('email_verifications').doc(email);
  await verificationRef.set(
    {
      code,
      attempts: 0,
      createdAt: admin.firestore.FieldValue.serverTimestamp(),
      expiresAt
    },
    { merge: true }
  );

  if (!SENDGRID_KEY) {
    throw new functions.https.HttpsError('failed-precondition', 'Email service not configured.');
  }

  const msg = {
    to: email,
    from: {
      email: 'no-reply@one-time-ranked-voting.app',
      name: 'Election Committee'
    },
    subject: 'Your verification code',
    text: `Your verification code is ${code}. It expires in ${CODE_TTL_MINUTES} minutes.`,
    html: `<p>Your verification code is <strong>${code}</strong>. It expires in ${CODE_TTL_MINUTES} minutes.</p>`
  };

  await sgMail.send(msg);

  return { ok: true, ttlMinutes: CODE_TTL_MINUTES };
});

export const verifyCodeAndCreateUser = functions.https.onCall(async (data) => {
  const emailRaw = data?.email;
  const code = data?.code;
  const password = data?.password;
  if (!emailRaw || typeof emailRaw !== 'string') {
    throw new functions.https.HttpsError('invalid-argument', 'Email is required.');
  }
  if (!code || typeof code !== 'string') {
    throw new functions.https.HttpsError('invalid-argument', 'Code is required.');
  }
  if (!password || typeof password !== 'string') {
    throw new functions.https.HttpsError('invalid-argument', 'Password is required.');
  }

  const email = normalizeEmail(emailRaw);
  const verificationRef = db.collection('email_verifications').doc(email);
  const verificationSnap = await verificationRef.get();
  if (!verificationSnap.exists) {
    throw new functions.https.HttpsError('failed-precondition', 'Verification not found.');
  }

  const verificationData = verificationSnap.data() as {
    code: string;
    attempts: number;
    expiresAt: admin.firestore.Timestamp;
  };

  if (verificationData.expiresAt.toMillis() < Date.now()) {
    await verificationRef.delete();
    throw new functions.https.HttpsError('deadline-exceeded', 'Verification code expired.');
  }

  if (verificationData.code !== code) {
    await verificationRef.update({
      attempts: admin.firestore.FieldValue.increment(1)
    });
    throw new functions.https.HttpsError('permission-denied', 'Incorrect code.');
  }

  let userRecord: admin.auth.UserRecord;
  try {
    userRecord = await auth.getUserByEmail(email);
    if (userRecord.disabled) {
      await auth.updateUser(userRecord.uid, { disabled: false });
    }
  } catch (error: any) {
    if (error.code === 'auth/user-not-found') {
      userRecord = await auth.createUser({
        email,
        password,
        emailVerified: true,
        disabled: false
      });
    } else {
      throw error;
    }
  }

  const userRef = db.collection('users').doc(userRecord.uid);
  await userRef.set(
    {
      email,
      hasVoted: false,
      createdAt: admin.firestore.FieldValue.serverTimestamp()
    },
    { merge: true }
  );

  await verificationRef.delete();

  return { ok: true, uid: userRecord.uid };
});

export const submitBallot = functions.https.onCall(async (data, context) => {
  if (!context.auth) {
    throw new functions.https.HttpsError('unauthenticated', 'Authentication required.');
  }

  const uid = context.auth.uid;
  const choices = data?.choices;
  if (!Array.isArray(choices)) {
    throw new functions.https.HttpsError('invalid-argument', 'Choices must be an array.');
  }

  const sanitizedChoices = choices.map((choice: any) => {
    if (!choice || typeof choice.postId !== 'string' || !Array.isArray(choice.preferences)) {
      throw new functions.https.HttpsError('invalid-argument', 'Invalid choice format.');
    }
    const seen = new Set<string>();
    choice.preferences.forEach((candidateId: any) => {
      if (typeof candidateId !== 'string') {
        throw new functions.https.HttpsError('invalid-argument', 'Candidate id must be string.');
      }
      if (seen.has(candidateId)) {
        throw new functions.https.HttpsError('invalid-argument', 'Duplicate candidate detected.');
      }
      seen.add(candidateId);
    });
    if (seen.size === 0) {
      throw new functions.https.HttpsError('invalid-argument', 'Each post must include ranked candidates.');
    }
    return {
      postId: choice.postId,
      preferences: choice.preferences
    };
  });

  await db.runTransaction(async (transaction) => {
    const userRef = db.collection('users').doc(uid);
    const userSnap = await transaction.get(userRef);
    if (!userSnap.exists) {
      throw new functions.https.HttpsError('failed-precondition', 'User profile missing.');
    }
    if (userSnap.get('hasVoted') === true) {
      throw new functions.https.HttpsError('failed-precondition', 'Ballot already submitted.');
    }

    const ballotRef = db.collection('ballots').doc(uid);
    transaction.set(ballotRef, {
      choices: sanitizedChoices,
      submittedAt: admin.firestore.FieldValue.serverTimestamp()
    });
    transaction.update(userRef, { hasVoted: true });
  });

  await auth.updateUser(uid, { disabled: true });
  await auth.revokeRefreshTokens(uid);

  return { ok: true };
});
