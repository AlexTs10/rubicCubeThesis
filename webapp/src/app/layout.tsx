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
          {children}
        </main>
      </body>
    </html>
  );
}
