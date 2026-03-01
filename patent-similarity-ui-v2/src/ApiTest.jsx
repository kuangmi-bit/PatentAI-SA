import React, { useState, useEffect } from 'react';
import api from './api/client';

const ApiTest = () => {
  const [health, setHealth] = useState(null);
  const [libraries, setLibraries] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [newLibName, setNewLibName] = useState('');

  // Test health endpoint
  const testHealth = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.health.check();
      setHealth(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Test libraries endpoint
  const testLibraries = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.libraries.list();
      setLibraries(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Test create library
  const createLibrary = async () => {
    if (!newLibName.trim()) return;
    try {
      setLoading(true);
      setError(null);
      await api.libraries.create({
        name: newLibName,
        description: 'Created from frontend test'
      });
      setNewLibName('');
      await testLibraries();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Test tasks endpoint
  const testTasks = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.tasks.list();
      setTasks(data.items || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    testHealth();
    testLibraries();
    testTasks();
  }, []);

  return (
    <div style={{ padding: '40px', maxWidth: '800px', margin: '0 auto' }}>
      <h1>API Integration Test</h1>
      
      {error && (
        <div style={{ 
          padding: '16px', 
          background: '#fee2e2', 
          color: '#dc2626',
          borderRadius: '8px',
          marginBottom: '20px'
        }}>
          Error: {error}
        </div>
      )}

      {/* Health Check */}
      <section style={{ marginBottom: '32px' }}>
        <h2>Health Check</h2>
        <button onClick={testHealth} disabled={loading}>
          Refresh Health
        </button>
        {health && (
          <pre style={{ 
            background: '#f1f5f9', 
            padding: '16px',
            borderRadius: '8px',
            marginTop: '12px'
          }}>
            {JSON.stringify(health, null, 2)}
          </pre>
        )}
      </section>

      {/* Libraries */}
      <section style={{ marginBottom: '32px' }}>
        <h2>Libraries ({libraries.length})</h2>
        <div style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
          <input
            type="text"
            value={newLibName}
            onChange={(e) => setNewLibName(e.target.value)}
            placeholder="New library name"
            style={{ padding: '8px 12px', flex: 1 }}
          />
          <button onClick={createLibrary} disabled={loading || !newLibName.trim()}>
            Create Library
          </button>
          <button onClick={testLibraries} disabled={loading}>
            Refresh
          </button>
        </div>
        <div style={{ display: 'grid', gap: '12px' }}>
          {libraries.map(lib => (
            <div key={lib.id} style={{ 
              padding: '16px', 
              background: '#f8fafc',
              borderRadius: '8px',
              border: '1px solid #e2e8f0'
            }}>
              <strong>{lib.name}</strong>
              <p style={{ margin: '4px 0', color: '#64748b' }}>
                {lib.description || 'No description'}
              </p>
              <small style={{ color: '#94a3b8' }}>
                Patents: {lib.patent_count} | ID: {lib.id}
              </small>
            </div>
          ))}
        </div>
      </section>

      {/* Tasks */}
      <section style={{ marginBottom: '32px' }}>
        <h2>Tasks ({tasks.length})</h2>
        <button onClick={testTasks} disabled={loading} style={{ marginBottom: '16px' }}>
          Refresh Tasks
        </button>
        <div style={{ display: 'grid', gap: '12px' }}>
          {tasks.map(task => (
            <div key={task.id} style={{ 
              padding: '16px', 
              background: '#f8fafc',
              borderRadius: '8px',
              border: '1px solid #e2e8f0'
            }}>
              <strong>{task.name}</strong>
              <div style={{ marginTop: '8px' }}>
                <span style={{
                  padding: '4px 8px',
                  borderRadius: '4px',
                  fontSize: '12px',
                  background: task.status === 'completed' ? '#d1fae5' : 
                             task.status === 'failed' ? '#fee2e2' : '#dbeafe',
                  color: task.status === 'completed' ? '#065f46' :
                        task.status === 'failed' ? '#991b1b' : '#1e40af'
                }}>
                  {task.status}
                </span>
                <span style={{ marginLeft: '12px', color: '#64748b' }}>
                  Progress: {task.progress}%
                </span>
              </div>
            </div>
          ))}
        </div>
      </section>

      {loading && <p>Loading...</p>}
    </div>
  );
};

export default ApiTest;
