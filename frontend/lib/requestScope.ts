let scopeController: AbortController | null = null;

function ensureScope(): AbortController {
  if (!scopeController) {
    scopeController = new AbortController();
  }
  return scopeController;
}

export function cancelInFlightRequests(): void {
  scopeController?.abort();
  scopeController = new AbortController();
}

export function getRequestSignal(): AbortSignal {
  return ensureScope().signal;
}

export function runScoped<T>(fn: (signal: AbortSignal) => Promise<T>): Promise<T> {
  const signal = getRequestSignal();
  return fn(signal);
}
