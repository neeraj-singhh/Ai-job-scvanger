import { useQuery } from '@tanstack/react-query'
import { getMatches } from '@/lib/api/matches'
import { JobCard } from '@/components/JobCard'
import { Loader2 } from 'lucide-react'

export default function Matches() {
  const { data: matches, isLoading } = useQuery({
    queryKey: ['matches'],
    queryFn: () => getMatches(0.4), // Only show reasonable matches (score > 40%)
  })

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-bold tracking-tight text-slate-50">Your Matches</h1>
        <p className="text-slate-400">
          Jobs recommended for you based on your profile and preferences, ranked by our AI engine.
        </p>
      </div>

      {isLoading ? (
        <div className="flex h-64 items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      ) : !matches || matches.length === 0 ? (
        <div className="rounded-xl border border-dashed border-slate-800 p-12 text-center">
          <h3 className="mt-2 text-lg font-semibold text-slate-50">No matches found</h3>
          <p className="mt-1 text-sm text-slate-400">
            We couldn't find any strong matches. Try updating your preferences or check back later after we scrape more jobs.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {matches.map((match) => (
            <JobCard key={match.id} job={match.job} match={match} />
          ))}
        </div>
      )}
    </div>
  )
}
