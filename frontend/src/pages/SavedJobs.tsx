import { useQuery } from '@tanstack/react-query'
import { getSavedJobs } from '@/lib/api/jobs'
import { JobCard } from '@/components/JobCard'
import { Loader2 } from 'lucide-react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/Button'

export default function SavedJobs() {
  const { data: savedJobs, isLoading } = useQuery({
    queryKey: ['savedJobs'],
    queryFn: getSavedJobs,
  })

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-bold tracking-tight text-slate-50">Saved Jobs</h1>
        <p className="text-slate-400">Jobs you've bookmarked to apply for later.</p>
      </div>

      {isLoading ? (
        <div className="flex h-64 items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      ) : !savedJobs || savedJobs.length === 0 ? (
        <div className="rounded-xl border border-dashed border-slate-800 p-12 text-center">
          <h3 className="mt-2 text-lg font-semibold text-slate-50">You haven't saved any jobs yet.</h3>
          <p className="mt-1 text-sm text-slate-400">
            Keep track of the best opportunities by saving them.
          </p>
          <div className="mt-6 flex justify-center gap-4">
            <Link to="/matches">
              <Button>Explore your matches</Button>
            </Link>
            <Link to="/jobs">
              <Button variant="outline">Search all jobs</Button>
            </Link>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          {savedJobs.map((savedJob) => (
            <JobCard key={savedJob.id} job={savedJob.job} />
          ))}
        </div>
      )}
    </div>
  )
}
