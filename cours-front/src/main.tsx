import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import './index.css'
import Layout from './components/Layout'
import ProtectedRoute from './components/ProtectedRoute'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import SubjectPage from './pages/SubjectPage'
import ChapterPage from './pages/ChapterPage'
import StepPage from './pages/StepPage'
import FlashPage from './pages/FlashPage'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<LoginPage />} />
          <Route path="dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
          <Route path="subjects/:subjectId" element={<ProtectedRoute><SubjectPage /></ProtectedRoute>} />
          <Route path="subjects/:subjectId/chapters/:chapterId" element={<ProtectedRoute><ChapterPage /></ProtectedRoute>} />
          <Route path="step/:stepId" element={<ProtectedRoute><StepPage /></ProtectedRoute>} />
          <Route path="flash/:subjectId" element={<ProtectedRoute><FlashPage /></ProtectedRoute>} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  </StrictMode>
)
