import { useState, useEffect } from 'react'
import { useSocket } from '../hooks/useSocket'
import CodeCell from '../components/CodeCell'
import './Notebook.css'

interface Cell {
  id: string
  code: string
  output: string
  error: string | null
}

export default function Notebook() {
  const [cells, setCells] = useState<Cell[]>([
    { id: '1', code: '', output: '', error: null }
  ])
  const [notebookName, setNotebookName] = useState('untitled.ipynb')
  const socket = useSocket()

  useEffect(() => {
    if (!socket) return

    socket.on('cell_output', (data: any) => {
      setCells(prev => prev.map(cell =>
        cell.id === data.cell_id
          ? { ...cell, output: data.output, error: data.error }
          : cell
      ))
    })

    return () => {
      socket.off('cell_output')
    }
  }, [socket])

  const addCell = () => {
    const newCell: Cell = {
      id: Date.now().toString(),
      code: '',
      output: '',
      error: null
    }
    setCells([...cells, newCell])
  }

  const updateCell = (id: string, code: string) => {
    setCells(prev => prev.map(cell =>
      cell.id === id ? { ...cell, code } : cell
    ))
  }

  const executeCell = (id: string) => {
    const cell = cells.find(c => c.id === id)
    if (!cell || !socket) return

    socket.emit('execute_cell', {
      notebook_path: notebookName,
      code: cell.code,
      cell_id: id
    })
  }

  const deleteCell = (id: string) => {
    if (cells.length === 1) return
    setCells(prev => prev.filter(cell => cell.id !== id))
  }

  const saveNotebook = () => {
    if (!socket) return

    socket.emit('save_notebook', {
      notebook_path: notebookName,
      content: {
        cells: cells.map(c => ({
          cell_type: 'code',
          source: c.code,
          outputs: c.output ? [{ text: c.output }] : []
        }))
      }
    })
  }

  return (
    <div className="notebook-container">
      <div className="notebook-header">
        <input
          type="text"
          value={notebookName}
          onChange={(e) => setNotebookName(e.target.value)}
          className="notebook-name"
        />
        <button onClick={saveNotebook} className="btn-save">
          保存
        </button>
      </div>

      <div className="cells-container">
        {cells.map((cell, index) => (
          <CodeCell
            key={cell.id}
            cell={cell}
            index={index}
            onUpdate={(code) => updateCell(cell.id, code)}
            onExecute={() => executeCell(cell.id)}
            onDelete={() => deleteCell(cell.id)}
          />
        ))}
      </div>

      <button onClick={addCell} className="btn-add-cell">
        + セルを追加
      </button>
    </div>
  )
}
