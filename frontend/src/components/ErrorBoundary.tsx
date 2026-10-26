import { Component, type ErrorInfo, type ReactNode } from "react";

/** A rendering error shows a message instead of a blank white page (and is logged to the console for debugging). */
export default class ErrorBoundary extends Component<{ children: ReactNode }, { error: Error | null }> {
  state = { error: null as Error | null };
  static getDerivedStateFromError(error: Error) { return { error }; }
  componentDidCatch(error: Error, info: ErrorInfo) { console.error("UI error:", error, info.componentStack); }
  render() {
    if (!this.state.error) return this.props.children;
    return (
      <div role="alert" className="mx-auto mt-16 max-w-md rounded-2xl border border-red-200 bg-red-50 p-6 text-center text-sm text-red-900">
        <h1 className="text-lg font-semibold">Something went wrong</h1>
        <p className="mt-2">The page hit an unexpected error. Reloading usually fixes it.</p>
        <button className="btn mt-4" onClick={() => location.reload()}>Reload page</button>
      </div>
    );
  }
}
