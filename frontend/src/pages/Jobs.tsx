import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { getJobs } from '@/lib/api/jobs'
import { JobCard } from '@/components/JobCard'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'
import { Loader2, Search } from 'lucide-react'

export default function Jobs() {
  const [query, setQuery] = useState('')
  const [location, setLocation] = useState('')
  const [remoteOnly, setRemoteOnly] = useState(false)
  
  // Debounce the actual API call parameters
  const [filters, setFilters] = useState({ query: '', location: '', remote_only: false })

  const { data: jobs, isLoading } = useQuery({
    queryKey: ['jobs', filters],
    queryFn: () => getJobs({ ...filters, page_size: 50 }),
  })

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setFilters({ query, location, remote_only: remoteOnly })
  }

  const handleReset = () => {
    setQuery('')
    setLocation('')
    setRemoteOnly(false)
    setFilters({ query: '', location: '', remote_only: false })
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-bold tracking-tight text-slate-50">Discover Jobs</h1>
        <p className="text-slate-400">Search and filter through all scraped job listings.</p>
      </div>

      <form onSubmit={handleSearch} className="flex flex-col sm:flex-row gap-4 p-4 rounded-xl border border-slate-800 bg-slate-900/50">
        <div className="flex-1">
          <Input 
            placeholder="Search keywords, titles, companies..." 
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </div>
        <div className="flex-1">
          <Input 
            placeholder="Location..." 
            value={location}
            onChange={(e) => setLocation(e.target.value)}
          />
        </div>
        <label className="flex items-center gap-2 cursor-pointer text-sm text-slate-300 whitespace-nowrap px-2">
          <input 
            type="checkbox" 
            checked={remoteOnly}
            onChange={(e) => setRemoteOnly(e.target.checked)}
            className="rounded border-slate-700 bg-slate-900 text-primary focus:ring-primary focus:ring-offset-slate-900"
          />
          Remote Only
        </label>
        <div className="flex gap-2">
          <Button type="submit" className="gap-2">
            <Search size={16} /> Search
          </Button>
          <Button type="button" variant="outline" onClick={handleReset}>
            Reset
          </Button>
        </div>
      </form>

      {isLoading ? (
        <div className="flex h-64 items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      ) : !jobs || jobs.length === 0 ? (
        <div className="rounded-xl border border-dashed border-slate-800 p-12 text-center">
          <h3 className="mt-2 text-lg font-semibold text-slate-50">No jobs found</h3>
          <p className="mt-1 text-sm text-slate-400">
            No jobs match these filters.
          </p>
          <Button variant="outline" onClick={handleReset} className="mt-4">
            Clear Filters
          </Button>
        </div>
      ) : (
        <div className="space-y-4">
          {jobs.map((job) => (
            <JobCard key={job.id} job={job} />
          ))}
        </div>
      )}
    </div>
  )
}
