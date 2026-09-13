import { logout } from '@/lib/api/auth'
import { LogOut, Settings } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { useNavigate, useLocation } from 'react-router-dom'

export function Topbar() {
  const navigate = useNavigate()
  const location = useLocation()
  
  const getTitle = () => {
    const path = location.pathname.split('/')[1]
    if (!path) return 'Dashboard'
    return path.charAt(0).toUpperCase() + path.slice(1)
  }

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  return (
    <div className="flex h-16 shrink-0 items-center justify-between border-b border-slate-800 bg-slate-950/50 px-8 backdrop-blur-xl">
      <h2 className="text-xl font-semibold tracking-tight text-slate-50">
        {getTitle()}
      </h2>
      <div className="flex items-center gap-4">
        <Button 
          variant="ghost" 
          size="icon" 
          onClick={() => navigate('/settings')}
          className="text-slate-400 hover:text-slate-50"
        >
          <Settings size={20} />
        </Button>
        <Button 
          variant="ghost" 
          size="icon" 
          onClick={handleLogout}
          className="text-slate-400 hover:text-red-400"
        >
          <LogOut size={20} />
        </Button>
      </div>
    </div>
  )
}
