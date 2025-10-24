import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'One-Time Ranked Voting',
  description: 'Secure ranked-choice election app built with Firebase and Next.js'
};

export default function RootLayout({
  children
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-50">
        <div className="mx-auto max-w-3xl px-4 py-10">{children}</div>
      </body>
    </html>
  );
}
