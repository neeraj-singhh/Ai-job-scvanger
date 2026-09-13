import { Link } from 'react-router-dom'
import { Bookmark, BookmarkCheck, ExternalLink, MapPin, Building, DollarSign } from 'lucide-react'
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query'
import { JobResponse, getSavedJobs, saveJob, unsaveJob } from '@/lib/api/jobs'
import { JobMatchResponse } from '@/lib/api/matches'
import { Button } from '@/components/ui/Button'
import { cn } from '@/components/ui/Button'

interface JobCardProps {
  job: JobResponse
  match?: JobMatchResponse
}

export function JobCard({ job, match }: JobCardProps) {
  const queryClient = useQueryClient()
  
  const { data: savedJobs } = useQuery({
    queryKey: ['savedJobs'],
    queryFn: getSavedJobs,
  })

  const isSaved = savedJobs?.some(s => s.job.id === job.id)

  const saveMutation = useMutation({
    mutationFn: () => saveJob(job.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['savedJobs'] })
    }
  })

  const unsaveMutation = useMutation({
    mutationFn: () => unsaveJob(job.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['savedJobs'] })
    }
  })

  const toggleSave = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (isSaved) {
      unsaveMutation.mutate()
    } else {
      saveMutation.mutate()
    }
  }

  const score = match ? Math.round(match.score * 100) : null
  const isStrongMatch = score && score >= 75

  return (
    <div className="flex flex-col justify-between rounded-xl border border-slate-800 bg-slate-900/50 p-6 transition-all hover:bg-slate-900 hover:shadow-lg hover:shadow-primary/5">
      <div>
        <div className="flex items-start justify-between gap-4">
          <div className="space-y-1">
            <h3 className="text-xl font-semibold tracking-tight text-slate-50 line-clamp-1">{job.title}</h3>
            <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-sm text-slate-400">
              <span className="flex items-center gap-1.5"><Building size={16} /> {job.company}</span>
              {(job.location || job.remote) && (
                <span className="flex items-center gap-1.5">
                  <MapPin size={16} /> 
                  {job.remote ? 'Remote' : job.location}
                  {job.remote && job.location && ` (${job.location})`}
                </span>
              )}
              {(job.salary_min || job.salary_max) && (
                <span className="flex items-center gap-1.5 text-green-400">
                  <DollarSign size={16} /> 
                  {job.salary_min && job.salary_max 
                    ? `${job.salary_min.toLocaleString()} - ${job.salary_max.toLocaleString()}`
                    : job.salary_min 
                      ? `${job.salary_min.toLocaleString()}+` 
                      : `Up to ${job.salary_max?.toLocaleString()}`}
                  {job.salary_currency && ` ${job.salary_currency}`}
                </span>
              )}
            </div>
          </div>
          <div className="flex items-center gap-2">
            {score !== null && (
              <div className={cn(
                "rounded-full px-3 py-1 text-sm font-medium",
                isStrongMatch ? "bg-green-500/10 text-green-500" : "bg-slate-800 text-slate-300"
              )}>
                {score}% MATCH
              </div>
            )}
            <Button 
              variant="ghost" 
              size="icon" 
              onClick={toggleSave}
              className={cn(isSaved ? "text-primary hover:text-primary/80" : "text-slate-500 hover:text-slate-300")}
              disabled={saveMutation.isPending || unsaveMutation.isPending}
            >
              {isSaved ? <BookmarkCheck size={20} fill="currentColor" /> : <Bookmark size={20} />}
            </Button>
          </div>
        </div>
        
        {match && (
          <div className="mt-5 rounded-lg bg-slate-950 p-4 border border-slate-800/50">
            <div className="space-y-3">
              <div>
                <p className="text-xs font-semibold uppercase tracking-wider text-green-500/80 mb-2 flex items-center gap-1.5">
                  ✓ Matched Skills
                </p>
                <div className="flex flex-wrap gap-1.5">
                  {match.matched_skills.map(skill => (
                    <span key={skill} className="inline-flex items-center rounded bg-slate-800 px-2 py-1 text-xs font-medium text-slate-300 border border-slate-700/50">
                      {skill}
                    </span>
                  ))}
                  {match.matched_skills.length === 0 && <span className="text-sm text-slate-500 italic">No skills matched directly.</span>}
                </div>
              </div>
              
              {match.missing_skills.length > 0 && (
                <div className="pt-2 border-t border-slate-800/50">
                  <p className="text-xs font-semibold uppercase tracking-wider text-red-400/80 mb-2">
                    ⚠ Missing Skills
                  </p>
                  <p className="text-sm text-slate-400">
                    {match.missing_skills.join(', ')}
                  </p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      <div className="mt-6 flex items-center justify-between">
        <span className="text-xs text-slate-500">
          Posted {new Date(job.created_at).toLocaleDateString()} via {job.source}
        </span>
        <div className="flex gap-3">
          <Link to={`/jobs/${job.id}`}>
            <Button variant="outline" size="sm">
              View Details
            </Button>
          </Link>
          <a href={job.source_url} target="_blank" rel="noopener noreferrer">
            <Button size="sm" className="gap-2 bg-primary text-primary-foreground hover:bg-primary/90">
              Apply <ExternalLink size={14} />
            </Button>
          </a>
        </div>
      </div>
    </div>
  )
}
