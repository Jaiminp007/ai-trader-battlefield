import React, { useState, useEffect } from 'react';
import './Dashboard.css';
import CustomDropdown from './CustomDropdown'; // Import the new component

const Dashboard = () => {
  const [navOpen, setNavOpen] = useState(false);
  const [active, setActive] = useState('home');
  const [agents, setAgents] = useState({});
  const [stocks, setStocks] = useState([]);
  const [selectedStock, setSelectedStock] = useState('');
  const [selectedAgents, setSelectedAgents] = useState({
    'left-1': null,
    'left-2': null,
    'left-3': null,
    'right-1': null,
    'right-2': null,
    'right-3': null,
  });
  const [simulationStatus, setSimulationStatus] = useState(null);
  const [simulationResults, setSimulationResults] = useState(null);
  const [isRunning, setIsRunning] = useState(false);

  useEffect(() => {
    const apiBase = process.env.REACT_APP_API_BASE_URL || '';
    fetch(`${apiBase}/api/ai_agents`)
      .then(response => response.json())
      .then(data => setAgents(data))
      .catch(error => console.error('Error fetching agents:', error));
  }, []);

  useEffect(() => {
    const apiBase = process.env.REACT_APP_API_BASE_URL || '';
    fetch(`${apiBase}/api/data_files`)
      .then(res => res.json())
      .then((data) => {
        // Accept either { stocks: [...] } or [...] directly
        const list = Array.isArray(data) ? data : data?.stocks;
        const safe = Array.isArray(list) ? list : [];
        setStocks(safe);
        if (safe.length > 0) {
          setSelectedStock(safe[0].filename || safe[0]);
        }
      })
      .catch(err => {
        console.error('Error fetching data files:', err);
        setStocks([]);
      });
  }, []);

  // Navigation handler for all nav links
  const handleNav = (e, to) => {
    e.preventDefault();
    if (to === 'home') {
      window.location.href = '/';
    } else if (to === 'models') {
      window.location.href = '/models';
    } else if (to === 'about') {
      window.location.href = '/about';
    } else if (to === 'contact') {
      window.location.href = '/contact';
    }
  };

  const handleAgentSelect = (id, agent) => {
    setSelectedAgents(prev => ({ ...prev, [id]: agent }));
  };

  const handleStartSimulation = async () => {
    // Validate all 6 agents are selected
    const agents = Object.values(selectedAgents).filter(Boolean);
    if (agents.length !== 6) {
      alert('Please select all 6 AI agents before starting the simulation.');
      return;
    }

    if (!selectedStock) {
      alert('Please select a stock dataset.');
      return;
    }

    setIsRunning(true);
    setSimulationResults(null);
    setSimulationStatus('Starting simulation...');

    try {
      const apiBase = process.env.REACT_APP_API_BASE_URL || '';
      const response = await fetch(`${apiBase}/api/run`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          agents: agents,
          stock: selectedStock
        })
      });

      const data = await response.json();
      
      if (response.ok) {
        const simId = data.simulation_id;
        setSimulationStatus('Simulation running...');
        
        // Poll for results
        pollSimulationStatus(simId);
      } else {
        throw new Error(data.error || 'Failed to start simulation');
      }
    } catch (error) {
      console.error('Simulation error:', error);
      setSimulationStatus(`Error: ${error.message}`);
      setIsRunning(false);
    }
  };

  const pollSimulationStatus = async (simId) => {
    try {
      const apiBase = process.env.REACT_APP_API_BASE_URL || '';
      const response = await fetch(`${apiBase}/api/simulation/${simId}`);
      const data = await response.json();

      if (data.status === 'completed') {
        setSimulationResults(data.results);
        setSimulationStatus('Simulation completed!');
        setIsRunning(false);
      } else if (data.status === 'error') {
        setSimulationStatus(`Error: ${data.error}`);
        setIsRunning(false);
      } else {
        const message = data.message || `Running... ${data.progress || 0}%`;
        setSimulationStatus(message);
        // Continue polling
        setTimeout(() => pollSimulationStatus(simId), 2000);
      }
    } catch (error) {
      console.error('Polling error:', error);
      setSimulationStatus(`Polling error: ${error.message}`);
      setIsRunning(false);
    }
  };

  return (
    <div className="dashboard">
      {/* Header Title */}
      <header className="dashboard-header">
        <h1 className="dashboard-title">
          AlgoClash: <span className="subtitle">Where Code Collides</span>
        </h1>
        <nav className="dashboard-nav">
          <a
            href="#home"
            className={active === 'home' ? 'active' : ''}
            onClick={e => {
              handleNav(e, 'home');
              setActive('home');
            }}
          >
            Home
          </a>
          <a
            href="/models"
            className={active === 'models' ? 'active' : ''}
            onClick={e => {
              handleNav(e, 'models');
              setActive('models');
            }}
          >
            Models
          </a>
          <a
            href="/about"
            className={active === 'about' ? 'active' : ''}
            onClick={e => {
              handleNav(e, 'about');
              setActive('about');
            }}
          >
            About
          </a>
          <a
            href="/contact"
            className={active === 'contact' ? 'active' : ''}
            onClick={e => {
              handleNav(e, 'contact');
              setActive('contact');
            }}
          >
            Contact
          </a>
        </nav>
      </header>

      {/* Top controls below navbar: Stock selector */}
      <div className="top-controls">
        <label htmlFor="stock-select">Stock data:</label>
        {stocks.length > 0 ? (
          <select
            id="stock-select"
            className="stock-select"
            value={selectedStock}
            onChange={(e) => setSelectedStock(e.target.value)}
          >
            {stocks.map((item) => {
              const ticker = item.ticker || String(item).replace(/_data\.csv$/i, '').toUpperCase();
              const filename = item.filename || String(item);
              return (
                <option key={filename} value={filename}>{ticker}</option>
              );
            })}
          </select>
        ) : (
          <span className="stock-empty">No data files found</span>
        )}
      </div>

      {/* Main Content Area */}
      <div className="dashboard-content">
        {[1, 2, 3].map(i => {
          const leftKey = `left-${i}`;
          const rightKey = `right-${i}`;
          const values = Object.values(selectedAgents);
          const disabledLeft = new Set(values.filter(a => a && a !== selectedAgents[leftKey]));
          const disabledRight = new Set(values.filter(a => a && a !== selectedAgents[rightKey]));
          return (
            <React.Fragment key={i}>
              <div className={`side-element left-element left-element-${i}`}>
                <div className="side-circle left-circle">
                  <CustomDropdown 
                    agents={agents} 
                    selected={selectedAgents[leftKey]} 
                    onSelect={(agent) => handleAgentSelect(leftKey, agent)}
                    disabledAgents={disabledLeft}
                  />
                </div>
              </div>
              <div className={`side-element right-element right-element-${i}`}>
                <div className="side-circle right-circle">
                  <CustomDropdown 
                    agents={agents} 
                    selected={selectedAgents[rightKey]} 
                    onSelect={(agent) => handleAgentSelect(rightKey, agent)}
                    disabledAgents={disabledRight}
                  />
                </div>
              </div>
            </React.Fragment>
          );
        })}
      
        {/* Center Blue Box */}
        <div className="center-box"></div>

        {/* Start Button */}
        <button 
          className={`start-button ${isRunning ? 'running' : ''}`}
          onClick={handleStartSimulation}
          disabled={isRunning}
        >
          {isRunning ? 'RUNNING...' : 'START'}
        </button>

        {/* Simulation Status */}
        {simulationStatus && (
          <div className="simulation-status">
            {simulationStatus}
          </div>
        )}

        {/* Results Display */}
        {simulationResults && (
          <div className="results-container">
            <h2>🏁 Battle Results</h2>
            <div className="winner-display">
              {simulationResults.winner && (
                <div className="winner">
                  🏆 Winner: {simulationResults.winner.name} 
                  <span className="roi">ROI: {simulationResults.winner.roi?.toFixed(2)}%</span>
                </div>
              )}
            </div>
            <div className="leaderboard">
              <h3>📊 Leaderboard</h3>
              {simulationResults.leaderboard?.map((agent, index) => (
                <div key={agent.name} className={`leaderboard-item rank-${index + 1}`}>
                  <span className="rank">
                    {index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : `${index + 1}.`}
                  </span>
                  <span className="name">{agent.name}</span>
                  <span className="roi">{agent.roi?.toFixed(2)}%</span>
                  <span className="value">${agent.current_value?.toFixed(2)}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
