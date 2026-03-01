/**
 * API Client for PatentAI Backend
 * Base URL: http://localhost:8000
 */

const API_BASE_URL = 'http://localhost:8000';

// Helper function for API calls
async function fetchApi(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  };
  
  try {
    const response = await fetch(url, { ...defaultOptions, ...options });
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`);
    }
    
    // Handle empty responses (e.g., 204 No Content)
    if (response.status === 204) {
      return null;
    }
    
    return await response.json();
  } catch (error) {
    console.error(`API Error (${endpoint}):`, error);
    throw error;
  }
}

// ==================== Health Check ====================
export const healthApi = {
  check: () => fetchApi('/health'),
};

// ==================== Libraries ====================
export const libraryApi = {
  // List all libraries
  list: (search) => fetchApi(`/libraries${search ? `?search=${encodeURIComponent(search)}` : ''}`),
  
  // Get library by ID
  get: (id) => fetchApi(`/libraries/${id}`),
  
  // Create new library
  create: (data) => fetchApi('/libraries', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  
  // Delete library
  delete: (id) => fetchApi(`/libraries/${id}`, { method: 'DELETE' }),
};

// ==================== Patents ====================
export const patentApi = {
  // List patents (optionally filtered by library)
  list: (libraryId, search) => {
    const params = new URLSearchParams();
    if (libraryId) params.append('library_id', libraryId);
    if (search) params.append('search', search);
    const query = params.toString();
    return fetchApi(`/patents${query ? `?${query}` : ''}`);
  },
  
  // Get patent by ID
  get: (id) => fetchApi(`/patents/${id}`),
  
  // Delete patent
  delete: (id) => fetchApi(`/patents/${id}`, { method: 'DELETE' }),
};

// ==================== Upload ====================
export const uploadApi = {
  // Upload patent file
  uploadFile: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch(`${API_BASE_URL}/upload/patent`, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`);
    }
    
    return await response.json();
  },
  
  // Parse uploaded file
  parse: (fileId) => fetchApi(`/upload/parse/${fileId}`),
  
  // Save patent to library
  save: (data) => fetchApi('/upload/save', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  
  // Delete uploaded file
  deleteFile: (fileId) => fetchApi(`/upload/${fileId}`, { method: 'DELETE' }),
};

// ==================== Tasks ====================
export const taskApi = {
  // List tasks
  list: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.status) queryParams.append('status', params.status);
    if (params.library_id) queryParams.append('library_id', params.library_id);
    if (params.search) queryParams.append('search', params.search);
    if (params.skip) queryParams.append('skip', params.skip);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const query = queryParams.toString();
    return fetchApi(`/tasks${query ? `?${query}` : ''}`);
  },
  
  // Get task by ID
  get: (id) => fetchApi(`/tasks/${id}`),
  
  // Create new task
  create: (data) => fetchApi('/tasks', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  
  // Update task
  update: (id, data) => fetchApi(`/tasks/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  }),
  
  // Delete task
  delete: (id) => fetchApi(`/tasks/${id}`, { method: 'DELETE' }),
  
  // Submit task for analysis
  submit: (id, targetPatentId) => fetchApi(`/tasks/${id}/submit${targetPatentId ? `?target_patent_id=${targetPatentId}` : ''}`, {
    method: 'POST',
  }),
  
  // Cancel task
  cancel: (id) => fetchApi(`/tasks/${id}/cancel`, { method: 'POST' }),
  
  // Get task results
  getResult: (id) => fetchApi(`/tasks/${id}/result`),
};

// ==================== Batch Import ====================
export const batchApi = {
  // Import patents from JSON
  importJson: (libraryId, data) => fetchApi(`/batch/import/json/${libraryId}`, {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  
  // Import patents from file
  importFile: async (libraryId, file, generateEmbeddings = true) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch(`${API_BASE_URL}/batch/import/file/${libraryId}?generate_embeddings=${generateEmbeddings}`, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`);
    }
    
    return await response.json();
  },
  
  // Validate import data
  validate: (data) => fetchApi('/batch/validate', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  
  // Get import template
  getTemplate: () => fetchApi('/batch/template'),
};

export default {
  health: healthApi,
  libraries: libraryApi,
  patents: patentApi,
  upload: uploadApi,
  tasks: taskApi,
  batch: batchApi,
};
