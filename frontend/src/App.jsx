import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import { ThemeProvider } from './context/ThemeContext'
import ProtectedRoute from './components/ProtectedRoute'
import Login from './pages/Login'
import CompanyDetail from './pages/CompanyDetail'
import Dashboard from './pages/Dashboard'
import DataImport from './pages/DataImport'
import Integrations from './pages/Integrations'
import Settings from './pages/Settings'

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/"            element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
            <Route path="/customers/:id" element={<ProtectedRoute><CompanyDetail /></ProtectedRoute>} />
            <Route path="/integrations"  element={<ProtectedRoute><Integrations /></ProtectedRoute>} />
            <Route path="/import"        element={<ProtectedRoute><DataImport /></ProtectedRoute>} />
            <Route path="/settings"      element={<ProtectedRoute><Settings /></ProtectedRoute>} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  )
}

export default App
