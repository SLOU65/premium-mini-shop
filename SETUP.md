# YouTube Mini App - Инструкция по развертыванию

## Требования
- Node.js 18+ 
- npm или pnpm
- YouTube Data API v3 ключ

## Установка

1. **Распаковать архив**
```bash
tar -xzf youtube_miniapp.tar.gz
cd youtube_miniapp
```

2. **Установить зависимости**
```bash
pnpm install
# или
npm install
```

3. **Настроить переменные окружения**

Создайте файл `.env.local` в корне проекта:
```
DATABASE_URL=mysql://user:password@localhost:3306/youtube_miniapp
JWT_SECRET=your-secret-key-here
VITE_APP_ID=your-manus-app-id
OAUTH_SERVER_URL=https://api.manus.im
VITE_OAUTH_PORTAL_URL=https://portal.manus.im
OWNER_OPEN_ID=your-owner-id
OWNER_NAME=Your Name
VITE_APP_TITLE=YouTube Mini App
VITE_APP_LOGO=/logo.svg
BUILT_IN_FORGE_API_URL=https://api.manus.im
BUILT_IN_FORGE_API_KEY=your-api-key
VITE_FRONTEND_FORGE_API_KEY=your-frontend-key
VITE_FRONTEND_FORGE_API_URL=https://api.manus.im
```

4. **Настроить базу данных**
```bash
pnpm db:push
```

5. **Запустить dev сервер**
```bash
pnpm dev
```

Приложение будет доступно на `http://localhost:5173`

## Структура проекта

```
youtube_miniapp/
├── client/              # React frontend
│   ├── src/
│   │   ├── pages/      # Страницы приложения
│   │   ├── components/ # Переиспользуемые компоненты
│   │   ├── lib/        # Утилиты и конфигурация
│   │   └── contexts/   # React контексты
│   └── public/         # Статические файлы
├── server/             # Express backend
│   ├── routers.ts      # tRPC процедуры
│   ├── db.ts           # Функции работы с БД
│   └── youtube.ts      # YouTube API утилиты
├── drizzle/            # Миграции БД
└── shared/             # Общие типы и константы
```

## Функции

- 🔍 **Поиск видео** - поиск до 1000 результатов с фильтрами
- 📊 **Информация о видео** - просмотр статистики и метаданных
- 👥 **Информация о каналах** - данные о каналах и подписчиках
- 🌍 **Многоязычность** - поддержка русского и английского
- 🔐 **Безопасность** - шифрование API ключей AES-256
- 📱 **Адаптивный дизайн** - работает на всех устройствах

## Технологический стек

- **Frontend**: React 19, TypeScript, Tailwind CSS, shadcn/ui
- **Backend**: Express, tRPC, Node.js
- **Database**: MySQL/TiDB с Drizzle ORM
- **Auth**: Manus OAuth
- **API**: YouTube Data API v3

## Лицензия

MIT
