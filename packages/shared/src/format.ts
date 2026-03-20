const KOREA_TIME_ZONE = "Asia/Seoul";

function parseDateTime(value: string): Date {
  const normalized = /(?:[zZ]|[+-]\d{2}:\d{2})$/.test(value) ? value : `${value}Z`;
  return new Date(normalized);
}

function getKoreaDateParts(value: string) {
  const date = parseDateTime(value);
  const formatter = new Intl.DateTimeFormat("en-CA", {
    timeZone: KOREA_TIME_ZONE,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    hourCycle: "h23"
  });

  const parts = formatter.formatToParts(date);
  const map = new Map(parts.map((part) => [part.type, part.value]));

  return {
    year: map.get("year") ?? "0000",
    month: map.get("month") ?? "00",
    day: map.get("day") ?? "00",
    hour: map.get("hour") ?? "00",
    minute: map.get("minute") ?? "00"
  };
}

export function formatWon(value: number): string {
  return new Intl.NumberFormat("ko-KR", {
    style: "currency",
    currency: "KRW",
    maximumFractionDigits: 0
  }).format(value);
}

export function formatPercent(value: number): string {
  return `${value >= 0 ? "+" : ""}${value.toFixed(1)}%`;
}

export function formatCompactNumber(value: number): string {
  return new Intl.NumberFormat("ko-KR", {
    notation: "compact",
    maximumFractionDigits: 1
  }).format(value);
}

export function formatDateTime(value: string): string {
  const { year, month, day, hour, minute } = getKoreaDateParts(value);
  return `${year}. ${month}. ${day}. ${hour}:${minute}`;
}

export function formatDateTimeShort(value: string): string {
  const { month, day, hour, minute } = getKoreaDateParts(value);
  return `${month}. ${day}. ${hour}:${minute}`;
}

export function toConfidenceLabel(score: number): string {
  if (score >= 0.82) return "높음";
  if (score >= 0.68) return "보통";
  return "탐색";
}
