function PageHeader({ title, description }) {
  return (
    <header className="border-b border-slate-200 bg-white px-8 py-6">
      <h2 className="text-2xl font-semibold tracking-tight text-slate-900">
        {title}
      </h2>

      {description && (
        <p className="mt-1 text-sm text-slate-500">{description}</p>
      )}
    </header>
  )
}

export default PageHeader
