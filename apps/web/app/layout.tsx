import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Docuwing — Document Intelligence Platform",
  description: "Transform unstructured documents into structured, actionable knowledge.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
