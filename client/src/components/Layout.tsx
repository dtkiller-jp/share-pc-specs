import { Outlet, Link } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import './Layout.css'

export default function Layout() {
  const { user, logout } = useAuthStore()

  return (
    <div className="layout">
      <nav className="navbar">
        <div className="nav-brand">Distributed Jupyter</div>
        <div className="nav-links">
          <Link to="/">Notebook</Link>
          {user?.is_admin && <Link to="/admin">Admin</Link>}
          <span className="user-email">{user?.email}</span>
          <button onClick={logout} className="btn-logout">Logout</button>
        </div>
      </nav>
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  )
}
