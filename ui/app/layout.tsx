import { Analytics } from '@vercel/analytics/next'
import type { Metadata, Viewport } from 'next'
import { Geist, Geist_Mono } from 'next/font/google'
import './globals.css'
import { Sidebar } from '@/components/sidebar'

const geistSans = Geist({ variable: '--font-geist-sans', subsets: ['latin'] })
const geistMono = Geist_Mono({
  variable: '--font-geist-mono',
  subsets: ['latin'],
})

export const metadata: Metadata = {
  title: 'Hermes Crypto Prediction Bot',
  description: 'AI-powered cryptocurrency price prediction platform with agent orchestration',
  keywords: ['crypto', 'prediction', 'trading', 'AI', 'bitcoin', 'ethereum'],
  openGraph: {
    title: 'Hermes Crypto Prediction Bot',
    description: 'AI-powered cryptocurrency price prediction platform',
    type: 'website',
  },
}

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  userScalable: true,
  themeColor: '#0f0f0f',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" className={`${geistSans.variable} ${geistMono.variable} dark`}>
      <body className="font-sans antialiased bg-background text-foreground">
        <div className="flex">
          <Sidebar />
          <main className="flex-1 ml-64">
            {children}
          </main>
        </div>
        {process.env.NODE_ENV === 'production' && <Analytics />}
      </body>
    </html>
  )
}
