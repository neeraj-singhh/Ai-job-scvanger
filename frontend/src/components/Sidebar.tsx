import { NavLink, useLocation } from 'react-router-dom'
import { 
  LayoutDashboard, 
  Target, 
  Briefcase, 
  Bookmark, 
  Bell, 
  SlidersHorizontal, 
  User 
} from 'lucide-react'
import { cn } from '@/components/ui/Button'

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Matches', href: '/matches', icon: Target },
  { name: 'Jobs', href: '/jobs', icon: Briefcase },
  { name: 'Saved', href: '/saved', icon: Bookmark },
  { name: 'Notifications', href: '/notifications', icon: Bell },
  { name: 'Preferences', href: '/preferences', icon: SlidersHorizontal },
  { name: 'Profile', href: '/profile', icon: User },
]

export function Sidebar() {
  const location = useLocation()

  return (
    <div className="flex w-64 flex-col border-r border-slate-800 bg-slate-950/50 backdrop-blur-xl">
      <div className="flex h-16 items-center px-6">
        <h1 className="text-lg font-bold tracking-tight text-slate-50 flex items-center gap-2">
          <Target className="text-primary" size={20} />
          AI Job Scavenger
        </h1>
      </div>
      <nav className="flex-1 space-y-1 px-3 py-4">
        {navigation.map((item) => {
          const isActive = location.pathname.startsWith(item.href)
          return (
            <NavLink
              key={item.name}
              to={item.href}
              className={cn(
                'group flex items-center rounded-md px-3 py-2 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-primary/10 text-primary'
                  : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-50'
              )}
            >
              <item.icon
                className={cn(
                  'mr-3 flex-shrink-0 h-5 w-5',
                  isActive ? 'text-primary' : 'text-slate-500 group-hover:text-slate-300'
                )}
                aria-hidden="true"
              />
              {item.name}
            </NavLink>
          )
        })}
      </nav>
    </div>
  )
}
