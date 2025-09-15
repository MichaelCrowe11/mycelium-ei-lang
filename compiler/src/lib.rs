/*!
# Mycelium-EI-Lang Compiler

The Mycelium-EI-Lang compiler is designed for ecological intelligence programming,
featuring distributed execution, environmental adaptation, and deep integration
with biological cultivation systems.

## Architecture

- **Lexer**: Tokenizes source code with mycelium-specific syntax
- **Parser**: Builds AST with ecological programming constructs
- **Semantic Analysis**: Type checking with environmental constraints
- **Code Generation**: Compiles to multiple targets (native, WASM, Python bridge)
- **Optimization**: Bio-inspired optimization passes

## Usage

```rust
use mycelium_ei_compiler::*;

let source = include_str!("../../examples/cultivation.myc");
let tokens = lexer::tokenize(source)?;
let ast = parser::parse(tokens)?;
let analyzed = semantic::analyze(ast)?;
let bytecode = codegen::compile(analyzed)?;
```
*/

pub mod lexer;
pub mod parser;
pub mod ast;
pub mod semantic;
pub mod codegen;
pub mod optimization;
pub mod error;

pub use error::{CompilerError, Result};

#[derive(Debug, Clone)]
pub struct CompilerOptions {
    pub target: CompilerTarget,
    pub optimization_level: OptimizationLevel,
    pub enable_mycelium_threading: bool,
    pub enable_environmental_adaptation: bool,
    pub python_bridge: bool,
    pub debug_info: bool,
}

#[derive(Debug, Clone, PartialEq)]
pub enum CompilerTarget {
    Native,
    WebAssembly,
    PythonExtension,
    EdgeDevice,
}

#[derive(Debug, Clone, PartialEq)]
pub enum OptimizationLevel {
    None,
    Basic,
    Ecological,    // Bio-inspired optimizations
    Adaptive,      // Runtime adaptation
}

impl Default for CompilerOptions {
    fn default() -> Self {
        Self {
            target: CompilerTarget::Native,
            optimization_level: OptimizationLevel::Ecological,
            enable_mycelium_threading: true,
            enable_environmental_adaptation: true,
            python_bridge: false,
            debug_info: true,
        }
    }
}

/// Main compiler interface
pub struct Compiler {
    options: CompilerOptions,
}

impl Compiler {
    pub fn new(options: CompilerOptions) -> Self {
        Self { options }
    }

    pub fn compile(&self, source: &str) -> Result<Vec<u8>> {
        tracing::info!("Starting Mycelium-EI-Lang compilation");
        
        // Lexical analysis
        let tokens = lexer::tokenize(source)?;
        tracing::debug!("Tokenized {} tokens", tokens.len());

        // Parsing
        let ast = parser::parse(tokens)?;
        tracing::debug!("Generated AST with {} nodes", ast.node_count());

        // Semantic analysis
        let analyzed_ast = semantic::analyze(ast, &self.options)?;
        tracing::debug!("Semantic analysis completed");

        // Optimization
        let optimized_ast = optimization::optimize(analyzed_ast, &self.options)?;
        tracing::debug!("Optimization passes completed");

        // Code generation
        let bytecode = codegen::generate(optimized_ast, &self.options)?;
        tracing::info!("Compilation completed successfully");

        Ok(bytecode)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_basic_compilation() {
        let source = r#"
            environment {
                temperature: 22.5,
                humidity: 85.0
            }
            
            function main() {
                print("Hello, Mycelium!")
            }
        "#;

        let compiler = Compiler::new(CompilerOptions::default());
        let result = compiler.compile(source);
        assert!(result.is_ok());
    }
}