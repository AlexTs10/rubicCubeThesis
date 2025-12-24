import type { Metadata } from 'next';
import './globals.css';
import Navigation from '@/components/ui/Navigation';

export const metadata: Metadata = {
  title: 'Rubik\'s Cube Solver - Thesis Project',
  description: 'Interactive Rubik\'s Cube Solver comparing Thistlethwaite, Kociemba, and Korf IDA* algorithms',
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
          {children}
        </main>
      </body>
    </html>
  );
}
