"use client";

import { Component, type ErrorInfo, type ReactNode } from "react";

type PersonalTabErrorBoundaryProps = {
  section: string;
  bottomPadding?: number;
  onRetry?: () => void;
  children: ReactNode;
};

type PersonalTabErrorBoundaryState = {
  hasError: boolean;
};

export class PersonalTabErrorBoundary extends Component<
  PersonalTabErrorBoundaryProps,
  PersonalTabErrorBoundaryState
> {
  state: PersonalTabErrorBoundaryState = { hasError: false };

  static getDerivedStateFromError(): PersonalTabErrorBoundaryState {
    return { hasError: true };
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    if (process.env.NODE_ENV === "development") {
      console.error(`[PersonalTab:${this.props.section}]`, error, info.componentStack);
    }
  }

  private handleRetry = (): void => {
    this.setState({ hasError: false });
    this.props.onRetry?.();
  };

  render(): ReactNode {
    if (!this.state.hasError) {
      return this.props.children;
    }

    return (
      <div
        className="flex min-h-0 flex-1 flex-col items-center justify-center gap-3 px-6"
        style={{ paddingBottom: this.props.bottomPadding ?? 0 }}
      >
        <p className="text-center text-sm opacity-70">Unable to load this section.</p>
        <button
          type="button"
          onClick={this.handleRetry}
          className="rounded-xl px-6 py-2 text-sm font-semibold underline"
        >
          Retry
        </button>
      </div>
    );
  }
}
