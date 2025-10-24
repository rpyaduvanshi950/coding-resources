# One-Time Ranked Voting Election App

A production-ready Next.js + Firebase web application that lets voters sign up with a single-use code, cast ranked-choice ballots once, and automatically locks their account after submission.

## Features

- Email-based signup with six-digit verification codes delivered via SendGrid
- Firebase Auth, Firestore, and Cloud Functions enforce one ballot per user
- Ranked-choice voting wizard with per-post candidate rankings
- Tailwind CSS UI with reusable button and input utilities
- Hardened Firestore security rules that block ballot tampering and verification-code snooping

## Tech Stack

- Next.js 14 (App Router) + TypeScript + Tailwind CSS
- Firebase Authentication, Firestore, Cloud Functions (Node.js 20)
- SendGrid for transactional email delivery

## Prerequisites

- Node.js 20+
- Firebase CLI (`npm install -g firebase-tools`)
- Yarn or npm (examples below use npm)
- A Firebase project with Authentication and Firestore enabled
- A SendGrid account + API key

## Environment Setup

1. Clone the repository and install dependencies:

   ```bash
   npm install
   cd functions && npm install && cd ..
   ```

2. Create `.env.local` in the project root (see template provided) and populate the Firebase web config:

   ```env
   NEXT_PUBLIC_FB_API_KEY=your-api-key
   NEXT_PUBLIC_FB_AUTH_DOMAIN=your-project.firebaseapp.com
   NEXT_PUBLIC_FB_PROJECT_ID=your-project-id
   NEXT_PUBLIC_FB_APP_ID=your-app-id
   # Optional: set to 'true' to connect to local emulators
   NEXT_PUBLIC_USE_EMULATORS=true
   ```

3. Configure the SendGrid API key for Cloud Functions:

   ```bash
   firebase functions:config:set sendgrid.key="YOUR_SENDGRID_API_KEY"
   ```

4. (Optional) Enable the Firebase web frameworks integration for optimal Next.js hosting:

   ```bash
   firebase experiments:enable webframeworks
   ```

## Local Development

1. Start Firebase emulators (Firestore, Auth, Functions, Hosting):

   ```bash
   npm run emulate
   ```

   When `NEXT_PUBLIC_USE_EMULATORS=true` the Next.js app automatically connects to the emulated services.

2. In another terminal, run the Next.js dev server:

   ```bash
   npm run dev
   ```

3. Seed Firestore with posts and candidates using the Firebase Console or the emulator UI:

   - `/posts/{postId}` with `name`, `order`, `isActive`
   - `/candidates/{candidateId}` with `postId`, `name`, optional `bio`, `imageUrl`

4. Manual test flow:

   1. Go to `http://localhost:3000/signup` and request a code
   2. Use emulator logs or SendGrid email to retrieve the code
   3. Complete verification, then log in
   4. Rank candidates for each post and submit
   5. Confirm you are redirected to the thank-you page and the account is disabled

## Deployment

1. Build the Next.js app:

   ```bash
   npm run build
   ```

2. Deploy Cloud Functions:

   ```bash
   cd functions
   npm run build
   firebase deploy --only functions
   cd ..
   ```

3. Deploy hosting (Next.js). The Firebase web frameworks integration detects Next.js and deploys it behind a managed Cloud Function:

   ```bash
   firebase deploy --only hosting
   ```

## Firestore Data Model

```
/posts/{postId}
  name: string
  order: number
  isActive: boolean

/candidates/{candidateId}
  postId: string
  name: string
  bio?: string
  imageUrl?: string

/users/{uid}
  email: string
  hasVoted: boolean
  createdAt: serverTimestamp

/ballots/{uid}
  submittedAt: serverTimestamp
  choices: [{ postId, preferences: string[] }]

/email_verifications/{email}
  code: string
  attempts: number
  createdAt: serverTimestamp
  expiresAt: Timestamp
```

## Cloud Functions

### `requestSignupCode`
- Generates and stores a six-digit code (15 minute TTL)
- Sends the code via SendGrid

### `verifyCodeAndCreateUser`
- Validates the code and password
- Creates (or re-enables) the Firebase Auth user and Firestore profile
- Deletes the verification document

### `submitBallot`
- Requires authentication
- Validates ranked choices and writes the ballot within a transaction
- Marks `hasVoted`, disables the Auth user, and revokes refresh tokens

## Firestore Security Rules Highlights

- Only authenticated users can read posts and candidates
- Users can read their own profile and ballot, but cannot edit `hasVoted`
- Ballots are write-once via Cloud Functions
- Email verification documents are never exposed to the client

## Notes

- Admins seed posts/candidates via the Firebase Console or scripts
- After a ballot is submitted, the account is disabled and cannot log in again
- Tailwind utility classes (`.btn`, `.input`) live in `styles/globals.css`

## License

MIT
