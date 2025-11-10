import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import Login from './pages/Login'
import Notebook from './pages/Notebook'
import AdminDashboard from './pages/AdminDashboard'
import Layout from './components/Layout'

function App() {
  const { user } = useAuthStore()

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/"
          element={user ? <Layout /> : <Navigate to="/login" />}
        >
          <Route index element={<Notebook />} />
          {user?.is_admin && (
            <Route path="admin" element={<AdminDashboard />} />
          )}
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
