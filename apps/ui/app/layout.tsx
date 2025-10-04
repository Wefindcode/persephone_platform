import type { Metadata } from 'next';
import './globals.css';
import { Steps } from '../components/Steps';

export const metadata: Metadata = {
  title: 'Persephone Platform',
  description: 'Персефона — управление ML-артефактами: загрузка, подготовка, деплой и мониторинг.',
};

export default function RootLayout({ children }: { children: React.ReactNode }): JSX.Element {
  return (
    <html lang="ru" className="bg-neutral-950">
      <body className="min-h-screen bg-neutral-950 font-sans text-neutral-100">
        <div className="mx-auto flex min-h-screen max-w-6xl flex-col px-6 py-10">
          <header className="flex flex-col gap-4 border-b border-neutral-800 pb-6 md:flex-row md:items-center md:justify-between">
            <div>
              <h1 className="text-3xl font-semibold tracking-tight text-neutral-100">Persephone</h1>
              <p className="mt-1 text-sm text-neutral-400">
                Управление жизненным циклом артефакта: от загрузки до мониторинга.
              </p>
            </div>
            <Steps />
          </header>
          <main className="mt-8 flex-1 space-y-6">{children}</main>
          <footer className="mt-8 border-t border-neutral-900 pt-4 text-xs text-neutral-600">
            © {new Date().getFullYear()} Persephone Platform
          </footer>
        </div>
      </body>
    </html>
  );
}
