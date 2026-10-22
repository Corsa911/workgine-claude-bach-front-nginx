# Workgine frontend

Основная инструкция запуска находится в ../README.md.

Локальная разработка: `npm ci`, затем `npm run dev`.
Backend должен работать на http://localhost:8000. Для другого адреса задайте
NEXT_PUBLIC_API_URL в .env.local до запуска или сборки.

Проверки: `npm run lint`, `npm run build`.
Форматирование: `npx prettier --write src`.
