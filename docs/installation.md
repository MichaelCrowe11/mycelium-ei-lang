# 📦 Installation Guide

## System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **RAM**: Minimum 4GB (8GB recommended for large optimizations)
- **Disk Space**: 100MB for basic installation

## Quick Installation

### From PyPI (Recommended)

```bash
pip install mycelium-ei-lang
```

### Verify Installation

```bash
python -m mycelium_ei --version
```

You should see:
```
0.1.1
```

## Advanced Installation Options

### With GPU Support

For CUDA-accelerated bio-algorithms:

```bash
pip install mycelium-ei-lang[gpu]
# This installs CuPy and other GPU dependencies
```

### Development Installation

For contributors and developers:

```bash
git clone https://github.com/MichaelCrowe11/pulsar-lang.git
cd pulsar-lang/mycelium-ei-lang
pip install -e .[dev]
```

### Docker Installation

```bash
# Pull the official image
docker pull ghcr.io/michaelcrowe11/mycelium-lang:latest

# Run interactive session
docker run -it ghcr.io/michaelcrowe11/mycelium-lang:latest

# For GPU support
docker pull ghcr.io/michaelcrowe11/mycelium-lang:cuda
docker run --gpus all -it ghcr.io/michaelcrowe11/mycelium-lang:cuda
```

## Platform-Specific Instructions

### Windows

```powershell
# Using pip
pip install mycelium-ei-lang

# Using Windows Package Manager
winget install Mycelium.EI.Lang
```

### macOS

```bash
# Using pip
pip install mycelium-ei-lang

# Using Homebrew
brew tap mycelium-ei/tap
brew install mycelium-ei-lang
```

### Linux

```bash
# Using pip
pip install mycelium-ei-lang

# Using Snap (Ubuntu/Debian)
sudo snap install mycelium-ei-lang

# Using Conda
conda install -c mycelium-ei mycelium-ei-lang
```

## VS Code Extension

Enhanced development experience with syntax highlighting and IntelliSense:

1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X)
3. Search for "Mycelium-EI-Lang"
4. Click Install

Or install from command line:
```bash
code --install-extension Mycelium-EI-Lang.mycelium-ei-lang
```

## Node.js Integration

For JavaScript/TypeScript projects:

```bash
npm install @michaelcrowe11/mycelium-ei-lang
```

```javascript
const { MyceliumCompiler } = require('@michaelcrowe11/mycelium-ei-lang');

const compiler = new MyceliumCompiler();
const result = await compiler.compile(`
    function fibonacci(n) {
        if (n <= 1) return n;
        return fibonacci(n-1) + fibonacci(n-2);
    }
`);
```

## WebAssembly Runtime

For browser execution:

```html
<script src="https://cdn.jsdelivr.net/npm/@michaelcrowe11/mycelium-ei-lang/wasm/mycelium-wasm.js"></script>
<script>
    const mycelium = new MyceliumWASM();
    
    const result = mycelium.geneticAlgorithm({
        populationSize: 50,
        generations: 100
    });
</script>
```

## Jupyter Integration

For interactive notebooks:

```bash
pip install mycelium-ei-lang[jupyter]
jupyter kernel install mycelium-ei-kernel
```

Then select "Mycelium-EI-Lang" kernel in Jupyter notebooks.

## Troubleshooting

### Common Issues

**ImportError: No module named 'mycelium_ei'**
```bash
pip install --upgrade mycelium-ei-lang
```

**Permission denied errors**
```bash
pip install --user mycelium-ei-lang
```

**GPU acceleration not working**
```bash
pip install cupy-cuda11x  # or cupy-cuda12x for CUDA 12
python -c "import cupy; print('GPU available:', cupy.cuda.is_available())"
```

### Environment Variables

```bash
# Set Python path
export PYTHONPATH=$PYTHONPATH:/path/to/mycelium-ei-lang

# Enable GPU acceleration
export MYCELIUM_ENABLE_GPU=1

# Set debug mode
export MYCELIUM_DEBUG=1
```

### Virtual Environment Setup

```bash
# Create virtual environment
python -m venv mycelium-env

# Activate (Linux/macOS)
source mycelium-env/bin/activate

# Activate (Windows)
mycelium-env\Scripts\activate

# Install Mycelium
pip install mycelium-ei-lang
```

## Update Instructions

```bash
# Update to latest version
pip install --upgrade mycelium-ei-lang

# Update VS Code extension
code --update-extensions

# Update Docker image
docker pull ghcr.io/michaelcrowe11/mycelium-lang:latest
```

## Uninstallation

```bash
# Remove Python package
pip uninstall mycelium-ei-lang

# Remove VS Code extension
code --uninstall-extension Mycelium-EI-Lang.mycelium-ei-lang

# Remove Docker images
docker rmi ghcr.io/michaelcrowe11/mycelium-lang:latest
```

## Next Steps

After installation:

1. 📚 Read the [Language Reference](language-reference.md)
2. 🚀 Try the [Examples](examples.md)
3. 🔧 Explore the [API Documentation](api.md)
4. 💻 Check out the [WebAssembly Runtime](webassembly.md)

## Getting Help

If you encounter issues:

1. Check the [Troubleshooting](#troubleshooting) section
2. Search [GitHub Issues](https://github.com/MichaelCrowe11/pulsar-lang/issues)
3. Ask on our [Discord Server](#) (coming soon)
4. Email: michael.benjamin.crowe@gmail.com

---

**Ready to start coding?** [View Examples →](examples.md)