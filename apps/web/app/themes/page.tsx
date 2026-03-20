import { SectionHeading } from "@/components/dashboard/section-heading";
import { ThemeGrid } from "@/components/dashboard/theme-grid";
import { getThemes } from "@/lib/api";

export default async function ThemesPage() {
  const themes = await getThemes();

  return (
    <section className="space-y-6">
      <SectionHeading
        eyebrow="Theme Universe"
        title="한국 주식 핵심 테마 맵"
        description="국내 뉴스와 해외 뉴스 영향을 함께 반영해 현재 주목도가 높은 투자 테마를 정리했습니다."
      />
      <ThemeGrid themes={themes} />
    </section>
  );
}
