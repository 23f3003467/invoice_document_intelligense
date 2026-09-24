import "./globals.css";

export const metadata = {
  title: "Document Intelligence",
  description: "Upload a PDF — it gets classified, extracted, and flagged automatically.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
