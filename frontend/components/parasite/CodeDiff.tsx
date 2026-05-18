'use client';

import React, { useState } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

interface CodeDiffProps {
  beforeCode: string;
  afterCode: string;
  filename: string;
}

export const CodeDiff: React.FC<CodeDiffProps> = ({ beforeCode, afterCode, filename }) => {
  const [expanded, setExpanded] = useState(false);

  // Extract language from extension
  const ext = filename.split('.').pop() || 'text';
  const language = ext === 'py' ? 'python' : ext === 'js' ? 'javascript' : ext === 'ts' ? 'typescript' : 'text';

  // In a real app we'd do a complex line-by-line diff, 
  // here we just show them side by side or stacked based on space
  return (
    <div className="border border-border-dim rounded-sm overflow-hidden text-xs">
      <div className="flex border-b border-border-dim bg-elevated/50">
        <div className="flex-1 p-2 border-r border-border-dim text-critical-red font-bold text-center bg-critical-red/10">VULNERABLE</div>
        <div className="flex-1 p-2 text-parasite-green font-bold text-center bg-parasite-green/10">PATCHED</div>
      </div>
      
      <div className="flex flex-col md:flex-row">
        {/* Left Side (Vulnerable) */}
        <div className="flex-1 overflow-x-auto border-b md:border-b-0 md:border-r border-border-dim bg-[#1a0505]">
          <SyntaxHighlighter 
            language={language} 
            style={vscDarkPlus}
            customStyle={{ background: 'transparent', margin: 0, padding: '16px' }}
            showLineNumbers
          >
            {beforeCode}
          </SyntaxHighlighter>
        </div>
        
        {/* Right Side (Fixed) */}
        <div className="flex-1 overflow-x-auto bg-[#051a0a]">
          <SyntaxHighlighter 
            language={language} 
            style={vscDarkPlus}
            customStyle={{ background: 'transparent', margin: 0, padding: '16px' }}
            showLineNumbers
          >
            {afterCode}
          </SyntaxHighlighter>
        </div>
      </div>
    </div>
  );
};
