import { useEffect, useState } from 'react'
import { io, Socket } from 'socket.io-client'
import { useAuthStore } from '../store/authStore'

export function useSocket() {
  const [socket, setSocket] = useState<Socket | null>(null)
  const token = useAuthStore((state) => state.token)

  useEffect(() => {
    if (!token) return

    const newSocket = io('http://localhost:8000', {
      auth: { token }
    })

    newSocket.on('connect', () => {
      console.log('Connected to server')
    })

    newSocket.on('disconnect', () => {
      console.log('Disconnected from server')
    })

    newSocket.on('error', (error: any) => {
      console.error('Socket error:', error)
    })

    setSocket(newSocket)

    return () => {
      newSocket.close()
    }
  }, [token])

  return socket
}
