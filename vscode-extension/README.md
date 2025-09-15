# Mycelium-EI-Lang VS Code Extension

Official VS Code extension for Mycelium-EI-Lang - the revolutionary bio-inspired programming language with quantum computing integration.

## Features

### Syntax Highlighting
- Full syntax highlighting for `.myc` files
- Bio-inspired keywords highlighted in green
- Quantum constructs highlighted in blue
- Function names and built-ins with distinct colors

### IntelliSense
- Auto-completion for all built-in functions
- Parameter hints and documentation
- Keyword suggestions
- Smart bracket matching

### Code Snippets
- `env` - Create environment block
- `func` - Create function
- `main` - Create main function
- `genetic` - Genetic optimization snippet
- `swarm` - Particle swarm optimization
- `neural` - Create neural network
- `cultivation` - Cultivation system setup
- `quantum` - Quantum entanglement

### Commands
- **Run Current File** (`Ctrl+Shift+R` / `Cmd+Shift+R`)
  - Execute the current Mycelium file
  - Output shown in dedicated panel

- **Run Bio-Optimization**
  - Choose from genetic, swarm, or ant colony algorithms
  - Interactive optimization interface

### Hover Documentation
Hover over any built-in function to see:
- Function description
- Parameter details
- Usage examples

### Error Detection
- Syntax error highlighting
- Unmatched bracket detection
- Real-time diagnostics

## Requirements

- VS Code 1.74.0 or higher
- Python 3.8+ with mycelium-ei-lang package installed

## Installation

### From VS Code Marketplace (Recommended)
1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X)
3. Search for "Mycelium-EI-Lang"
4. Click Install

### From VSIX Package
1. Download the `.vsix` file
2. In VS Code, go to Extensions
3. Click "..." menu → "Install from VSIX"
4. Select the downloaded file

## Getting Started

1. Install the extension
2. Install the Mycelium-EI-Lang Python package:
   ```bash
   pip install mycelium-ei-lang
   ```
3. Create a new file with `.myc` extension
4. Start coding with full IntelliSense support!

## Example Code

```mycelium
environment {
    temperature: 24.0,
    humidity: 85.0,
    nutrients: 100.0
}

function optimize_growth() {
    let result = genetic_optimize("fitness_func", 6, 50, 100)
    return result
}

function main() {
    print("Starting bio-optimization...")
    let optimal = optimize_growth()
    print("Optimization complete!")
}
```

## Configuration

Access settings through VS Code Settings → Extensions → Mycelium-EI-Lang:

- `mycelium.pythonPath`: Path to Python interpreter (default: `python`)
- `mycelium.enableOptimizations`: Enable performance optimizations (default: `true`)
- `mycelium.debugMode`: Enable debug output (default: `false`)

## Themes

The extension includes a custom "Mycelium Dark" theme optimized for bio-inspired code with:
- Green tones for biological constructs
- Blue accents for quantum features
- High contrast for readability

## Support

- GitHub Issues: [Report bugs](https://github.com/MichaelCrowe11/mycelium-ei-lang/issues)
- Documentation: [Full docs](https://mycelium-ei-lang.readthedocs.io)
- Examples: [Sample code](https://github.com/MichaelCrowe11/mycelium-ei-lang/tree/main/examples)

## License

MIT License - Free for personal and commercial use

## Author

Michael Benjamin Crowe

---

**Enjoy coding with Mycelium-EI-Lang!** 🧬