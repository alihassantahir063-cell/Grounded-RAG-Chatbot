import { useRef } from 'react'

export default function FileUpload({ onFilesSelected, isUploading, uploadedFiles }) {
  const inputRef = useRef(null)

  const selectFiles = (files) => {
    if (files.length > 0 && !isUploading) onFilesSelected(files)
  }

  const handleChange = (event) => {
    selectFiles([...event.target.files])
    event.target.value = ''
  }

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
      <div
        onClick={() => !isUploading && inputRef.current?.click()}
        onDragOver={(event) => event.preventDefault()}
        onDrop={(event) => {
          event.preventDefault()
          selectFiles([...event.dataTransfer.files])
        }}
        onKeyDown={(event) => {
          if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault()
            if (!isUploading) inputRef.current?.click()
          }
        }}
        role="button"
        tabIndex={isUploading ? -1 : 0}
        aria-disabled={isUploading}
        className={`rounded-xl border-2 border-dashed border-slate-300 bg-slate-50 px-6 py-10 text-center transition hover:border-indigo-400 hover:bg-indigo-50 ${
          isUploading ? 'cursor-wait opacity-70' : 'cursor-pointer'
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          multiple
          accept=".pdf,.txt"
          className="hidden"
          onChange={handleChange}
        />
        <p className="text-lg font-semibold text-slate-700">Upload PDF or TXT documents</p>
        <p className="mt-2 text-sm text-slate-500">Drag and drop or click to select</p>
      </div>

      <div className="mt-4 flex items-center justify-between gap-3">
        <div className="text-sm text-slate-600">
          {uploadedFiles.length > 0 ? uploadedFiles.join(', ') : 'No files uploaded yet'}
        </div>
        <button
          type="button"
          onClick={() => inputRef.current?.click()}
          className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-500 disabled:bg-slate-400"
          disabled={isUploading}
        >
          {isUploading ? 'Uploading...' : 'Select files'}
        </button>
      </div>
    </div>
  )
}
