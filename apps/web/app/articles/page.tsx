import { NewsStream } from "@/components/dashboard/news-stream";
import { SectionHeading } from "@/components/dashboard/section-heading";
import { getArticles, getThemes } from "@/lib/api";

export default async function ArticlesPage() {
  const [articles, themes] = await Promise.all([getArticles(), getThemes()]);

  return (
    <section className="space-y-6">
      <SectionHeading
        eyebrow="Filtered Feed"
        title="실시간 주식 뉴스 피드"
        description="연예·사건·라이프스타일 등 투자와 직접 관련 없는 뉴스는 제외하고, 최신 기사만 자동으로 반영합니다."
      />
      <NewsStream
        items={articles}
        themeOptions={themes.map((theme) => ({ slug: theme.slug, name: theme.name }))}
        title="실시간 뉴스 목록"
        description="새 뉴스는 페이지 새로고침 없이 최상단에 추가됩니다."
        limit={20}
      />
    </section>
  );
}
