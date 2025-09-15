use std::fmt;
use thiserror::Error;

#[derive(Debug, Error)]
pub enum CompilerError {
    #[error("Lexical error: {0}")]
    LexicalError(String),
    
    #[error("Parse error: {0}")]
    ParseError(String),
    
    #[error("Semantic error: {0}")]
    SemanticError(String),
    
    #[error("Code generation error: {0}")]
    CodeGenError(String),
    
    #[error("Optimization error: {0}")]
    OptimizationError(String),
    
    #[error("IO error: {0}")]
    IoError(#[from] std::io::Error),
    
    #[error("Unknown error: {0}")]
    Unknown(String),
}

pub type Result<T> = std::result::Result<T, CompilerError>;