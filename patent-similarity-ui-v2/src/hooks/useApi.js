import { useState, useEffect, useCallback } from 'react';
import api from '../api/client';

// Generic hook for data fetching
export function useFetch(fetchFn, dependencies = []) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    async function fetchData() {
      try {
        setLoading(true);
        setError(null);
        const result = await fetchFn();
        if (!cancelled) {
          setData(result);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err.message || 'Failed to fetch data');
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    fetchData();

    return () => {
      cancelled = true;
    };
  }, dependencies);

  return { data, loading, error, refetch: () => setData(null) };
}

// Hook for libraries
export function useLibraries(search) {
  return useFetch(() => api.libraries.list(search), [search]);
}

// Hook for library details
export function useLibrary(id) {
  return useFetch(() => api.libraries.get(id), [id]);
}

// Hook for patents
export function usePatents(libraryId, search) {
  return useFetch(() => api.patents.list(libraryId, search), [libraryId, search]);
}

// Hook for tasks
export function useTasks(params = {}) {
  const { status, library_id, search, skip, limit } = params;
  return useFetch(
    () => api.tasks.list({ status, library_id, search, skip, limit }),
    [status, library_id, search, skip, limit]
  );
}

// Hook for task details
export function useTask(id) {
  return useFetch(() => api.tasks.get(id), [id]);
}

// Hook for task results
export function useTaskResult(id) {
  return useFetch(() => api.tasks.getResult(id), [id]);
}

// Hook for API operations with loading state
export function useApiOperation() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const execute = useCallback(async (operation) => {
    try {
      setLoading(true);
      setError(null);
      const result = await operation();
      return result;
    } catch (err) {
      setError(err.message || 'Operation failed');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return { execute, loading, error, clearError: () => setError(null) };
}

export default useApi;
