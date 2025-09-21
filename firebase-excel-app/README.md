# Firebase Excel Exporter

A small Vite + React app that connects to Firestore directly from the browser, fetches an entire collection, and downloads the data as an Excel spreadsheet. It mirrors the workflow of a Node/Python backup script, but keeps everything in the frontend so that non-technical users can export the data on demand.

## Prerequisites

- Node.js 18+
- A Firebase project with Firestore enabled
- Firestore security rules that allow read access for the authenticated users of this tool

## Getting started

```bash
npm install
npm run dev
```

Vite will print the local development URL (typically `http://localhost:5173`).

## Usage

1. Open the app and paste your **web** Firebase configuration JSON into the textarea. You can copy this object from the Firebase console under Project Settings → General → Your apps → Firebase SDK snippet (Config).
2. Enter the name of the Firestore collection you want to back up (for example `eventsUsers2025`).
3. Click **Fetch collection**. The table preview will populate with the first 50 documents.
4. Hit **Download Excel** to download the entire result set as an `.xlsx` file. The exported file uses the same column order as the original Node/Python pipeline (`userId`, `name`, `email`, etc.).

### Resetting state

Use the **Reset** button to clear the table and remove the cached Firebase app instance. This is handy if you want to switch projects without refreshing the browser.

## Security notes

- Never paste Firebase Admin credentials or service account keys into the app. They are meant for server environments only.
- Prefer authenticated access (for example, by requiring sign-in with Google) and strict Firestore rules to protect sensitive collections.
- For large collections consider server-side pagination or Cloud Functions; browsers can struggle when downloading many thousands of rows.

## Building for production

```bash
npm run build
```

The production-ready assets will be emitted into `dist/`.
