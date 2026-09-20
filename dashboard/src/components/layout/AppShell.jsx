import Sidebar from './Sidebar'

function AppShell({ activePage, onNavigate, children }) {
  return (
    <div className="dashboard-shell flex min-h-screen">
      <Sidebar activePage={activePage} onNavigate={onNavigate} />

      <main className="dashboard-main">
        <div className="dashboard-content">{children}</div>
      </main>
    </div>
  )
}

export default AppShell
