"use client";

import Link from "next/link";
import { ExternalLink, RefreshCcw } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import { formatDateTime, formatDateTimeShort, type ContentMode, type NewsCard } from "@newsalpha/shared";

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
  density?: "comfortable" | "dense";
  initialGeneratedAt?: string | null;
  initialContentMode?: ContentMode;
};

const DEFAULT_POLL_MS = 10000;

function contentModeLabel(mode: ContentMode) {
  if (mode === "live") return "라이브 수집";
  if (mode === "hybrid") return "라이브 + mock";
  return "mock 피드";
}

function linkStatusLabel(status: NewsCard["linkStatus"]) {
  if (status === "google-news") return "Google News 경유";
  if (status === "mock") return "mock 링크";
  if (status === "missing") return "링크 없음";
  return "원문 직결";
}

function refreshStatusLabel(state: "ready" | "refreshing" | "reconnecting") {
  if (state === "refreshing") return "갱신 중";
  if (state === "reconnecting") return "재연결 중";
  return "자동 갱신";
}

export function NewsStream({
  items: initialItems,
  title = "실시간 주식 뉴스",
  description = "페이지를 열어 둔 동안 새 뉴스가 자동으로 상단에 반영됩니다.",
  themeOptions = [],
  fixedThemeSlug,
  limit = 12,
  density = "comfortable",
  initialGeneratedAt = null,
  initialContentMode = "live"
}: NewsStreamProps) {
  const [items, setItems] = useState<NewsCard[]>(initialItems);
  const [activeTheme, setActiveTheme] = useState<string | undefined>(fixedThemeSlug);
  const [lastUpdatedAt, setLastUpdatedAt] = useState<string | null>(initialGeneratedAt ?? initialItems[0]?.publishedAt ?? null);
  const [refreshState, setRefreshState] = useState<"ready" | "refreshing" | "reconnecting">("ready");
  const [newIds, setNewIds] = useState<string[]>([]);
  const [contentMode, setContentMode] = useState<ContentMode>(initialContentMode);
  const seenIdsRef = useRef<Set<string>>(new Set(initialItems.map((item) => item.id)));
  const failureCountRef = useRef(0);
  const pollMsRef = useRef(DEFAULT_POLL_MS);

  useEffect(() => {
    setItems(initialItems);
    setActiveTheme(fixedThemeSlug);
    setLastUpdatedAt(initialGeneratedAt ?? initialItems[0]?.publishedAt ?? null);
    setNewIds([]);
    setContentMode(initialContentMode);
    seenIdsRef.current = new Set(initialItems.map((item) => item.id));
    failureCountRef.current = 0;
    pollMsRef.current = DEFAULT_POLL_MS;
  }, [fixedThemeSlug, initialContentMode, initialGeneratedAt, initialItems]);

  useEffect(() => {
    let cancelled = false;
    let timeoutId: number | undefined;

    async function refresh() {
      if (cancelled) return;
      setRefreshState((previous) => (previous === "reconnecting" ? "reconnecting" : "refreshing"));
      let nextDelay = pollMsRef.current;

      try {
        const response = await getLiveArticles(activeTheme, limit);
        if (cancelled) return;

        const unseenIds = response.items.filter((item) => !seenIdsRef.current.has(item.id)).map((item) => item.id);
        seenIdsRef.current = new Set(response.items.map((item) => item.id));
        setItems(response.items);
        setLastUpdatedAt(response.generatedAt);
        pollMsRef.current = response.pollingIntervalMs || DEFAULT_POLL_MS;
        setContentMode(response.contentMode);
        failureCountRef.current = 0;
        setRefreshState("ready");
        nextDelay = pollMsRef.current;

        if (unseenIds.length > 0) {
          setNewIds((previous) => Array.from(new Set([...unseenIds, ...previous])).slice(0, 20));
        }
      } catch {
        if (cancelled) return;
        failureCountRef.current += 1;
        setRefreshState("reconnecting");
        nextDelay = Math.min(DEFAULT_POLL_MS * 2 ** failureCountRef.current, 60000);
      } finally {
        if (!cancelled) {
          timeoutId = window.setTimeout(refresh, nextDelay);
        }
      }
    }

    void refresh();

    return () => {
      cancelled = true;
      if (timeoutId) window.clearTimeout(timeoutId);
    };
  }, [activeTheme, limit]);

  const filterChips = useMemo(() => {
    if (fixedThemeSlug) return [];
    return themeOptions;
  }, [fixedThemeSlug, themeOptions]);

  const themeSlugMap = useMemo(() => new Map(themeOptions.map((theme) => [theme.name, theme.slug])), [themeOptions]);
  const dense = density === "dense";

  return (
    <Card className="h-full">
      <CardHeader className="space-y-4">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div className="space-y-2">
            <CardTitle>{title}</CardTitle>
            <p className="max-w-3xl text-sm leading-6 text-muted-foreground">{description}</p>
          </div>
          <div className="grid gap-2 rounded-2xl border border-cyan-400/20 bg-cyan-400/10 px-3 py-3 text-xs text-cyan-100">
            <div className="flex items-center justify-between gap-3">
              <span>{refreshStatusLabel(refreshState)}</span>
              <span>{contentModeLabel(contentMode)}</span>
            </div>
            <div className="text-cyan-50/70">
              {lastUpdatedAt ? `${formatDateTimeShort(lastUpdatedAt)} KST 기준` : "최근 갱신 시각 없음"}
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
              전체 실시간 뉴스
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
          <div className="flex items-center gap-2 rounded-2xl border border-emerald-400/20 bg-emerald-400/10 px-3 py-2 text-sm text-emerald-100">
            <RefreshCcw className="h-4 w-4" />
            새 뉴스 {newIds.length}건이 자동 반영됐습니다.
          </div>
        ) : null}
      </CardHeader>

      <CardContent className={dense ? "space-y-3" : "space-y-4"}>
        {items.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-white/10 bg-white/[0.03] p-6 text-sm text-muted-foreground">
            조건에 맞는 뉴스가 아직 없습니다.
          </div>
        ) : null}

        {items.map((item) => {
          const isNew = newIds.includes(item.id);
          const isMock = item.contentMode === "mock";
          const articleHref = `/articles/${item.id}`;

          return (
            <article
              key={item.id}
              className={`rounded-2xl border transition ${
                dense ? "p-3" : "p-4"
              } ${
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
                <Badge>{linkStatusLabel(item.linkStatus)}</Badge>
                {isNew ? <Badge variant="info">새 뉴스</Badge> : null}
                {isMock ? <Badge variant="warning">mock</Badge> : null}
                {item.themes.slice(0, dense ? 4 : 3).map((theme) => {
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

              <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                <div className="min-w-0 flex-1">
                  <Link href={articleHref} className="block">
                    <h3 className={`${dense ? "text-[15px]" : "text-base"} font-medium leading-6 text-white`}>{item.title}</h3>
                  </Link>
                  <p className={`mt-2 ${dense ? "line-clamp-2" : ""} text-sm leading-6 text-muted-foreground`}>
                    {item.translatedSummaryKo ?? item.summary}
                  </p>

                  {item.linkedStocks.length > 0 ? (
                    <div className="mt-3 flex flex-wrap gap-2">
                      {item.linkedStocks.map((stock) => (
                        <Link key={`${item.id}-${stock.ticker}`} href={`/stocks/${stock.ticker}`} prefetch={false}>
                          <Badge variant="warning">{stock.nameKo}</Badge>
                        </Link>
                      ))}
                    </div>
                  ) : null}
                </div>

                <div className="flex shrink-0 flex-row gap-2 lg:flex-col">
                  <Link href={articleHref} prefetch={false}>
                    <Button variant="ghost" className="h-9 rounded-xl">
                      상세 보기
                    </Button>
                  </Link>
                  {item.url ? (
                    <a href={item.url} target="_blank" rel="noreferrer">
                      <Button className="h-9 rounded-xl" variant={item.linkStatus === "direct" ? "default" : "subtle"}>
                        원본보기
                        <ExternalLink className="ml-2 h-4 w-4" />
                      </Button>
                    </a>
                  ) : null}
                </div>
              </div>

              <div className="mt-3 flex flex-wrap items-center justify-between gap-3 text-xs text-muted-foreground">
                <span>
                  {item.sourceName}
                  {item.linkHost ? ` · ${item.linkHost}` : ""}
                  {" · "}
                  {formatDateTime(item.publishedAt)}
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
