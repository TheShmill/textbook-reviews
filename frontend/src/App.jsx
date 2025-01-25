import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import React from 'react'
import './App.css'
import Landing from './pages/Landing'
import Search from './pages/Search'

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<Landing/>}/>
          <Route path="/search" element={<Search/>}/>
        </Routes>
      </div>
    </Router>
  )
}

export default App
