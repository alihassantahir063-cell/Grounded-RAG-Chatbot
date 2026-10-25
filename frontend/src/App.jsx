import { useState } from 'react'
import FileUpload from './components/FileUpload'
import ChatWindow from './components/ChatWindow'
import SourceBadge from './components/SourceBadge'

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || (import.meta.env.DEV ? '/api' : 'http://localhost:8000')

export default function App() {
  const [messages, setMessages] = useState([])
  const [uploadedFiles, setUploadedFiles] = useState([])
  const [isUploading, setIsUploading] = useState(false)
  const [isLoadingAnswer, setIsLoadingAnswer] = useState(false)
  const [sources, setSources] = useState([])

  const handleFileUpload = async (files) => {
    if (!files.length) return

    setIsUploading(true)
    setSources([])
    const formData = new FormData()
    files.forEach((file) => formData.append('files', file))

    try {
      const response = await fetch(`${API_BASE_URL}/upload`, {
        method: 'POST',
        body: formData,
      })

      const data = await response.json()
      if (!response.ok) {
        throw new Error(data.detail || 'Upload failed')
      }

      setUploadedFiles(data.files || [])
      setMessages([{ role: 'assistant', content: 'Document uploaded successfully. Ask a question about it.' }])
    } catch (error) {
      setMessages([{ role: 'assistant', content: `Upload error: ${error.message}` }])
    } finally {
      setIsUploading(false)
    }
  }

  const handleSendMessage = async (question) => {
    const userMessage = { role: 'user', content: question }
    setMessages((prev) => [...prev, userMessage])
    setIsLoadingAnswer(true)

    try {
      const response = await fetch(`${API_BASE_URL}/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question }),
      })

      const data = await response.json()
      if (!response.ok) {
        throw new Error(data.detail || 'Something went wrong')
      }

      const assistantReply = { role: 'assistant', content: data.answer }
      setMessages((prev) => [...prev, assistantReply])
      setSources(data.sources || [])
    } catch (error) {
      setMessages((prev) => [...prev, { role: 'assistant', content: `Error: ${error.message}` }])
    } finally {
      setIsLoadingAnswer(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-100 p-6">
      <div className="mx-auto max-w-6xl space-y-6">
        <header className="rounded-2xl bg-slate-900 p-6 text-white shadow-lg">
          <h1 className="text-3xl font-bold">Grounded RAG Chatbot</h1>
          <p className="mt-2 text-sm text-slate-300">
            Answers only from the uploaded document. If missing from the document, it refuses to guess.
          </p>
        </header>

        <FileUpload
          onFilesSelected={handleFileUpload}
          uploadedFiles={uploadedFiles}
          isUploading={isUploading}
        />

        <div className="grid gap-6 xl:grid-cols-[2fr_1fr]">
          <ChatWindow messages={messages} onSendMessage={handleSendMessage} loading={isLoadingAnswer} />

          <aside className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
            <h3 className="text-lg font-semibold text-slate-800">Retrieved sources</h3>
            <div className="mt-4 space-y-3">
              {sources.length === 0 ? (
                <p className="text-sm text-slate-500">No source contexts loaded yet.</p>
              ) : (
                sources.map((source, index) => (
                  <div key={`${source.file_name}-${source.page_number ?? 'page'}-${index}`} className="rounded-xl border border-slate-200 bg-slate-50 p-3">
                    <div className="text-sm font-medium text-slate-700">{source.file_name}</div>
                    {source.page_number !== null && source.page_number !== undefined ? (
                      <div className="mt-1 text-xs text-slate-500">Page {source.page_number}</div>
                    ) : null}
                    <p className="mt-2 text-xs leading-5 text-slate-600">{source.content.slice(0, 280)}{source.content.length > 280 ? '...' : ''}</p>
                  </div>
                ))
              )}
            </div>
            <div className="mt-4">
              <SourceBadge source={sources[0]} />
            </div>
          </aside>
        </div>
      </div>
    </div>
  )
}
