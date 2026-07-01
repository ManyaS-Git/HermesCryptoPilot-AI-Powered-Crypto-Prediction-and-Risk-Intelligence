# Hermes Crypto Prediction Bot Frontend

A complete, modern frontend for the Hermes AI-powered cryptocurrency price prediction platform with agent orchestration.

## Features

### Pages

- **Dashboard** - Real-time overview with key metrics, recent predictions, and active agents
- **Predictions** - Comprehensive view of all predictions with filtering and search
- **Market Analysis** - Technical analysis charts, volatility tracking, and market sentiment
- **Portfolio** - Investment tracking with performance charts and position management
- **Agents** - Monitor AI agents, view their performance metrics, and accuracy tracking
- **Settings** - Configure API endpoints, trading preferences, and notifications

### Components

- **Sidebar Navigation** - Quick access to all pages with active state indicators
- **Stat Cards** - Display key metrics with color-coded indicators
- **Prediction Cards** - Show prediction details with confidence levels and returns
- **Agent Status** - Display agent health, accuracy, and prediction counts
- **Charts** - Interactive Recharts for price movements, volatility, and portfolio allocation

### Design

- **Dark Theme** - Professional dark UI optimized for extended trading sessions
- **Responsive Layout** - Works seamlessly on desktop and tablet devices
- **Color System** - Strategic use of purple (#8b5cf6), cyan (#06b6d4), and status colors
- **Modern Typography** - Clean, readable fonts with proper hierarchy

## Tech Stack

- **Next.js 16** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS v4** - Utility-first styling
- **Recharts** - Interactive data visualization
- **shadcn/ui** - High-quality UI components
- **Lucide React** - Modern icon library

## Getting Started

### Installation

```bash
# Install dependencies
pnpm install

# Start development server
pnpm dev
```

The app will be available at `http://localhost:3000`

### Environment Configuration

Create a `.env.local` file or update environment variables:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

## API Integration

The frontend connects to a backend API at `/api` endpoint. Key endpoints used:

- `GET /api/predictions` - Fetch all predictions
- `GET /api/agents` - Get agent status and performance
- `GET /api/portfolio` - Get portfolio data
- `GET /api/analysis/{symbol}` - Get market analysis for a symbol
- `GET /api/dashboard/stats` - Get dashboard statistics
- `POST /api/predictions` - Create new prediction

See `lib/api.ts` for implementation details.

## Project Structure

```
├── app/
│   ├── layout.tsx           # Root layout with sidebar
│   ├── page.tsx             # Dashboard page
│   ├── predictions/
│   │   └── page.tsx         # Predictions page
│   ├── analysis/
│   │   └── page.tsx         # Market analysis page
│   ├── portfolio/
│   │   └── page.tsx         # Portfolio page
│   ├── agents/
│   │   └── page.tsx         # Agents page
│   ├── settings/
│   │   └── page.tsx         # Settings page
│   └── globals.css          # Global styles & theme
├── components/
│   ├── sidebar.tsx          # Navigation sidebar
│   ├── prediction-card.tsx  # Prediction display component
│   ├── agent-status.tsx     # Agent status component
│   ├── stat-card.tsx        # Statistics card component
│   └── ui/                  # shadcn/ui components
├── lib/
│   ├── api.ts               # API client functions
│   ├── types.ts             # TypeScript type definitions
│   └── utils.ts             # Utility functions
└── public/                  # Static assets
```

## Styling

The application uses Tailwind CSS v4 with custom design tokens:

- **Background**: `#0f0f0f`
- **Card**: `#1a1a1a`
- **Border**: `#2d2d2d`
- **Primary**: `#8b5cf6` (Purple)
- **Accent**: `#06b6d4` (Cyan)
- **Success**: `#10b981` (Green)
- **Warning**: `#f59e0b` (Yellow)
- **Destructive**: `#ef4444` (Red)

## Component Usage Examples

### Stat Card
```tsx
<StatCard
  label="Total Predictions"
  value={42}
  icon={Target}
  color="primary"
/>
```

### Prediction Card
```tsx
<PredictionCard prediction={prediction} />
```

### Agent Status
```tsx
<AgentStatus agent={agent} />
```

## Data Types

All TypeScript types are defined in `lib/types.ts`:

- `Prediction` - Price prediction with confidence and returns
- `Agent` - AI agent with status and performance metrics
- `Portfolio` - Investment portfolio with positions
- `Position` - Individual portfolio position
- `MarketAnalysis` - Technical analysis data
- `DashboardStats` - Dashboard metrics

## Performance Optimizations

- Client-side data fetching with React hooks
- Responsive chart rendering with Recharts
- Optimized image loading
- CSS-in-JS with Tailwind for minimal bundle
- Lazy loading of routes with Next.js

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Future Enhancements

- Real-time WebSocket updates
- Advanced charting with TradingView Lightweight Charts
- Dark/Light theme toggle
- Mobile app version
- Push notifications
- Export functionality

## Deployment

### Vercel (Recommended)

```bash
vercel deploy
```

### Docker

```bash
docker build -t hermes-frontend .
docker run -p 3000:3000 hermes-frontend
```

### Manual Deploy

```bash
pnpm build
pnpm start
```

## Troubleshooting

### Port Already in Use
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9
```

### API Connection Issues
- Check that backend server is running on configured URL
- Verify `NEXT_PUBLIC_API_URL` environment variable
- Check browser console for CORS errors

### Missing Components
```bash
npx shadcn@latest add [component-name]
```

## License

This project is part of the Hermes Crypto Prediction Bot ecosystem.

## Support

For issues and questions, contact the development team or open an issue on GitHub.
