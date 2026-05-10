import forms from "@tailwindcss/forms";

import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./app/**/*.{ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "rgb(37 99 235)",
          50: "rgb(239 246 255)",
          100: "rgb(219 234 254)",
          200: "rgb(191 219 254)",
          300: "rgb(147 197 253)",
          400: "rgb(96 165 250)",
          500: "rgb(59 130 246)",
          600: "rgb(37 99 235)",
          700: "rgb(29 78 216)",
          800: "rgb(30 64 175)",
          900: "rgb(30 58 138)",
        },
        danger: {
          DEFAULT: "rgb(220 38 38)",
          100: "rgb(254 226 226)",
          600: "rgb(220 38 38)",
          700: "rgb(185 28 28)",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      borderRadius: {
        sm: "0.25rem",
        md: "0.375rem",
        lg: "0.5rem",
      },
    },
  },
  plugins: [forms],
} satisfies Config;
