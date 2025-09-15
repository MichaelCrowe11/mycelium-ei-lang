# @mycelium-ei/lang

Bio-inspired programming language with quantum computing integration for Node.js

## Installation

```bash
npm install -g @mycelium-ei/lang
```

## Usage

### CLI
```bash
mycelium run script.myc
mycelium compile script.myc
mycelium optimize --genetic script.myc
```

### Programmatic API
```javascript
const { MyceliumCompiler, BioOptimizer } = require('@mycelium-ei/lang');

// Compile Mycelium code
const compiler = new MyceliumCompiler();
const result = compiler.compile(`
  function fibonacci(n) {
    if (n <= 1) return n;
    return fibonacci(n-1) + fibonacci(n-2);
  }
`);

// Run bio-optimization
const optimizer = new BioOptimizer();
const optimized = optimizer.genetic({
  fitness: (x) => x * x,
  dimensions: 2,
  population: 50
});
```

## Features

- 🧬 **Genetic Algorithms** - Built-in evolutionary optimization
- 🐜 **Swarm Intelligence** - Particle swarm and ant colony optimization
- 🧠 **Neural Networks** - Bio-inspired neural architectures
- ⚛️ **Quantum Integration** - Quantum computing primitives
- 🌱 **Cultivation Systems** - Environmental growth modeling

## TypeScript Support

Full TypeScript definitions included:

```typescript
import { MyceliumCompiler, OptimizationResult } from '@mycelium-ei/lang';

const compiler = new MyceliumCompiler();
const result: OptimizationResult = await compiler.optimize({
  algorithm: 'genetic',
  parameters: { population: 100 }
});
```

## License

Proprietary - © 2024 Michael Benjamin Crowe. All rights reserved.

## Links

- [Documentation](https://mycelium-ei-lang.readthedocs.io)
- [GitHub](https://github.com/MichaelCrowe11/pulsar-lang)
- [PyPI Package](https://pypi.org/project/mycelium-ei-lang/)