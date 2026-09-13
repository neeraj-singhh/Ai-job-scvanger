import { Moon, Sun, Bell, Shield, Monitor } from 'lucide-react'
import { Button } from '@/components/ui/Button'

export default function Settings() {
  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-slate-50">Settings</h1>
        <p className="mt-2 text-slate-400">Manage application settings and preferences.</p>
      </div>

      <div className="space-y-6">
        <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6">
          <div className="flex items-center gap-4 mb-4">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-500/10 text-blue-500">
              <Monitor size={20} />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-slate-50">Appearance</h2>
              <p className="text-sm text-slate-400">Customize how the app looks.</p>
            </div>
          </div>
          <div className="flex gap-4 pl-14">
            <Button variant="outline" className="gap-2 border-primary text-primary bg-primary/5">
              <Moon size={16} /> Dark
            </Button>
            <Button variant="outline" className="gap-2" disabled>
              <Sun size={16} /> Light (Coming soon)
            </Button>
          </div>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6">
          <div className="flex items-center gap-4 mb-4">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-purple-500/10 text-purple-500">
              <Bell size={20} />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-slate-50">Desktop Notifications</h2>
              <p className="text-sm text-slate-400">Manage OS-level notification alerts.</p>
            </div>
          </div>
          <div className="pl-14">
            <label className="flex items-center gap-3 cursor-pointer text-slate-300">
              <input 
                type="checkbox"
                defaultChecked
                className="h-5 w-5 rounded border-slate-700 bg-slate-900 text-primary focus:ring-primary focus:ring-offset-slate-900"
              />
              <span className="font-medium">Enable push notifications for new matches</span>
            </label>
            <div className="mt-4">
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => {
                  if (window.electron) {
                    window.electron.showNotification('Test Notification', 'Desktop notifications are working perfectly!')
                  } else {
                    alert('Desktop notifications are only available in the desktop app.')
                  }
                }}
              >
                Send Test Notification
              </Button>
            </div>
          </div>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6">
          <div className="flex items-center gap-4 mb-4">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-green-500/10 text-green-500">
              <Shield size={20} />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-slate-50">Privacy & Security</h2>
              <p className="text-sm text-slate-400">Manage your data.</p>
            </div>
          </div>
          <div className="pl-14">
            <Button variant="destructive" size="sm">
              Delete Account
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
