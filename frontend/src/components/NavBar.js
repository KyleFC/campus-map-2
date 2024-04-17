// Navbar.js
import React from 'react';
import '../App.css'; // Assuming you have an external CSS file for styles
import logo from '../assets/icons/logo.svg';

const Navbar = () => {
  return (
    <nav className="navbar">
      <div className="navbar-container">
        
        <a href="/" className="navbar-brand">
            <img src={logo} alt="Logo" className="logo" />
        </a>
        <ul className="navbar-nav">
          {/* Add more nav items if needed */}
        </ul>
      </div>
    </nav>
  );
};

export default Navbar;
