import Link from "next/link";

import { NewsStream } from "@/components/dashboard/news-stream";
import { SectionHeading } from "@/components/dashboard/section-heading";
import { Button } from "@/components/ui/button";
import { getArticles, getThemes } from "@/lib/api";

export default async function ArticlesPage() {
  const [articles, themes] = await Promise.all([getArticles(), getThemes()]);

  return (
    <section className="space-y-6">
      <SectionHeading
        eyebrow="Archive"
        title="뉴스 아카이브"
        description="실시간 피드에 노출된 기사를 테마 필터와 함께 다시 확인하는 화면입니다. 실시간 전용 화면은 별도 페이지에서 더 조밀하게 볼 수 있습니다."
        action={
          <Link href="/live">
            <Button variant="ghost">실시간 뉴스로 이동</Button>
          </Link>
        }
      />
      <NewsStream
        items={articles}
        themeOptions={themes.map((theme) => ({ slug: theme.slug, name: theme.name }))}
        title="뉴스 목록"
        description="최신 기사 순으로 정렬되며, 자동 갱신도 계속 유지됩니다."
        limit={20}
      />
    </section>
  );
}
