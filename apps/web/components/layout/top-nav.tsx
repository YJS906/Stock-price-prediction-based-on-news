import Link from "next/link";

import { Badge } from "@/components/ui/badge";

const links = [
  { href: "/", label: "대시보드" },
  { href: "/themes", label: "테마" },
  { href: "/articles", label: "뉴스" },
  { href: "/stocks", label: "종목" },
  { href: "/admin/ops", label: "Ops" },
  { href: "/admin/evals", label: "모델 평가" }
];

export function TopNav() {
  return (
    <header className="sticky top-0 z-40 border-b border-white/8 bg-slate-950/72 backdrop-blur-xl">
      <div className="mx-auto flex w-full max-w-[1440px] items-center justify-between gap-4 px-5 py-4 lg:px-8">
        <Link href="/" className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-2xl border border-cyan-400/30 bg-cyan-400/10 text-sm font-semibold text-cyan-200">
            NA
          </div>
          <div>
            <div className="font-semibold tracking-[0.2em] text-white/90">NEWSALPHA</div>
            <div className="text-xs text-muted-foreground">한국 주식 뉴스 기반 투자 보조</div>
          </div>
        </Link>

        <nav className="hidden items-center gap-2 lg:flex">
          {links.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="rounded-2xl px-3 py-2 text-sm text-muted-foreground transition hover:bg-white/5 hover:text-white"
            >
              {link.label}
            </Link>
          ))}
        </nav>

        <Badge variant="info">실시간 피드 중심</Badge>
      </div>
    </header>
  );
}
