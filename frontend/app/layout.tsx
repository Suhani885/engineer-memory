import type { Metadata } from "next";
import type { ReactNode } from "react";
import { Inter } from "next/font/google";

import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

export const metadata: Metadata = {
  title: {
    default: "Engineering Memory",
    template: "%s | Engineering Memory",
  },
  description:
    "The memory layer for engineering teams. Capture, understand, and search your engineering knowledge automatically.",
  keywords: ["engineering", "knowledge base", "GitHub", "AI", "team memory"],
};

export default function RootLayout({
  children,
}: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="min-h-screen bg-background font-sans antialiased">
        {children}
      </body>
    </html>
  );
}
