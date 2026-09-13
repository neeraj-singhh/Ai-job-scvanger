import { createBrowserRouter, Navigate } from 'react-router-dom'
import { ProtectedRoute } from '@/components/ProtectedRoute'
import AppLayout from '@/layouts/AppLayout'
import Login from '@/pages/Login'
import Signup from '@/pages/Signup'

import Dashboard from '@/pages/Dashboard'
import Matches from '@/pages/Matches'
import Jobs from '@/pages/Jobs'
import JobDetail from '@/pages/JobDetail'
import SavedJobs from '@/pages/SavedJobs'

import Notifications from '@/pages/Notifications'
import Preferences from '@/pages/Preferences'
import Profile from '@/pages/Profile'
import Settings from '@/pages/Settings'

export const router = createBrowserRouter([
  {
    path: '/login',
    element: <Login />,
  },
  {
    path: '/signup',
    element: <Signup />,
  },
  {
    path: '/',
    element: <ProtectedRoute />,
    children: [
      {
        element: <AppLayout />,
        children: [
          { index: true, element: <Navigate to="/dashboard" replace /> },
          { path: 'dashboard', element: <Dashboard /> },
          { path: 'matches', element: <Matches /> },
          { path: 'jobs', element: <Jobs /> },
          { path: 'jobs/:id', element: <JobDetail /> },
          { path: 'saved', element: <SavedJobs /> },
          { path: 'notifications', element: <Notifications /> },
          { path: 'preferences', element: <Preferences /> },
          { path: 'profile', element: <Profile /> },
          { path: 'settings', element: <Settings /> },
        ],
      },
    ],
  },
])
