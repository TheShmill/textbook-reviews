import React from 'react';
import { Link } from 'react-router-dom'; // Import Link from react-router-dom
import './Landing.css'

function Landing() {
  return (
    <div>
        <ul className="navbar">
            <li>
                <Link to="/">Home</Link>
            </li>
            <li>
                <Link to="/pages/search">Search</Link>
            </li>
        </ul>
    </div>
  );
}

export default Landing;
