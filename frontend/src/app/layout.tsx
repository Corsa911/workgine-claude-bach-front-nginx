import "./globals.css";
export const metadata = {
  title: "Workgine · Рабочее пространство",
  description: "Заказы и исполнители в одном пространстве",
};
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ru">
      <body>{children}</body>
    </html>
  );
}
