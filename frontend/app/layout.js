import "./globals.css";

export const metadata = {
  title: "WESH — Window Efficiency Score Calculator",
  description: "Live window thermal efficiency scoring for UK households",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
