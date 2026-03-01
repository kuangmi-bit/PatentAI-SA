// API client for PatentAI backend
const API_BASE = 'http://localhost:8000';

async function fetchApi(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });
  
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }
  
  if (response.status === 204) return null;
  return response.json();
}

export const api = {
  // Health
  health: () => fetchApi('/health'),
  
  // Libraries
  libraries: {
    list: () => fetchApi('/libraries'),
    get: (id) => fetchApi(`/libraries/${id}`),
    create: (data) => fetchApi('/libraries', { method: 'POST', body: JSON.stringify(data) }),
    delete: (id) => fetchApi(`/libraries/${id}`, { method: 'DELETE' }),
  },
  
  // Patents
  patents: {
    list: (libraryId) => fetchApi(`/patents${libraryId ? `?library_id=${libraryId}` : ''}`),
    get: (id) => fetchApi(`/patents/${id}`),
    delete: (id) => fetchApi(`/patents/${id}`, { method: 'DELETE' }),
  },
  
  // Tasks
  tasks: {
    list: () => fetchApi('/tasks'),
    get: (id) => fetchApi(`/tasks/${id}`),
    create: (data) => fetchApi('/tasks', { method: 'POST', body: JSON.stringify(data) }),
    submit: (id, patentId) => fetchApi(`/tasks/${id}/submit${patentId ? `?target_patent_id=${patentId}` : ''}`, { method: 'POST' }),
    cancel: (id) => fetchApi(`/tasks/${id}/cancel`, { method: 'POST' }),
    delete: (id) => fetchApi(`/tasks/${id}`, { method: 'DELETE' }),
    result: (id) => fetchApi(`/tasks/${id}/result`),
  },
  
  // Upload
  upload: {
    file: async (file) => {
      const formData = new FormData();
      formData.append('file', file);
      
      console.log('Uploading to:', `${API_BASE}/upload/patent`);
      console.log('File:', file.name, file.type, file.size);
      
      const response = await fetch(`${API_BASE}/upload/patent`, {
        method: 'POST',
        body: formData,
        // Don't set Content-Type header - browser will set it with boundary
      });
      
      console.log('Response status:', response.status);
      console.log('Response headers:', Object.fromEntries(response.headers.entries()));
      
      if (!response.ok) {
        const errorText = await response.text().catch(() => response.statusText);
        console.error('Upload error:', errorText);
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }
      return response.json();
    },
    parse: (fileId) => fetchApi(`/upload/parse/${fileId}`, { method: 'POST' }),
    save: (data) => fetchApi('/upload/save', { method: 'POST', body: JSON.stringify(data) }),
  },
  
  // Batch
  batch: {
    import: (libraryId, patents) => fetchApi(`/batch/import/json/${libraryId}`, {
      method: 'POST',
      body: JSON.stringify({ patents, generate_embeddings: true }),
    }),
  },
};

export default api;
