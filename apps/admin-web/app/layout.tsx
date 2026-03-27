import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Portal EduAssist',
  description: 'Portal do EduAssist para atendimento, conta e acompanhamento escolar.',
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
