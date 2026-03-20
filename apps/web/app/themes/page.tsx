import { SectionHeading } from "@/components/dashboard/section-heading";
import { ThemeGrid } from "@/components/dashboard/theme-grid";
import { getThemes } from "@/lib/api";

export default async function ThemesPage() {
  const themes = await getThemes();

  return (
    <section className="space-y-6">
      <SectionHeading
        eyebrow="Theme Universe"
        title="국내 주식 중심 테마 맵"
        description="국내 뉴스와 미국/해외 뉴스를 함께 반영한 한국 주식 테마 분류 결과입니다."
      />
      <ThemeGrid themes={themes} />
    </section>
  );
}

