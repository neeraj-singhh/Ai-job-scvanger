import { useQuery } from '@tanstack/react-query'
import { getProfile } from '@/lib/api/user'
import { Loader2, User as UserIcon, Mail, Calendar } from 'lucide-react'

export default function Profile() {
  const { data: profile, isLoading } = useQuery({
    queryKey: ['profile'],
    queryFn: getProfile,
  })

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  if (!profile) return null

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-slate-50">Profile</h1>
        <p className="mt-2 text-slate-400">Manage your account details.</p>
      </div>

      <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-8 space-y-6">
        <div className="flex items-center gap-6">
          <div className="flex h-24 w-24 items-center justify-center rounded-full bg-slate-800 text-slate-400 text-3xl">
            {profile.full_name ? profile.full_name.charAt(0).toUpperCase() : <UserIcon size={40} />}
          </div>
          <div>
            <h2 className="text-2xl font-bold text-slate-50">{profile.full_name || 'Anonymous User'}</h2>
            <p className="text-slate-400 flex items-center gap-2 mt-1">
              <Mail size={16} /> {profile.email}
            </p>
            <p className="text-slate-500 text-sm flex items-center gap-2 mt-1">
              <Calendar size={16} /> Member since {new Date(profile.created_at).toLocaleDateString()}
            </p>
          </div>
        </div>

        {/* Placeholder for future resume upload functionality */}
        <div className="mt-8 pt-6 border-t border-slate-800">
          <h3 className="text-lg font-semibold text-slate-50 mb-4">Resume parsing</h3>
          <div className="rounded-lg border border-dashed border-slate-700 p-8 text-center bg-slate-900/30">
            <p className="text-slate-400">
              Resume parsing and autonomous application submission are premium features coming in a future update.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
