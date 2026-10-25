import { useEffect, useRef, useState } from 'react'

export default function ChatWindow({ messages, onSendMessage, loading }) {
  const [input, setInput] = useState('')
  const [voiceMode, setVoiceMode] = useState(false)
  const [isListening, setIsListening] = useState(false)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [voiceError, setVoiceError] = useState('')
  const previousMessageCount = useRef(messages.length)
  const recognitionRef = useRef(null)
  const speechRequestId = useRef(0)
  const SpeechRecognition =
    typeof window !== 'undefined' &&
    (window.SpeechRecognition || window.webkitSpeechRecognition)
  const voiceSupported =
    Boolean(SpeechRecognition) &&
    typeof window !== 'undefined' &&
    'speechSynthesis' in window &&
    'SpeechSynthesisUtterance' in window

  const stopSpeaking = () => {
    speechRequestId.current += 1
    if (voiceSupported) window.speechSynthesis.cancel()
    setIsSpeaking(false)
  }

  const speakMessage = (text) => {
    if (!voiceSupported) return

    stopSpeaking()
    const requestId = speechRequestId.current
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.onend = () => {
      if (speechRequestId.current === requestId) setIsSpeaking(false)
    }
    utterance.onerror = () => {
      if (speechRequestId.current === requestId) setIsSpeaking(false)
    }

    setIsSpeaking(true)
    window.speechSynthesis.speak(utterance)
  }

  useEffect(() => {
    const hasNewMessage = messages.length > previousMessageCount.current
    previousMessageCount.current = messages.length

    const latestMessage = messages[messages.length - 1]
    if (voiceMode && hasNewMessage && latestMessage?.role === 'assistant') {
      speakMessage(latestMessage.content)
    }
  }, [messages, voiceMode])

  useEffect(() => {
    if (!voiceMode) {
      recognitionRef.current?.abort()
      recognitionRef.current = null
      setIsListening(false)
      setVoiceError('')
      stopSpeaking()
    }
  }, [voiceMode])

  useEffect(() => () => {
    recognitionRef.current?.abort()
    speechRequestId.current += 1
    if (voiceSupported) window.speechSynthesis.cancel()
  }, [])

  const handleSubmit = (event) => {
    event.preventDefault()
    if (!input.trim() || loading) return
    onSendMessage(input.trim())
    setInput('')
  }

  const handleVoiceInput = () => {
    if (isListening) {
      recognitionRef.current?.stop()
      return
    }

    if (!SpeechRecognition) return

    setVoiceError('')
    const recognition = new SpeechRecognition()
    recognition.lang = navigator.language || 'en-US'
    recognition.interimResults = false
    recognition.continuous = false
    recognition.onresult = (event) => {
      const transcript = Array.from(event.results)
        .filter((result) => result.isFinal)
        .map((result) => result[0].transcript)
        .join(' ')
        .trim()

      if (transcript) {
        setInput(transcript)
        onSendMessage(transcript)
      }
    }
    recognition.onerror = (event) => {
      if (event.error !== 'aborted' && event.error !== 'no-speech') {
        setVoiceError(`Voice input error: ${event.error}`)
      } else if (event.error === 'no-speech') {
        setVoiceError('No speech detected. Please try again.')
      }
    }
    recognition.onend = () => {
      recognitionRef.current = null
      setIsListening(false)
    }

    recognitionRef.current = recognition
    setIsListening(true)
    recognition.start()
  }

  return (
    <div className="flex h-[640px] flex-col rounded-2xl border border-slate-200 bg-white shadow-sm">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200 p-4">
        <h2 className="text-xl font-semibold text-slate-800">Document Q&A</h2>
        <label className={`flex items-center gap-2 text-sm ${voiceSupported ? 'text-slate-600' : 'text-slate-400'}`}>
          <input
            type="checkbox"
            checked={voiceMode}
            onChange={(event) => setVoiceMode(event.target.checked)}
            disabled={!voiceSupported}
            className="h-4 w-4 accent-indigo-600"
          />
          Voice chat
        </label>
      </div>

      {!voiceSupported ? (
        <p className="border-b border-slate-200 px-4 py-2 text-xs text-slate-500">
          Voice chat is not supported by this browser. Try a browser with speech recognition and speech synthesis support.
        </p>
      ) : null}

      <div className="flex-1 space-y-4 overflow-y-auto p-4">
        {messages.length === 0 ? (
          <div className="flex h-full items-center justify-center text-center text-sm text-slate-500">
            Upload a document and ask a question.
          </div>
        ) : (
          messages.map((message, index) => (
            <div
              key={index}
              className={`max-w-[85%] rounded-2xl px-4 py-3 ${
                message.role === 'user'
                  ? 'ml-auto bg-indigo-600 text-white'
                  : 'bg-slate-100 text-slate-800'
              }`}
            >
              <div className="whitespace-pre-wrap text-sm leading-6">{message.content}</div>
            </div>
          ))
        )}
      </div>

      <form onSubmit={handleSubmit} className="border-t border-slate-200 p-4">
        {voiceError ? <p role="alert" className="mb-3 text-sm text-red-600">{voiceError}</p> : null}
        <div className="flex gap-3">
          <input
            value={input}
            onChange={(event) => setInput(event.target.value)}
            className="flex-1 rounded-xl border border-slate-300 px-4 py-3 text-sm outline-none focus:border-indigo-400"
            placeholder="Ask a question about the uploaded document..."
            disabled={loading}
          />
          {voiceMode ? (
            <button
              type="button"
              onClick={handleVoiceInput}
              className={`rounded-xl px-4 py-3 text-sm font-medium text-white disabled:bg-slate-400 ${
                isListening ? 'bg-rose-600 hover:bg-rose-500' : 'bg-slate-700 hover:bg-slate-600'
              }`}
              disabled={loading}
              aria-label={isListening ? 'Stop voice input' : 'Start voice input'}
            >
              {isListening ? 'Stop listening' : 'Speak'}
            </button>
          ) : null}
          <button
            type="submit"
            className="rounded-xl bg-indigo-600 px-5 py-3 text-sm font-medium text-white hover:bg-indigo-500 disabled:bg-slate-400"
            disabled={loading || !input.trim()}
          >
            {loading ? 'Thinking...' : 'Send'}
          </button>
        </div>
        {voiceMode ? (
          <p className="mt-2 text-xs text-slate-500" aria-live="polite">
            {isListening
              ? 'Listening... Speak your question.'
              : isSpeaking
                ? 'Reading the response aloud...'
                : 'Select Speak to ask by voice. Answers will be spoken aloud.'}
          </p>
        ) : null}
      </form>
    </div>
  )
}
