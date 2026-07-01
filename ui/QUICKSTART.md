# 🚀 Hermes Frontend - Quick Start Guide

Get the Hermes frontend running in 5 minutes!

## Prerequisites
- Node.js 18+
- pnpm installed (`npm install -g pnpm`)

## 1. Start Development Server

```bash
cd /vercel/share/v0-project
pnpm install    # Only needed first time
pnpm dev
```

The app opens at `http://localhost:3000`

## 2. Access the Pages

### 🏠 Dashboard
http://localhost:3000
- Overview of all system metrics
- Recent predictions
- Active agents
- Risk alerts

### 📈 Predictions
http://localhost:3000/predictions
- Search all predictions
- Filter by status
- View prediction details

### 📊 Market Analysis
http://localhost:3000/analysis
- Select cryptocurrency (BTC, ETH, SOL, XRP, ADA)
- View price charts
- Technical analysis
- Volatility tracking

### 💼 Portfolio
http://localhost:3000/portfolio
- Portfolio summary
- Performance charts
- Asset allocation
- Position details

### 🤖 Agents
http://localhost:3000/agents
- Agent status monitoring
- Performance metrics
- Accuracy tracking

### ⚙️ Settings
http://localhost:3000/settings
- API configuration
- Trading preferences
- Notification settings

## 3. Configure API (Optional)

Create `.env.local`:
```bash
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api" > .env.local
```

Without this, API calls will return mock/empty data (handled gracefully).

## 4. Build for Production

```bash
pnpm build    # Compile for production
pnpm start    # Run production server
```

## Features

✨ **6 Full Pages**
- Dashboard with real-time metrics
- Predictions with search/filter
- Market analysis with charts
- Portfolio tracking
- Agent monitoring
- Settings configuration

🎨 **Professional Design**
- Dark theme optimized for trading
- Purple & Cyan color scheme
- Responsive on all devices
- Smooth animations

📊 **Rich Visualizations**
- Interactive charts (Recharts)
- Price movement tracking
- Portfolio allocation
- Technical analysis

🔧 **Production Ready**
- TypeScript strict mode
- Error handling included
- Loading states
- Accessibility features

## File Structure

```
app/
├── page.tsx              ← Dashboard
├── predictions/page.tsx  ← Predictions
├── analysis/page.tsx     ← Market Analysis
├── portfolio/page.tsx    ← Portfolio
├── agents/page.tsx       ← Agents
└── settings/page.tsx     ← Settings

components/
├── sidebar.tsx           ← Navigation
├── prediction-card.tsx   ← Prediction Component
├── agent-status.tsx      ← Agent Component
└── stat-card.tsx         ← Stats Component

lib/
├── types.ts              ← TypeScript Definitions
└── api.ts                ← API Client
```

## Common Commands

```bash
# Development
pnpm dev              # Start dev server

# Building
pnpm build            # Production build
pnpm start            # Run production

# Linting
pnpm lint             # Run eslint

# Add Components
npx shadcn@latest add [component]
```

## Troubleshooting

### Port 3000 Already in Use
```bash
# Kill the process
lsof -ti:3000 | xargs kill -9

# Or use different port
PORT=3001 pnpm dev
```

### API Not Connecting
1. Check backend is running on `http://localhost:8000`
2. Verify `.env.local` has correct URL
3. Check browser console for CORS errors

### Build Fails
```bash
# Clear cache and rebuild
rm -rf .next
pnpm build
```

### Missing Components
```bash
# Install missing shadcn component
npx shadcn@latest add badge
```

## Deployment

### 🎯 Vercel (Easiest)
```bash
npm install -g vercel
vercel
# Follow prompts, done!
```

### 🐳 Docker
```bash
docker build -t hermes .
docker run -p 3000:3000 hermes
```

### 🖥️ Manual
```bash
pnpm build
pnpm start
```

## API Reference

When backend is running, the app fetches from:
- `GET /api/predictions` - List predictions
- `GET /api/agents` - Get agents
- `GET /api/portfolio` - Portfolio data
- `GET /api/analysis/{symbol}` - Market analysis
- `GET /api/dashboard/stats` - Dashboard metrics
- `POST /api/predictions` - Create prediction

See `lib/api.ts` for implementation.

## Customization

### Change Theme Colors
Edit `app/globals.css` in the `.dark` section:
```css
--primary: #8b5cf6;      /* Your color */
--accent: #06b6d4;       /* Your color */
```

### Add New Page
```bash
# Create route
mkdir -p app/new-page
echo "'use client';\nexport default function Page() { return <div>New Page</div>; }" > app/new-page/page.tsx

# Update sidebar in components/sidebar.tsx
```

### Add New Component
```bash
# Create component
touch components/my-component.tsx

# Import and use
import { MyComponent } from '@/components/my-component'
```

## Resources

📚 **Documentation**
- README.md - Full documentation
- FEATURES.md - Feature checklist
- COMPLETION_REPORT.md - Project report

🔗 **Links**
- Next.js: https://nextjs.org
- React: https://react.dev
- Tailwind: https://tailwindcss.com
- shadcn/ui: https://ui.shadcn.com
- Recharts: https://recharts.org

## Quick Tips

1. **Use search in predictions** - Filter by symbol or asset
2. **Toggle symbol** - Change between BTC, ETH, etc. in analysis
3. **View full portfolio** - Scroll table right on mobile
4. **API Configuration** - Update endpoint in settings if needed
5. **Status Colors** - Green = good, Yellow = warning, Red = danger

## Support

- Check README.md for detailed docs
- Review FEATURES.md for feature list
- See COMPLETION_REPORT.md for full report
- Check component files for code examples

---

**Ready to go!** 🎉

```bash
cd /vercel/share/v0-project
pnpm dev
# Open http://localhost:3000
```

Questions? Check the docs or review the component source code!
