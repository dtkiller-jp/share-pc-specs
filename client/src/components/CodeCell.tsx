import { useState, useRef } from 'react'
import Editor from '@monaco-editor/react'
import type { editor } from 'monaco-editor'
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
  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null)

  const handleExecute = () => {
    setIsExecuting(true)
    onExecute()
    setTimeout(() => setIsExecuting(false), 3000)
  }

  const handleEditorDidMount = (editor: editor.IStandaloneCodeEditor) => {
    editorRef.current = editor

    // Shift+Enter で実行
    editor.addCommand(
      window.monaco.KeyMod.Shift | window.monaco.KeyCode.Enter,
      () => {
        handleExecute()
      }
    )

    // フォーカス
    editor.focus()
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
            {isExecuting ? '実行中...' : '実行 (Shift+Enter)'}
          </button>
          <button onClick={onDelete} className="btn-delete">
            削除
          </button>
        </div>
      </div>

      <div className="cell-editor">
        <Editor
          height="200px"
          defaultLanguage="python"
          value={cell.code}
          onChange={(value) => onUpdate(value || '')}
          onMount={handleEditorDidMount}
          theme="vs-dark"
          options={{
            minimap: { enabled: false },
            fontSize: 14,
            lineNumbers: 'on',
            scrollBeyondLastLine: false,
            automaticLayout: true,
            wordWrap: 'on',
            renderLineHighlight: 'all',
            scrollbar: {
              vertical: 'auto',
              horizontal: 'auto',
              verticalScrollbarSize: 10,
              horizontalScrollbarSize: 10
            },
            padding: { top: 10, bottom: 10 },
            suggestOnTriggerCharacters: true,
            quickSuggestions: {
              other: true,
              comments: false,
              strings: true
            },
            parameterHints: {
              enabled: true
            },
            acceptSuggestionOnEnter: 'on',
            tabCompletion: 'on',
            wordBasedSuggestions: 'allDocuments',
            // Python specific
            autoIndent: 'full',
            formatOnType: true,
            formatOnPaste: true
          }}
        />
      </div>

      {(cell.output || cell.error) && (
        <div className="cell-output">
          <div className="output-label">Out [{index + 1}]:</div>
          {cell.error ? (
            <pre className="output-error">{cell.error}</pre>
          ) : (
            <pre className="output-text">{cell.output || '(出力なし)'}</pre>
          )}
        </div>
      )}
    </div>
  )
}
