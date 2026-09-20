function PageHeader({ title, description }) {
  return (
    <header className="dashboard-page-header">
      <div className="relative z-10">
        <h2 className="dashboard-page-title">{title}</h2>

        {description && (
          <p className="dashboard-page-description">
            {description}
          </p>
        )}
      </div>
    </header>
  )
}

export default PageHeader
