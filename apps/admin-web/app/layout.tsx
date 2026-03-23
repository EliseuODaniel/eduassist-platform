import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'EduAssist Platform',
  description: 'Bootstrap panel for EduAssist Platform.',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  );
}

