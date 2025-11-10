import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import axios from 'axios'
import './Login.css'

export default function Login() {
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()
  const setAuth = useAuthStore((state) => state.setAuth)

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!email) {
      setError('メールアドレスを入力してください')
      return
    }

    setLoading(true)
    setError('')

    try {
      const response = await axios.post('/api/auth/login', { email })
      const { user, token } = response.data
      
      setAuth(user, token)
      navigate('/')
    } catch (err: any) {
      const message = err.response?.data?.detail || 'ログインに失敗しました'
      setError(message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-container">
      <div className="login-box">
        <h1>Distributed Jupyter</h1>
        <p className="login-subtitle">分散型Notebook実行環境</p>
        
        <form onSubmit={handleLogin} className="login-form">
          <input
            type="email"
            placeholder="メールアドレスを入力"
            value={email}
            onChange={(e) => {
              setEmail(e.target.value)
              setError('')
            }}
            className="login-input"
            disabled={loading}
          />
          
          {error && (
            <div className="error-message">
              {error}
            </div>
          )}
          
          <button type="submit" className="login-button" disabled={loading}>
            {loading ? 'ログイン中...' : 'ログイン'}
          </button>
        </form>
        
        <p className="login-note">
          ホワイトリストに登録されたメールアドレスでログインできます<br/>
          管理者に連絡してアクセス権限を取得してください
        </p>
      </div>
    </div>
  )
}
