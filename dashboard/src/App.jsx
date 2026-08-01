import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { Activity, RefreshCw } from 'lucide-react';
import './index.css';

const API_BASE_URL = 'http://localhost:8000';
const REFRESH_INTERVAL = 30000; // 30 seconds

// Custom tooltip for the chart
const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div style={{
        background: 'rgba(17, 24, 39, 0.9)',
        border: '1px solid rgba(255,255,255,0.1)',
        padding: '10px',
        borderRadius: '8px',
        color: '#fff'
      }}>
        <p style={{ margin: '0 0 5px 0', fontSize: '12px', color: '#9ca3af' }}>
          {new Date(label).toLocaleString()}
        </p>
        <p style={{ margin: 0, fontWeight: 'bold' }}>
          ${payload[0].value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
        </p>
      </div>
    );
  }
  return null;
};

const CryptoCard = ({ coin, latestData, historyData, signal }) => {
  // Extract usd price
  const price = latestData.find(d => d.currency === 'usd')?.price || 0;
  
  // Prepare chart data (filtering for usd only)
  const chartData = historyData
    .filter(d => d.currency === 'usd')
    .map(d => ({
      time: d.timestamp,
      price: parseFloat(d.price)
    }));

  // Calculate 24h change roughly if we have enough data
  let changePct = 0;
  if (chartData.length > 0) {
    const oldestPrice = chartData[0].price;
    const newestPrice = chartData[chartData.length - 1].price;
    changePct = ((newestPrice - oldestPrice) / oldestPrice) * 100;
  }

  const isPositive = changePct >= 0;

  return (
    <div className="crypto-card">
      <div className="card-header">
        <div className="coin-info">
          <h2>{coin}</h2>
          <p className="price">${price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 6 })}</p>
          <p style={{ color: isPositive ? '#34d399' : '#f87171', margin: '0.25rem 0 0 0', fontSize: '0.875rem' }}>
            {isPositive ? '↑' : '↓'} {Math.abs(changePct).toFixed(2)}% (24h)
          </p>
        </div>
        <span className={`badge ${signal.toLowerCase()}`}>
          {signal}
        </span>
      </div>
      
      <div className="chart-container">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <XAxis 
              dataKey="time" 
              hide={true} 
            />
            <YAxis 
              domain={['auto', 'auto']} 
              hide={true} 
            />
            <Tooltip content={<CustomTooltip />} />
            <Line 
              type="monotone" 
              dataKey="price" 
              stroke={isPositive ? '#34d399' : '#f87171'} 
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

function App() {
  const [data, setData] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const fetchData = async () => {
    setIsRefreshing(true);
    try {
      // 1. Fetch latest prices
      const latestRes = await axios.get(`${API_BASE_URL}/prices/latest`);
      const latestPrices = latestRes.data;
      
      // Group by coin
      const coins = [...new Set(latestPrices.map(p => p.coin))];
      
      const combinedData = {};
      
      // 2. For each coin, fetch history and signal
      for (const coin of coins) {
        const [historyRes, signalRes] = await Promise.all([
          axios.get(`${API_BASE_URL}/prices/history?coin=${coin}&hours=24`),
          axios.get(`${API_BASE_URL}/signals/${coin}`)
        ]);
        
        combinedData[coin] = {
          latest: latestPrices.filter(p => p.coin === coin),
          history: historyRes.data,
          signal: signalRes.data.signal
        };
      }
      
      setData(combinedData);
      setLastUpdated(new Date());
      setError(null);
    } catch (err) {
      console.error("Failed to fetch data:", err);
      setError("Failed to connect to the API. Ensure the backend is running and seeded.");
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, REFRESH_INTERVAL);
    return () => clearInterval(interval);
  }, []);

  if (loading && Object.keys(data).length === 0) {
    return (
      <div className="loading">
        <Activity className="animate-pulse" size={48} style={{ marginRight: '1rem' }} />
        <span>Loading CryptoPulse...</span>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <div className="header">
        <h1>CryptoPulse</h1>
        <div className="last-updated">
          {error ? null : (
            <>
              <RefreshCw 
                size={16} 
                style={{ 
                  animation: isRefreshing ? 'spin 1s linear infinite' : 'none',
                  cursor: 'pointer' 
                }} 
                onClick={fetchData}
              />
              Last updated: {lastUpdated?.toLocaleTimeString()}
            </>
          )}
        </div>
      </div>
      
      {error && (
        <div className="error">
          <strong>Error:</strong> {error}
        </div>
      )}

      <div className="grid">
        {Object.entries(data).map(([coin, coinData]) => (
          <CryptoCard 
            key={coin}
            coin={coin}
            latestData={coinData.latest}
            historyData={coinData.history}
            signal={coinData.signal}
          />
        ))}
      </div>
    </div>
  );
}

export default App;
