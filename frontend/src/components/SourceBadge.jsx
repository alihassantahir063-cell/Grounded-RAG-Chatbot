export default function SourceBadge({ source }) {
  if (!source) return null

  return (
    <div className="mt-3 rounded-lg border border-indigo-100 bg-indigo-50 px-3 py-2 text-xs text-indigo-800">
      <div className="font-semibold">Source</div>
      <div className="mt-1">{source.file_name}</div>
      {source.page_number !== null && source.page_number !== undefined ? (
        <div className="mt-1">Page {source.page_number}</div>
      ) : null}
    </div>
  )
}
