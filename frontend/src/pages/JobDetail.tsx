import { useParams, Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getJob, getSavedJobs, saveJob, unsaveJob } from '@/lib/api/jobs'
import { getMatches } from '@/lib/api/matches'
import { Button } from '@/components/ui/Button'
import { Loader2, Bookmark, BookmarkCheck, ExternalLink, ArrowLeft, Building, MapPin, DollarSign, Clock } from 'lucide-react'
import { cn } from '@/components/ui/Button'

export default function JobDetail() {
  const { id } = useParams<{ id: string }>()
  const queryClient = useQueryClient()

  const { data: job, isLoading: isLoadingJob } = useQuery({
    queryKey: ['jobs', id],
    queryFn: () => getJob(id!),
    enabled: !!id,
  })

  // Attempt to find if we have a match for this job to show the "Why this job?" explanation
  const { data: matches } = useQuery({
    queryKey: ['matches'],
    queryFn: () => getMatches(),
  })
  const match = matches?.find(m => m.job.id === id)

  const { data: savedJobs } = useQuery({
    queryKey: ['savedJobs'],
    queryFn: getSavedJobs,
  })
  const isSaved = savedJobs?.some(s => s.job.id === id)

  const saveMutation = useMutation({
    mutationFn: () => saveJob(id!),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['savedJobs'] })
  })

  const unsaveMutation = useMutation({
    mutationFn: () => unsaveJob(id!),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['savedJobs'] })
  })

  if (isLoadingJob) {
    return (
      <div className="flex h-[80vh] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  if (!job) {
    return <div className="text-slate-400">Job not found.</div>
  }

  return (
    <div className="mx-auto max-w-4xl space-y-8 pb-16">
      <Link to={-1 as any} className="inline-flex items-center gap-2 text-sm text-slate-400 hover:text-slate-50 transition-colors">
        <ArrowLeft size={16} /> Back
      </Link>

      <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-8 shadow-xl">
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-6">
          <div className="space-y-2">
            <h1 className="text-3xl font-bold tracking-tight text-slate-50">{job.title}</h1>
            <div className="flex flex-wrap items-center gap-x-6 gap-y-3 text-slate-400 mt-2">
              <span className="flex items-center gap-2 font-medium text-slate-300">
                <Building size={18} /> {job.company}
              </span>
              {(job.location || job.remote) && (
                <span className="flex items-center gap-2">
                  <MapPin size={18} /> 
                  {job.remote ? 'Remote' : job.location}
                  {job.remote && job.location && ` (${job.location})`}
                </span>
              )}
              {(job.salary_min || job.salary_max) && (
                <span className="flex items-center gap-2 text-green-400">
                  <DollarSign size={18} /> 
                  {job.salary_min && job.salary_max 
                    ? `${job.salary_min.toLocaleString()} - ${job.salary_max.toLocaleString()}`
                    : job.salary_min 
                      ? `${job.salary_min.toLocaleString()}+` 
                      : `Up to ${job.salary_max?.toLocaleString()}`}
                  {job.salary_currency && ` ${job.salary_currency}`}
                </span>
              )}
              {job.employment_type && (
                <span className="flex items-center gap-2 capitalize">
                  <Clock size={18} /> {job.employment_type.replace('_', ' ')}
                </span>
              )}
            </div>
          </div>

          <div className="flex gap-3 shrink-0">
            <Button 
              variant="outline"
              size="icon"
              className={cn("h-11 w-11", isSaved && "text-primary border-primary/50 bg-primary/10")}
              onClick={() => isSaved ? unsaveMutation.mutate() : saveMutation.mutate()}
            >
              {isSaved ? <BookmarkCheck size={22} fill="currentColor" /> : <Bookmark size={22} />}
            </Button>
            <a href={job.source_url} target="_blank" rel="noopener noreferrer">
              <Button className="h-11 px-6 bg-blue-600 hover:bg-blue-700 text-white gap-2 font-semibold">
                Apply Now <ExternalLink size={18} />
              </Button>
            </a>
          </div>
        </div>
      </div>

      {match && (
        <div className="rounded-xl border border-green-500/20 bg-green-500/5 p-8 relative overflow-hidden">
          <div className="absolute top-0 left-0 w-1 h-full bg-green-500"></div>
          
          <div className="flex items-center gap-4 mb-6">
            <div className="rounded-full bg-green-500/10 px-4 py-1.5 text-lg font-bold text-green-400 border border-green-500/20">
              {Math.round(match.score * 100)}% MATCH
            </div>
            <h2 className="text-xl font-semibold text-slate-200">Why this job?</h2>
          </div>
          
          <div className="space-y-6">
            {match.explanation && (
              <p className="text-slate-300 leading-relaxed bg-slate-950/50 p-4 rounded-lg border border-slate-800">
                {match.explanation}
              </p>
            )}

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-8">
              <div>
                <h3 className="text-sm font-semibold uppercase tracking-wider text-green-400 mb-3 flex items-center gap-2">
                  ✓ Matching Skills
                </h3>
                <ul className="space-y-2">
                  {match.matched_skills.map(skill => (
                    <li key={skill} className="flex items-center gap-2 text-slate-300">
                      <div className="h-1.5 w-1.5 rounded-full bg-green-500"></div>
                      {skill}
                    </li>
                  ))}
                  {match.matched_skills.length === 0 && <li className="text-slate-500 italic">None</li>}
                </ul>
              </div>
              
              <div>
                <h3 className="text-sm font-semibold uppercase tracking-wider text-red-400 mb-3 flex items-center gap-2">
                  ⚠ Missing Skills
                </h3>
                <ul className="space-y-2">
                  {match.missing_skills.map(skill => (
                    <li key={skill} className="flex items-center gap-2 text-slate-400">
                      <div className="h-1.5 w-1.5 rounded-full bg-red-500/50"></div>
                      {skill}
                    </li>
                  ))}
                  {match.missing_skills.length === 0 && <li className="text-slate-500 italic">None</li>}
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="md:col-span-2 space-y-8">
          <section className="space-y-4">
            <h2 className="text-xl font-semibold text-slate-50 border-b border-slate-800 pb-2">Job Description</h2>
            <div className="prose prose-invert max-w-none text-slate-300">
              {job.description_normalized 
                ? <div dangerouslySetInnerHTML={{ __html: job.description_normalized.replace(/\n/g, '<br/>') }} />
                : <div dangerouslySetInnerHTML={{ __html: job.description_raw?.replace(/\n/g, '<br/>') || 'No description available.' }} />
              }
            </div>
          </section>
        </div>

        <div className="space-y-6">
          {job.required_skills.length > 0 && (
            <div className="rounded-xl border border-slate-800 bg-slate-900/30 p-6">
              <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-400 mb-4">Required Skills</h3>
              <div className="flex flex-wrap gap-2">
                {job.required_skills.map(skill => (
                  <span key={skill} className="rounded-md bg-slate-800 px-2.5 py-1 text-sm text-slate-300">
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}

          {job.benefits.length > 0 && (
            <div className="rounded-xl border border-slate-800 bg-slate-900/30 p-6">
              <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-400 mb-4">Benefits</h3>
              <ul className="space-y-2">
                {job.benefits.map((benefit, i) => (
                  <li key={i} className="text-sm text-slate-300 flex items-start gap-2">
                    <span className="text-primary mt-1">•</span> {benefit}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
