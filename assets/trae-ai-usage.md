# TRAE AI Usage Documentation

Per hackathon rules, this document details how **TRAE AI** was used in conjunction with Claude Code to accelerate the development of PARASITE EVOLVED.

## How TRAE AI Accelerated Development

TRAE AI served as a critical companion during the 24-hour hackathon, specifically augmenting areas where immediate context-aware code generation and debugging were necessary.

### 1. Debugging Next.js 15 Hook Constraints
During the implementation of the `SessionLayout` component, a critical React Hook rule violation occurred. The Next.js 15 App Router requires parameters to be awaited in server components, but client components must handle them differently. 
- **Action:** Passed the layout structure to TRAE AI.
- **Result:** TRAE AI immediately identified the `React.use(params)` misuse in a client context and provided the exact refactor using `useParams()` from `next/navigation`, resolving the rendering block in seconds.

### 2. Generating the Utility Functions for Three.js
The 3D Visualization engine required complex math for the force-directed graph (calculating repulsion and spring forces between AST nodes).
- **Action:** Asked TRAE AI to generate a highly optimized layout simulation loop using a `Float32Array`.
- **Result:** TRAE AI provided a `useFrame` implementation that bypassed React state and directly mutated the mesh instances, maintaining 60fps even with 500+ edges.

### 3. Code Review of the Infiltration Engine
The `graph_builder.py` logic was intricate and deeply nested. 
- **Action:** Used TRAE AI to review the module for performance bottlenecks.
- **Result:** TRAE AI suggested caching repeated AST tree walks and utilizing `NetworkX`'s built-in bipartite capabilities to speed up the taint analysis.

## Screenshots & Logs
*(Placeholders for actual screenshots of TRAE AI in action)*
- `assets/trae-debugging.png` (Screenshot of the hook resolution)
- `assets/trae-generation.png` (Screenshot of the Three.js physics calculation)

---
*Built with TRAE AI + Claude Code*
