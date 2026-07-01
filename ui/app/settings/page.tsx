'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Settings, Bell, Lock, Palette, Database, LogOut } from 'lucide-react';

export default function SettingsPage() {
  const [apiUrl, setApiUrl] = useState('http://localhost:8000/api');
  const [riskTolerance, setRiskTolerance] = useState('medium');
  const [notifications, setNotifications] = useState(true);
  const [darkMode, setDarkMode] = useState(true);
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-foreground">Settings</h1>
        <p className="text-muted-foreground mt-1">
          Configure your Hermes prediction bot
        </p>
      </div>

      <div className="max-w-3xl space-y-6">
        {/* API Configuration */}
        <Card className="border-border">
          <CardHeader>
            <div className="flex items-center gap-3">
              <Database className="w-5 h-5 text-primary" />
              <div>
                <CardTitle>API Configuration</CardTitle>
                <CardDescription>
                  Connect to your backend API
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="api-url" className="text-foreground">
                API URL
              </Label>
              <Input
                id="api-url"
                value={apiUrl}
                onChange={(e) => setApiUrl(e.target.value)}
                className="mt-1 bg-card border-border text-foreground"
                placeholder="http://localhost:8000/api"
              />
              <p className="text-xs text-muted-foreground mt-1">
                Set your backend API endpoint for data fetching
              </p>
            </div>
            <Button onClick={handleSave} className="bg-primary hover:bg-primary/90">
              Save Configuration
            </Button>
          </CardContent>
        </Card>

        {/* Trading Preferences */}
        <Card className="border-border">
          <CardHeader>
            <div className="flex items-center gap-3">
              <Settings className="w-5 h-5 text-primary" />
              <div>
                <CardTitle>Trading Preferences</CardTitle>
                <CardDescription>
                  Adjust your trading parameters
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="risk" className="text-foreground">
                Risk Tolerance
              </Label>
              <Select value={riskTolerance} onValueChange={(val) => val && setRiskTolerance(val)}>
                <SelectTrigger id="risk" className="mt-1 bg-card border-border text-foreground">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="low">Low (Conservative)</SelectItem>
                  <SelectItem value="medium">Medium (Balanced)</SelectItem>
                  <SelectItem value="high">High (Aggressive)</SelectItem>
                </SelectContent>
              </Select>
              <p className="text-xs text-muted-foreground mt-1">
                Controls position sizing and stop-loss levels
              </p>
            </div>

            <div className="space-y-3">
              <Label className="text-foreground">Kelly Criterion</Label>
              <div className="grid grid-cols-3 gap-2">
                {['0.25', '0.5', '1.0'].map((value) => (
                  <Button
                    key={value}
                    variant={riskTolerance === value ? 'default' : 'outline'}
                    className="text-sm"
                    onClick={() => setRiskTolerance(value)}
                  >
                    {value}x
                  </Button>
                ))}
              </div>
              <p className="text-xs text-muted-foreground">
                Position sizing multiplier based on Kelly criterion
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Notifications */}
        <Card className="border-border">
          <CardHeader>
            <div className="flex items-center gap-3">
              <Bell className="w-5 h-5 text-primary" />
              <div>
                <CardTitle>Notifications</CardTitle>
                <CardDescription>
                  Manage alert preferences
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              {[
                { label: 'Price Alerts', description: 'Get notified of significant price moves' },
                { label: 'Prediction Updates', description: 'New predictions from agents' },
                { label: 'Risk Warnings', description: 'High risk detected in portfolio' },
                { label: 'Performance Reports', description: 'Daily performance summaries' },
              ].map((item) => (
                <div key={item.label} className="flex items-start gap-3">
                  <input
                    type="checkbox"
                    id={item.label}
                    defaultChecked
                    className="mt-1 w-4 h-4 rounded border-border bg-card"
                  />
                  <label htmlFor={item.label} className="flex-1 cursor-pointer">
                    <p className="text-sm font-medium text-foreground">{item.label}</p>
                    <p className="text-xs text-muted-foreground">{item.description}</p>
                  </label>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Appearance */}
        <Card className="border-border">
          <CardHeader>
            <div className="flex items-center gap-3">
              <Palette className="w-5 h-5 text-primary" />
              <div>
                <CardTitle>Appearance</CardTitle>
                <CardDescription>
                  Customize your interface
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-foreground">Dark Mode</p>
                <p className="text-sm text-muted-foreground">
                  Easy on the eyes during extended trading sessions
                </p>
              </div>
              <input
                type="checkbox"
                checked={darkMode}
                onChange={(e) => setDarkMode(e.target.checked)}
                className="w-6 h-6 rounded-full"
              />
            </div>
          </CardContent>
        </Card>

        {/* Security */}
        <Card className="border-border">
          <CardHeader>
            <div className="flex items-center gap-3">
              <Lock className="w-5 h-5 text-primary" />
              <div>
                <CardTitle>Security</CardTitle>
                <CardDescription>
                  Protect your account
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button variant="outline" className="w-full justify-start gap-2">
              Change Password
            </Button>
            <Button variant="outline" className="w-full justify-start gap-2">
              Enable Two-Factor Authentication
            </Button>
            <Button variant="outline" className="w-full justify-start gap-2">
              View Active Sessions
            </Button>
          </CardContent>
        </Card>

        {/* Danger Zone */}
        <Card className="border-red-500/30 bg-red-500/5">
          <CardHeader>
            <CardTitle className="text-red-400">Danger Zone</CardTitle>
            <CardDescription className="text-red-300">
              Irreversible actions
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button variant="destructive" className="w-full justify-start gap-2">
              <LogOut className="w-4 h-4" />
              Logout
            </Button>
            <Button variant="destructive" className="w-full justify-start gap-2">
              Reset All Settings
            </Button>
          </CardContent>
        </Card>

        {/* Save Feedback */}
        {saved && (
          <div className="p-4 bg-green-500/10 border border-green-500/30 rounded-lg text-green-400">
            Settings saved successfully!
          </div>
        )}
      </div>
    </div>
  );
}
