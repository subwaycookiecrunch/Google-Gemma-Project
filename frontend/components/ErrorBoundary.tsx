'use client';

import React, { Component, ErrorInfo, ReactNode } from 'react';
import { ShieldAlert } from 'lucide-react';

interface Props {
  children?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error in 3D Canvas:', error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="flex flex-col items-center justify-center h-full w-full bg-void text-warning-amber p-8 text-center font-mono border border-warning-amber/30">
          <ShieldAlert className="w-16 h-16 mb-6 opacity-80" />
          <h2 className="text-2xl font-bold tracking-widest mb-4">🦠 VISUALIZATION UNAVAILABLE</h2>
          <p className="text-sm max-w-md mb-8">
            The 3D WebGL context has crashed or is unsupported in this environment.
            Running in terminal mode.
          </p>
          <div className="bg-black/50 p-4 border border-border-dim rounded-sm text-left text-xs font-mono text-text-dim max-w-lg w-full overflow-hidden">
            <div className="text-critical-red mb-2">ERROR_TRACE:</div>
            {this.state.error?.message || 'Unknown WebGL context error.'}
          </div>
          
          <button 
            onClick={() => this.setState({ hasError: false })}
            className="mt-8 px-6 py-2 border border-warning-amber/50 hover:bg-warning-amber/10 transition-colors"
          >
            REBOOT VISUALIZER
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
