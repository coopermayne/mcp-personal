import { Routes, Route, NavLink } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Entries from './pages/Entries'
import Cards from './pages/Cards'
import Review from './pages/Review'

function App() {
  return (
    <div className="app">
      <nav className="navbar">
        <div className="nav-brand">Lifelogger</div>
        <div className="nav-links">
          <NavLink to="/" end>Dashboard</NavLink>
          <NavLink to="/entries">Entries</NavLink>
          <NavLink to="/cards">Cards</NavLink>
          <NavLink to="/review">Review</NavLink>
        </div>
      </nav>

      <main className="main-content">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/entries" element={<Entries />} />
          <Route path="/cards" element={<Cards />} />
          <Route path="/review" element={<Review />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
