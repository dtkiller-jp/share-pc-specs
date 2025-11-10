import { useState, useEffect } from 'react'
import axios from 'axios'
import { useAuthStore } from '../store/authStore'
import './AdminDashboard.css'

interface User {
  id: number
  email: string
  is_admin: boolean
  is_banned: boolean
  is_whitelisted: boolean
}

interface ResourceLimit {
  cpu_percent: number
  memory_mb: number
  gpu_memory_mb: number
  storage_mb: number
}

export default function AdminDashboard() {
  const [users, setUsers] = useState<User[]>([])
  const [selectedUser, setSelectedUser] = useState<User | null>(null)
  const [limits, setLimits] = useState<ResourceLimit>({
    cpu_percent: 50,
    memory_mb: 2048,
    gpu_memory_mb: 4096,
    storage_mb: 5120
  })
  const token = useAuthStore((state) => state.token)

  useEffect(() => {
    loadUsers()
  }, [])

  const loadUsers = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/admin/users', {
        headers: { Authorization: `Bearer ${token}` }
      })
      setUsers(response.data)
    } catch (error) {
      console.error('Failed to load users:', error)
    }
  }

  const updateLimits = async () => {
    if (!selectedUser) return

    try {
      await axios.put(
        `http://localhost:8000/api/admin/users/${selectedUser.id}/limits`,
        limits,
        { headers: { Authorization: `Bearer ${token}` } }
      )
      alert('リソース制限を更新しました')
    } catch (error) {
      console.error('Failed to update limits:', error)
      alert('更新に失敗しました')
    }
  }

  const toggleBan = async (userId: number, isBanned: boolean) => {
    try {
      await axios.put(
        `http://localhost:8000/api/admin/users/${userId}`,
        { is_banned: !isBanned },
        { headers: { Authorization: `Bearer ${token}` } }
      )
      loadUsers()
    } catch (error) {
      console.error('Failed to toggle ban:', error)
    }
  }

  const toggleWhitelist = async (userId: number, isWhitelisted: boolean) => {
    try {
      await axios.put(
        `http://localhost:8000/api/admin/users/${userId}`,
        { is_whitelisted: !isWhitelisted },
        { headers: { Authorization: `Bearer ${token}` } }
      )
      loadUsers()
    } catch (error) {
      console.error('Failed to toggle whitelist:', error)
    }
  }

  return (
    <div className="admin-dashboard">
      <h1>管理者ダッシュボード</h1>

      <div className="dashboard-grid">
        <div className="users-panel">
          <h2>ユーザー一覧</h2>
          <div className="users-list">
            {users.map(user => (
              <div
                key={user.id}
                className={`user-item ${selectedUser?.id === user.id ? 'selected' : ''}`}
                onClick={() => setSelectedUser(user)}
              >
                <div className="user-info">
                  <strong>{user.email}</strong>
                  {user.is_admin && <span className="badge admin">Admin</span>}
                  {user.is_banned && <span className="badge banned">BAN</span>}
                  {!user.is_whitelisted && <span className="badge">未承認</span>}
                </div>
                <div className="user-actions">
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      toggleWhitelist(user.id, user.is_whitelisted)
                    }}
                    className={user.is_whitelisted ? 'btn-danger' : 'btn-success'}
                  >
                    {user.is_whitelisted ? '承認解除' : '承認'}
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      toggleBan(user.id, user.is_banned)
                    }}
                    className={user.is_banned ? 'btn-success' : 'btn-danger'}
                  >
                    {user.is_banned ? 'BAN解除' : 'BAN'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="limits-panel">
          <h2>リソース制限設定</h2>
          {selectedUser ? (
            <div className="limits-form">
              <p>ユーザー: <strong>{selectedUser.email}</strong></p>

              <div className="form-group">
                <label>CPU使用率上限 (%)</label>
                <input
                  type="number"
                  value={limits.cpu_percent}
                  onChange={(e) => setLimits({ ...limits, cpu_percent: parseInt(e.target.value) })}
                />
              </div>

              <div className="form-group">
                <label>メモリ上限 (MB)</label>
                <input
                  type="number"
                  value={limits.memory_mb}
                  onChange={(e) => setLimits({ ...limits, memory_mb: parseInt(e.target.value) })}
                />
              </div>

              <div className="form-group">
                <label>GPUメモリ上限 (MB)</label>
                <input
                  type="number"
                  value={limits.gpu_memory_mb}
                  onChange={(e) => setLimits({ ...limits, gpu_memory_mb: parseInt(e.target.value) })}
                />
              </div>

              <div className="form-group">
                <label>ストレージ上限 (MB)</label>
                <input
                  type="number"
                  value={limits.storage_mb}
                  onChange={(e) => setLimits({ ...limits, storage_mb: parseInt(e.target.value) })}
                />
              </div>

              <button onClick={updateLimits} className="btn-primary">
                制限を更新
              </button>
            </div>
          ) : (
            <p className="no-selection">ユーザーを選択してください</p>
          )}
        </div>
      </div>
    </div>
  )
}
