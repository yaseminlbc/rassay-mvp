import { BrowserRouter, Route, Routes } from 'react-router-dom'
import CompanyDetail from './pages/CompanyDetail'
import Dashboard from './pages/Dashboard'
import Integrations from './pages/Integrations'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/customers/:id" element={<CompanyDetail />} />
        <Route path="/integrations" element={<Integrations />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
