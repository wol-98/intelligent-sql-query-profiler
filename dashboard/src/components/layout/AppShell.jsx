import Sidebar from './Sidebar'

function AppShell({ activePage, onNavigate, children }) {
  return (
    <div className="flex min-h-screen bg-slate-50">
      <Sidebar activePage={activePage} onNavigate={onNavigate} />

      <main className="min-w-0 flex-1">
        <div className="mx-auto max-w-[1600px] px-6 py-6 lg:px-8">
          {children}
        </div>
      </main>
    </div>
  )
}

export default AppShell
