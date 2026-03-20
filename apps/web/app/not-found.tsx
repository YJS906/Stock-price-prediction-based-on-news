import Link from "next/link";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function NotFound() {
  return (
    <div className="flex min-h-[60vh] items-center justify-center">
      <Card className="max-w-xl">
        <CardHeader>
          <CardTitle>요청한 데이터를 찾을 수 없습니다.</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm leading-6 text-muted-foreground">
            mock 데이터 기준으로 조회 가능한 엔티티가 없거나, 아직 파이프라인 시드가 실행되지 않았을 수 있습니다.
          </p>
          <Link href="/">
            <Button>대시보드로 돌아가기</Button>
          </Link>
        </CardContent>
      </Card>
    </div>
  );
}

