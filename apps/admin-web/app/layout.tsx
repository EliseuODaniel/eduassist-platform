import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'EduAssist Operator Console',
  description: 'Painel autenticado para operar o ecossistema EduAssist.',
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
