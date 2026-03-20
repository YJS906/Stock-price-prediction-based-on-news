import type { Metadata } from "next";
import { IBM_Plex_Sans_KR, Space_Grotesk } from "next/font/google";

import { TopNav } from "@/components/layout/top-nav";
import "./globals.css";

const bodyFont = IBM_Plex_Sans_KR({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
  variable: "--font-body"
});

const displayFont = Space_Grotesk({
  subsets: ["latin"],
  weight: ["400", "500", "700"],
  variable: "--font-display"
});

export const metadata: Metadata = {
  title: "NewsAlpha | 한국 주식 뉴스 인텔리전스",
  description: "실시간 뉴스, 테마, 종목 연결, 차트, 예측 밴드를 한 화면에서 보는 한국 주식 보조 플랫폼"
};

export const dynamic = "force-dynamic";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko" className={`${bodyFont.variable} ${displayFont.variable}`}>
      <body className="font-[var(--font-body)] antialiased">
        <TopNav />
        <main className="mx-auto flex min-h-[calc(100vh-76px)] w-full max-w-[1440px] flex-col gap-8 px-5 py-6 lg:px-8">
          {children}
        </main>
      </body>
    </html>
  );
}
