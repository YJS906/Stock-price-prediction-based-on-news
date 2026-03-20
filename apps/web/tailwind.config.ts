import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
    "../../packages/shared/src/**/*.{ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        border: "hsl(var(--border))",
        card: "hsl(var(--card))",
        "card-foreground": "hsl(var(--card-foreground))",
        muted: "hsl(var(--muted))",
        "muted-foreground": "hsl(var(--muted-foreground))",
        primary: "hsl(var(--primary))",
        accent: "hsl(var(--accent))",
        positive: "hsl(var(--positive))",
        negative: "hsl(var(--negative))",
        warning: "hsl(var(--warning))"
      },
      boxShadow: {
        panel: "0 16px 48px rgba(3, 9, 18, 0.38)"
      },
      backgroundImage: {
        grid: "linear-gradient(rgba(120,140,180,0.08) 1px, transparent 1px), linear-gradient(90deg, rgba(120,140,180,0.08) 1px, transparent 1px)"
      }
    }
  },
  plugins: []
};

export default config;

