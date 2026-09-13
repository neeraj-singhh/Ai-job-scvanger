import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { getMatches } from '@/lib/api/matches'
import { getSavedJobs, getJobs } from '@/lib/api/jobs'
import { Briefcase, Bookmark, Target, ArrowRight } from 'lucide-react'

export default function Dashboard() {
  const { data: matches } = useQuery({
    queryKey: ['matches'],
    queryFn: () => getMatches(0),
  })

  const { data: savedJobs } = useQuery({
    queryKey: ['savedJobs'],
    queryFn: getSavedJobs,
  })

  const { data: jobs } = useQuery({
    queryKey: ['jobs'],
    queryFn: () => getJobs({ page_size: 50 }),
  })

  const strongMatches = matches?.filter((m) => m.score >= 0.75) || []
  const recentTopMatches = strongMatches.slice(0, 3)

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-slate-50">Good morning</h1>
        <p className="mt-2 text-slate-400">Your job search is working for you.</p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6 backdrop-blur-sm">
          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-blue-500/10 text-blue-500">
              <Briefcase size={24} />
            </div>
            <div>
              <p className="text-sm font-medium text-slate-400">Total Jobs</p>
              <p className="text-2xl font-bold text-slate-50">{jobs?.length || 0}</p>
            </div>
          </div>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6 backdrop-blur-sm">
          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-green-500/10 text-green-500">
              <Target size={24} />
            </div>
            <div>
              <p className="text-sm font-medium text-slate-400">Strong Matches</p>
              <p className="text-2xl font-bold text-slate-50">{strongMatches.length}</p>
            </div>
          </div>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6 backdrop-blur-sm">
          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-purple-500/10 text-purple-500">
              <Bookmark size={24} />
            </div>
            <div>
              <p className="text-sm font-medium text-slate-400">Saved Jobs</p>
              <p className="text-2xl font-bold text-slate-50">{savedJobs?.length || 0}</p>
            </div>
          </div>
        </div>
      </div>

      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-slate-50">Top Matches</h2>
          <Link to="/matches" className="text-sm font-medium text-primary hover:underline flex items-center gap-1">
            View all <ArrowRight size={16} />
          </Link>
        </div>

        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          {recentTopMatches.length === 0 ? (
            <div className="col-span-full rounded-xl border border-dashed border-slate-800 p-8 text-center text-slate-400">
              No strong matches found yet. Try adjusting your preferences.
            </div>
          ) : (
            recentTopMatches.map((match) => (
              <div key={match.id} className="rounded-xl border border-slate-800 bg-slate-900/50 p-6 flex flex-col justify-between">
                <div>
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <h3 className="text-lg font-semibold text-slate-50 line-clamp-1">{match.job.title}</h3>
                      <p className="text-slate-400">{match.job.company}</p>
                    </div>
                    <div className="rounded-full bg-green-500/10 px-3 py-1 text-sm font-medium text-green-500">
                      {Math.round(match.score * 100)}% MATCH
                    </div>
                  </div>
                  
                  <div className="mt-4 space-y-3">
                    <div>
                      <p className="text-xs font-medium text-slate-500 uppercase tracking-wider mb-1">Matching Skills</p>
                      <div className="flex flex-wrap gap-1">
                        {match.matched_skills.slice(0, 4).map(skill => (
                          <span key={skill} className="inline-flex items-center rounded-md bg-slate-800 px-2 py-1 text-xs font-medium text-slate-300 ring-1 ring-inset ring-slate-700/50">
                            {skill}
                          </span>
                        ))}
                        {match.matched_skills.length > 4 && (
                          <span className="inline-flex items-center rounded-md bg-slate-800 px-2 py-1 text-xs font-medium text-slate-400 ring-1 ring-inset ring-slate-700/50">
                            +{match.matched_skills.length - 4} more
                          </span>
                        )}
                      </div>
                    </div>
                    
                    {match.missing_skills.length > 0 && (
                      <div>
                        <p className="text-xs font-medium text-slate-500 uppercase tracking-wider mb-1">Missing</p>
                        <p className="text-sm text-slate-400 truncate">{match.missing_skills.join(', ')}</p>
                      </div>
                    )}
                  </div>
                </div>
                
                <div className="mt-6 flex items-center justify-end gap-3">
                  <Link to={`/jobs/${match.job.id}`} className="text-sm font-medium text-primary hover:underline">
                    View Details
                  </Link>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}
