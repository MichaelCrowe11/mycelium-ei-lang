use logos::Logos;
use crate::error::{CompilerError, Result};

#[derive(Logos, Debug, PartialEq, Clone)]
pub enum Token {
    #[token("environment")]
    Environment,
    
    #[token("function")]
    Function,
    
    #[token("mycelium")]
    Mycelium,
    
    #[token("network")]
    Network,
    
    #[token("signal")]
    Signal,
    
    #[token("adapt")]
    Adapt,
    
    #[token("if")]
    If,
    
    #[token("else")]
    Else,
    
    #[token("while")]
    While,
    
    #[token("for")]
    For,
    
    #[token("return")]
    Return,
    
    #[token("let")]
    Let,
    
    #[token("const")]
    Const,
    
    #[token("true")]
    True,
    
    #[token("false")]
    False,
    
    #[regex(r"[a-zA-Z_][a-zA-Z0-9_]*", |lex| lex.slice().to_string())]
    Identifier(String),
    
    #[regex(r"[0-9]+", |lex| lex.slice().parse::<i64>().unwrap())]
    Integer(i64),
    
    #[regex(r"[0-9]+\.[0-9]+", |lex| lex.slice().parse::<f64>().unwrap())]
    Float(f64),
    
    #[regex(r#""([^"\\]|\\.)*""#, |lex| lex.slice()[1..lex.slice().len()-1].to_string())]
    String(String),
    
    #[token("{")]
    LeftBrace,
    
    #[token("}")]
    RightBrace,
    
    #[token("(")]
    LeftParen,
    
    #[token(")")]
    RightParen,
    
    #[token("[")]
    LeftBracket,
    
    #[token("]")]
    RightBracket,
    
    #[token(",")]
    Comma,
    
    #[token(":")]
    Colon,
    
    #[token(";")]
    Semicolon,
    
    #[token(".")]
    Dot,
    
    #[token("->")]
    Arrow,
    
    #[token("=")]
    Assign,
    
    #[token("==")]
    Equal,
    
    #[token("!=")]
    NotEqual,
    
    #[token("<")]
    Less,
    
    #[token(">")]
    Greater,
    
    #[token("<=")]
    LessEqual,
    
    #[token(">=")]
    GreaterEqual,
    
    #[token("+")]
    Plus,
    
    #[token("-")]
    Minus,
    
    #[token("*")]
    Star,
    
    #[token("/")]
    Slash,
    
    #[token("%")]
    Percent,
    
    #[token("&&")]
    And,
    
    #[token("||")]
    Or,
    
    #[token("!")]
    Not,
    
    #[regex(r"[ \t\n\f]+", logos::skip)]
    #[regex(r"//[^\n]*", logos::skip)]
    #[regex(r"/\*[^*]*\*+(?:[^/*][^*]*\*+)*/", logos::skip)]
    #[error]
    Error,
}

pub fn tokenize(source: &str) -> Result<Vec<Token>> {
    let mut tokens = Vec::new();
    let mut lexer = Token::lexer(source);
    
    while let Some(token) = lexer.next() {
        match token {
            Ok(Token::Error) => {
                return Err(CompilerError::LexicalError(
                    format!("Unexpected character at position {}", lexer.span().start)
                ));
            },
            Ok(token) => tokens.push(token),
            Err(_) => {
                return Err(CompilerError::LexicalError(
                    format!("Failed to tokenize at position {}", lexer.span().start)
                ));
            }
        }
    }
    
    Ok(tokens)
}