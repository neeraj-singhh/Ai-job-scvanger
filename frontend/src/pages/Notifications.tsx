import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getNotifications, markNotificationRead, markAllNotificationsRead } from '@/lib/api/user'
import { Button } from '@/components/ui/Button'
import { Loader2, Bell, CheckCheck, Briefcase } from 'lucide-react'
import { cn } from '@/components/ui/Button'
import { Link } from 'react-router-dom'

export default function Notifications() {
  const queryClient = useQueryClient()
  
  const { data: notifications, isLoading } = useQuery({
    queryKey: ['notifications'],
    queryFn: () => getNotifications(),
  })

  const readMutation = useMutation({
    mutationFn: markNotificationRead,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['notifications'] })
  })

  const readAllMutation = useMutation({
    mutationFn: markAllNotificationsRead,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['notifications'] })
  })

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-50">Notifications</h1>
          <p className="mt-2 text-slate-400">Updates on your matches and job alerts.</p>
        </div>
        {notifications && notifications.length > 0 && (
          <Button 
            variant="outline" 
            className="gap-2"
            onClick={() => readAllMutation.mutate()}
            disabled={readAllMutation.isPending}
          >
            <CheckCheck size={16} /> Mark all read
          </Button>
        )}
      </div>

      {!notifications || notifications.length === 0 ? (
        <div className="rounded-xl border border-dashed border-slate-800 p-12 text-center">
          <div className="flex justify-center mb-4 text-slate-600">
            <Bell size={48} />
          </div>
          <h3 className="mt-2 text-lg font-semibold text-slate-50">You're all caught up!</h3>
          <p className="mt-1 text-sm text-slate-400">
            We'll notify you when we find strong matches for your preferences.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {notifications.map((notification) => (
            <div 
              key={notification.id} 
              className={cn(
                "rounded-xl border p-5 transition-colors flex gap-4",
                notification.read 
                  ? "border-slate-800 bg-slate-900/30" 
                  : "border-primary/30 bg-primary/5"
              )}
            >
              <div className="mt-1">
                {notification.type === 'NEW_MATCH' ? (
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-green-500/10 text-green-500">
                    <Briefcase size={20} />
                  </div>
                ) : (
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-blue-500/10 text-blue-500">
                    <Bell size={20} />
                  </div>
                )}
              </div>
              
              <div className="flex-1 space-y-1">
                <div className="flex items-center justify-between">
                  <h3 className={cn("font-semibold", notification.read ? "text-slate-300" : "text-slate-50")}>
                    {notification.title}
                  </h3>
                  <span className="text-xs text-slate-500">
                    {new Date(notification.created_at).toLocaleString()}
                  </span>
                </div>
                <p className={cn("text-sm leading-relaxed", notification.read ? "text-slate-500" : "text-slate-300")}>
                  {notification.body}
                </p>
                <div className="pt-3 flex gap-3">
                  <Link to="/matches">
                    <Button variant="outline" size="sm">View Matches</Button>
                  </Link>
                  {!notification.read && (
                    <Button 
                      variant="ghost" 
                      size="sm"
                      onClick={() => readMutation.mutate(notification.id)}
                      disabled={readMutation.isPending}
                    >
                      Mark read
                    </Button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
