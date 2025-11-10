import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import './Login.css'

export default function Login() {
  const [email, setEmail] = useState('')
  const navigate = useNavigate()
  const setAuth = useAuthStore((state) => state.setAuth)

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    
    // TODO: Implement OAuth login
    // For now, mock login
    const mockUser = {
      id: 1,
      email,
      is_admin: email.includes('admin'),
      is_banned: false,
      is_whitelisted: true
    }
    const mockToken = 'mock-token-' + Date.now()
    
    setAuth(mockUser, mockToken)
    navigate('/')
  }

  return (
    <div className="login-container">
      <div className="login-box">
        <h1>Distributed Jupyter</h1>
        <p className="login-subtitle">分散型Notebook実行環境</p>
        
        <form onSubmit={handleLogin} className="login-form">
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="login-input"
          />
          <button type="submit" className="login-button">
            Login (Mock)
          </button>
        </form>
        
        <div className="oauth-buttons">
          <button className="oauth-btn google">
            Login with Google
          </button>
          <button className="oauth-btn github">
            Login with GitHub
          </button>
        </div>
      </div>
    </div>
  )
}
