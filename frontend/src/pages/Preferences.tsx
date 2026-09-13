import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getPreferences, updatePreferences, PreferenceResponse } from '@/lib/api/user'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Loader2, Plus, X } from 'lucide-react'

export default function Preferences() {
  const queryClient = useQueryClient()
  const { data: preferences, isLoading } = useQuery({
    queryKey: ['preferences'],
    queryFn: getPreferences,
  })

  const [formData, setFormData] = useState<Partial<PreferenceResponse>>({
    preferred_roles: [],
    skills: [],
    preferred_locations: [],
    remote_only: false,
    salary_min: null,
    salary_max: null,
    salary_currency: 'USD',
  })
  
  const [newSkill, setNewSkill] = useState('')
  const [newRole, setNewRole] = useState('')

  useEffect(() => {
    if (preferences) {
      setFormData(preferences)
    }
  }, [preferences])

  const mutation = useMutation({
    mutationFn: (data: Partial<PreferenceResponse>) => updatePreferences(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['preferences'] })
      // Optionally show success toast
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    mutation.mutate(formData)
  }

  const addArrayItem = (key: 'skills' | 'preferred_roles', value: string, setValue: (v: string) => void) => {
    if (!value.trim()) return
    const current = formData[key] || []
    if (!current.includes(value.trim())) {
      setFormData({ ...formData, [key]: [...current, value.trim()] })
    }
    setValue('')
  }

  const removeArrayItem = (key: 'skills' | 'preferred_roles', index: number) => {
    const current = formData[key] || []
    setFormData({ ...formData, [key]: current.filter((_, i) => i !== index) })
  }

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6 pb-12">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-slate-50">Preferences</h1>
        <p className="mt-2 text-slate-400">Tell us what you're looking for, and our AI will find the best matches.</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-8 rounded-xl border border-slate-800 bg-slate-900/50 p-8">
        
        {/* Roles */}
        <div className="space-y-4">
          <h2 className="text-xl font-semibold text-slate-50 border-b border-slate-800 pb-2">Target Roles</h2>
          <div className="flex flex-wrap gap-2 mb-2">
            {formData.preferred_roles?.map((role, idx) => (
              <span key={idx} className="inline-flex items-center gap-1 rounded-md bg-primary/20 px-3 py-1 text-sm font-medium text-primary">
                {role}
                <button type="button" onClick={() => removeArrayItem('preferred_roles', idx)} className="text-primary hover:text-white">
                  <X size={14} />
                </button>
              </span>
            ))}
          </div>
          <div className="flex gap-2">
            <Input 
              value={newRole}
              onChange={(e) => setNewRole(e.target.value)}
              placeholder="e.g. Senior Frontend Engineer"
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault()
                  addArrayItem('preferred_roles', newRole, setNewRole)
                }
              }}
            />
            <Button type="button" variant="outline" onClick={() => addArrayItem('preferred_roles', newRole, setNewRole)}>
              <Plus size={18} /> Add
            </Button>
          </div>
        </div>

        {/* Skills */}
        <div className="space-y-4">
          <h2 className="text-xl font-semibold text-slate-50 border-b border-slate-800 pb-2">Your Skills</h2>
          <div className="flex flex-wrap gap-2 mb-2">
            {formData.skills?.map((skill, idx) => (
              <span key={idx} className="inline-flex items-center gap-1 rounded-md bg-slate-800 px-3 py-1 text-sm font-medium text-slate-300">
                {skill}
                <button type="button" onClick={() => removeArrayItem('skills', idx)} className="text-slate-400 hover:text-white">
                  <X size={14} />
                </button>
              </span>
            ))}
          </div>
          <div className="flex gap-2">
            <Input 
              value={newSkill}
              onChange={(e) => setNewSkill(e.target.value)}
              placeholder="e.g. React, TypeScript, Python"
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault()
                  addArrayItem('skills', newSkill, setNewSkill)
                }
              }}
            />
            <Button type="button" variant="outline" onClick={() => addArrayItem('skills', newSkill, setNewSkill)}>
              <Plus size={18} /> Add
            </Button>
          </div>
        </div>

        {/* Logistics */}
        <div className="space-y-4">
          <h2 className="text-xl font-semibold text-slate-50 border-b border-slate-800 pb-2">Logistics</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-300">Minimum Salary</label>
              <Input 
                type="number"
                value={formData.salary_min || ''}
                onChange={(e) => setFormData({ ...formData, salary_min: e.target.value ? parseInt(e.target.value) : null })}
                placeholder="e.g. 100000"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-300">Currency</label>
              <Input 
                value={formData.salary_currency || 'USD'}
                onChange={(e) => setFormData({ ...formData, salary_currency: e.target.value })}
                placeholder="USD"
              />
            </div>
          </div>
          
          <div className="pt-2">
            <label className="flex items-center gap-3 cursor-pointer text-slate-300">
              <input 
                type="checkbox"
                checked={formData.remote_only || false}
                onChange={(e) => setFormData({ ...formData, remote_only: e.target.checked })}
                className="h-5 w-5 rounded border-slate-700 bg-slate-900 text-primary focus:ring-primary focus:ring-offset-slate-900"
              />
              <span className="font-medium">I am only looking for remote positions</span>
            </label>
          </div>
        </div>

        {mutation.isError && (
          <div className="text-sm text-red-500 font-medium">
            Failed to save preferences.
          </div>
        )}
        
        {mutation.isSuccess && (
          <div className="text-sm text-green-500 font-medium">
            Preferences saved successfully!
          </div>
        )}

        <div className="flex justify-end pt-4">
          <Button type="submit" disabled={mutation.isPending} className="px-8">
            {mutation.isPending ? 'Saving...' : 'Save Preferences'}
          </Button>
        </div>
      </form>
    </div>
  )
}
