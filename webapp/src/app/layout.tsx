import type { Metadata } from 'next';
import './globals.css';
import Navigation from '@/components/ui/Navigation';

export const metadata: Metadata = {
  title: 'Rubik\'s Cube Solver - Thesis Project',
  description: 'Interactive Rubik\'s Cube thesis preview comparing pure Thistlethwaite, Kociemba, and Korf with synthetic preview outputs',
  keywords: ['rubiks cube', 'solver', 'algorithm', 'thistlethwaite', 'kociemba', 'korf', 'ida*'],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="font-sans">
        <Navigation />
        <main className="pt-16 min-h-screen">
          <div className="sticky top-16 z-40 border-b border-amber-500/30 bg-amber-950/90 px-4 py-2 text-center text-sm font-medium text-amber-100 backdrop-blur">
            Synthetic preview only - not live solver telemetry.
          </div>
          {children}
        </main>
      </body>
    </html>
  );
}
