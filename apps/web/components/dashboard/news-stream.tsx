"use client";

import Link from "next/link";
import { useEffect, useMemo, useRef, useState } from "react";
import { formatDateTime, type NewsCard } from "@newsalpha/shared";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getLiveArticles } from "@/lib/api";

type ThemeOption = {
  slug: string;
  name: string;
};

type NewsStreamProps = {
  items: NewsCard[];
  title?: string;
  description?: string;
  themeOptions?: ThemeOption[];
  fixedThemeSlug?: string;
  limit?: number;
};

const DEFAULT_POLL_MS = 10000;

export function NewsStream({
  items: initialItems,
  title = "실시간 주식 뉴스",
  description = "페이지를 보고 있는 동안 새 뉴스를 자동으로 반영합니다.",
  themeOptions = [],
  fixedThemeSlug,
  limit = 12
}: NewsStreamProps) {
  const [items, setItems] = useState<NewsCard[]>(initialItems);
  const [activeTheme, setActiveTheme] = useState<string | undefined>(fixedThemeSlug);
  const [lastUpdatedAt, setLastUpdatedAt] = useState<string | null>(initialItems[0]?.publishedAt ?? null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [newIds, setNewIds] = useState<string[]>([]);
  const [pollMs, setPollMs] = useState(DEFAULT_POLL_MS);
  const seenIdsRef = useRef<Set<string>>(new Set(initialItems.map((item) => item.id)));

  useEffect(() => {
    setItems(initialItems);
    setActiveTheme(fixedThemeSlug);
    setLastUpdatedAt(initialItems[0]?.publishedAt ?? null);
    setNewIds([]);
    seenIdsRef.current = new Set(initialItems.map((item) => item.id));
  }, [fixedThemeSlug, initialItems]);

  useEffect(() => {
    let cancelled = false;
    let timeoutId: number | undefined;
    setNewIds([]);

    async function refresh() {
      if (cancelled) return;
      setIsRefreshing(true);
      try {
        const response = await getLiveArticles(activeTheme, limit);
        if (cancelled) return;

        const unseenIds = response.items.filter((item) => !seenIdsRef.current.has(item.id)).map((item) => item.id);
        seenIdsRef.current = new Set(response.items.map((item) => item.id));
        setItems(response.items);
        setLastUpdatedAt(response.generatedAt);
        setPollMs(response.pollingIntervalMs || DEFAULT_POLL_MS);
        if (unseenIds.length > 0) {
          setNewIds((previous) => Array.from(new Set([...unseenIds, ...previous])));
        }
      } catch {
        // Ignore transient polling failures and keep the last rendered feed.
        } finally {
          if (!cancelled) {
            setIsRefreshing(false);
            timeoutId = window.setTimeout(refresh, pollMs);
          }
        }
      }

    void refresh();

    return () => {
      cancelled = true;
      if (timeoutId) window.clearTimeout(timeoutId);
    };
  }, [activeTheme, limit, pollMs]);

  const filterChips = useMemo(() => {
    if (fixedThemeSlug) return [];
    return themeOptions;
  }, [fixedThemeSlug, themeOptions]);

  const themeSlugMap = useMemo(() => new Map(themeOptions.map((theme) => [theme.name, theme.slug])), [themeOptions]);

  return (
    <Card className="h-full">
      <CardHeader className="space-y-4">
        <div className="flex items-start justify-between gap-4">
          <div className="space-y-2">
            <CardTitle>{title}</CardTitle>
            <p className="text-sm leading-6 text-muted-foreground">{description}</p>
          </div>
          <div className="rounded-2xl border border-cyan-400/20 bg-cyan-400/10 px-3 py-2 text-right text-xs text-cyan-100">
            <div>{isRefreshing ? "갱신 중" : "자동 갱신"}</div>
            <div className="mt-1 text-cyan-50/70">
              {lastUpdatedAt ? `${formatDateTime(lastUpdatedAt)} 기준` : "실시간 대기"}
            </div>
          </div>
        </div>

        {filterChips.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            <Button
              type="button"
              variant={activeTheme ? "ghost" : "default"}
              className="h-9 rounded-full"
              onClick={() => setActiveTheme(undefined)}
            >
              전체
            </Button>
            {filterChips.map((theme) => (
              <Button
                key={theme.slug}
                type="button"
                variant={activeTheme === theme.slug ? "default" : "ghost"}
                className="h-9 rounded-full"
                onClick={() => setActiveTheme(theme.slug)}
              >
                {theme.name}
              </Button>
            ))}
          </div>
        ) : null}

        {newIds.length > 0 ? (
          <div className="rounded-2xl border border-emerald-400/20 bg-emerald-400/10 px-3 py-2 text-sm text-emerald-100">
            새 뉴스 {newIds.length}건이 피드에 반영되었습니다.
          </div>
        ) : null}
      </CardHeader>

      <CardContent className="space-y-4">
        {items.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-white/10 bg-white/[0.03] p-6 text-sm text-muted-foreground">
            조건에 맞는 뉴스가 아직 없습니다.
          </div>
        ) : null}

        {items.map((item) => {
          const isNew = newIds.includes(item.id);

          return (
            <article
              key={item.id}
              className={`rounded-2xl border p-4 transition ${
                isNew
                  ? "border-cyan-400/40 bg-cyan-400/[0.06] shadow-[0_0_0_1px_rgba(34,211,238,0.08)]"
                  : "border-white/8 bg-white/[0.03] hover:border-cyan-400/30 hover:bg-cyan-400/[0.04]"
              }`}
            >
              <div className="mb-3 flex flex-wrap items-center gap-2">
                <Badge variant={item.sourceType === "foreign" ? "warning" : "default"}>
                  {item.sourceType === "foreign" ? "해외" : "국내"}
                </Badge>
                <Badge variant="info">{item.importanceLabel}</Badge>
                {isNew ? <Badge variant="info">새 뉴스</Badge> : null}
                {item.themes.slice(0, 3).map((theme) => {
                  const slug = themeSlugMap.get(theme);
                  if (!slug) {
                    return <Badge key={`${item.id}-${theme}`}>{theme}</Badge>;
                  }
                  return (
                    <Link key={`${item.id}-${theme}`} href={`/themes/${slug}`} prefetch={false}>
                      <Badge>{theme}</Badge>
                    </Link>
                  );
                })}
              </div>

              <Link href={`/articles/${item.id}`} className="block">
                <h3 className="text-base font-medium leading-6 text-white">{item.title}</h3>
              </Link>

              <p className="mt-2 text-sm leading-6 text-muted-foreground">{item.translatedSummaryKo ?? item.summary}</p>

              {item.linkedStocks.length > 0 ? (
                <div className="mt-3 flex flex-wrap gap-2">
                  {item.linkedStocks.map((stock) => (
                    <Link key={`${item.id}-${stock.ticker}`} href={`/stocks/${stock.ticker}`} prefetch={false}>
                      <Badge variant="warning">{stock.nameKo}</Badge>
                    </Link>
                  ))}
                </div>
              ) : null}

              <div className="mt-3 flex items-center justify-between gap-4 text-xs text-muted-foreground">
                <span>
                  {item.sourceName} · {formatDateTime(item.publishedAt)}
                </span>
                <span>관련성 {(item.relevanceScore * 100).toFixed(0)}점</span>
              </div>
            </article>
          );
        })}
      </CardContent>
    </Card>
  );
}
