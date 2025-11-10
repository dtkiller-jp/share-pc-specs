import { useState } from 'react'
import Editor from '@monaco-editor/react'
import './CodeCell.css'

interface Cell {
  id: string
  code: string
  output: string
  error: string | null
}

interface Props {
  cell: Cell
  index: number
  onUpdate: (code: string) => void
  onExecute: () => void
  onDelete: () => void
}

export default function CodeCell({ cell, index, onUpdate, onExecute, onDelete }: Props) {
  const [isExecuting, setIsExecuting] = useState(false)

  const handleExecute = () => {
    setIsExecuting(true)
    onExecute()
    setTimeout(() => setIsExecuting(false), 1000)
  }

  return (
    <div className="code-cell">
      <div className="cell-header">
        <span className="cell-number">In [{index + 1}]:</span>
        <div className="cell-actions">
          <button
            onClick={handleExecute}
            disabled={isExecuting}
            className="btn-execute"
          >
            {isExecuting ? '実行中...' : '実行'}
          </button>
          <button onClick={onDelete} className="btn-delete">
            削除
          </button>
        </div>
      </div>

      <div className="cell-editor">
        <Editor
          height="150px"
          defaultLanguage="python"
          value={cell.code}
          onChange={(value) => onUpdate(value || '')}
          theme="vs-dark"
          options={{
            minimap: { enabled: false },
            fontSize: 14,
            lineNumbers: 'on',
            scrollBeyondLastLine: false
          }}
        />
      </div>

      {(cell.output || cell.error) && (
        <div className="cell-output">
          <div className="output-label">Out [{index + 1}]:</div>
          {cell.error ? (
            <pre className="output-error">{cell.error}</pre>
          ) : (
            <pre className="output-text">{cell.output}</pre>
          )}
        </div>
      )}
    </div>
  )
}
