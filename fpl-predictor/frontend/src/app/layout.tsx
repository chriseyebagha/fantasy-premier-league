import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "FPL Predictor - Smart Player Recommendations",
  description: "Advanced Fantasy Premier League predictions with captain recommendations, differentials, and price rise tracking",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
