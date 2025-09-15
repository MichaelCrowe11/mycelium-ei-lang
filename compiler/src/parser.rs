use crate::ast::*;
use crate::error::{CompilerError, Result};
use crate::lexer::Token;

pub struct Parser {
    tokens: Vec<Token>,
    current: usize,
}

impl Parser {
    pub fn new(tokens: Vec<Token>) -> Self {
        Self { tokens, current: 0 }
    }
    
    fn is_at_end(&self) -> bool {
        self.current >= self.tokens.len()
    }
    
    fn peek(&self) -> Option<&Token> {
        self.tokens.get(self.current)
    }
    
    fn advance(&mut self) -> Option<Token> {
        if !self.is_at_end() {
            let token = self.tokens[self.current].clone();
            self.current += 1;
            Some(token)
        } else {
            None
        }
    }
    
    fn check(&self, token_type: &Token) -> bool {
        if let Some(token) = self.peek() {
            std::mem::discriminant(token) == std::mem::discriminant(token_type)
        } else {
            false
        }
    }
    
    fn consume(&mut self, expected: Token, message: &str) -> Result<Token> {
        if self.check(&expected) {
            Ok(self.advance().unwrap())
        } else {
            Err(CompilerError::ParseError(message.to_string()))
        }
    }
    
    pub fn parse_program(&mut self) -> Result<Program> {
        let mut nodes = Vec::new();
        
        while !self.is_at_end() {
            nodes.push(self.parse_top_level()?);
        }
        
        Ok(Program { nodes })
    }
    
    fn parse_top_level(&mut self) -> Result<AstNode> {
        match self.peek() {
            Some(Token::Environment) => {
                self.advance();
                Ok(AstNode::Environment(self.parse_environment()?))
            },
            Some(Token::Function) => {
                self.advance();
                Ok(AstNode::Function(self.parse_function()?))
            },
            _ => {
                Ok(AstNode::Statement(self.parse_statement()?))
            }
        }
    }
    
    fn parse_environment(&mut self) -> Result<Environment> {
        self.consume(Token::LeftBrace, "Expected '{' after 'environment'")?;
        let mut parameters = Vec::new();
        
        while !self.check(&Token::RightBrace) {
            if let Some(Token::Identifier(name)) = self.advance() {
                self.consume(Token::Colon, "Expected ':' after parameter name")?;
                if let Some(Token::Float(value)) = self.advance() {
                    parameters.push(EnvironmentParam { name, value });
                    if !self.check(&Token::RightBrace) {
                        self.consume(Token::Comma, "Expected ',' or '}' after parameter")?;
                    }
                } else {
                    return Err(CompilerError::ParseError("Expected float value".to_string()));
                }
            } else {
                return Err(CompilerError::ParseError("Expected parameter name".to_string()));
            }
        }
        
        self.consume(Token::RightBrace, "Expected '}' to close environment")?;
        Ok(Environment { parameters })
    }
    
    fn parse_function(&mut self) -> Result<Function> {
        let name = if let Some(Token::Identifier(name)) = self.advance() {
            name
        } else {
            return Err(CompilerError::ParseError("Expected function name".to_string()));
        };
        
        self.consume(Token::LeftParen, "Expected '(' after function name")?;
        let parameters = self.parse_parameters()?;
        self.consume(Token::RightParen, "Expected ')' after parameters")?;
        
        let return_type = if self.check(&Token::Arrow) {
            self.advance();
            Some(self.parse_type()?)
        } else {
            None
        };
        
        self.consume(Token::LeftBrace, "Expected '{' to start function body")?;
        let mut body = Vec::new();
        
        while !self.check(&Token::RightBrace) {
            body.push(self.parse_statement()?);
        }
        
        self.consume(Token::RightBrace, "Expected '}' to close function body")?;
        
        Ok(Function {
            name,
            parameters,
            return_type,
            body,
        })
    }
    
    fn parse_parameters(&mut self) -> Result<Vec<Parameter>> {
        let mut parameters = Vec::new();
        
        if !self.check(&Token::RightParen) {
            loop {
                if let Some(Token::Identifier(name)) = self.advance() {
                    self.consume(Token::Colon, "Expected ':' after parameter name")?;
                    let ty = self.parse_type()?;
                    parameters.push(Parameter { name, ty });
                    
                    if !self.check(&Token::Comma) {
                        break;
                    }
                    self.advance();
                } else {
                    return Err(CompilerError::ParseError("Expected parameter name".to_string()));
                }
            }
        }
        
        Ok(parameters)
    }
    
    fn parse_type(&mut self) -> Result<Type> {
        match self.advance() {
            Some(Token::Identifier(name)) => {
                match name.as_str() {
                    "int" => Ok(Type::Integer),
                    "float" => Ok(Type::Float),
                    "string" => Ok(Type::String),
                    "bool" => Ok(Type::Boolean),
                    "mycelium" => Ok(Type::Mycelium),
                    "network" => Ok(Type::Network),
                    "signal" => Ok(Type::Signal),
                    _ => Ok(Type::Custom(name)),
                }
            },
            _ => Err(CompilerError::ParseError("Expected type name".to_string())),
        }
    }
    
    fn parse_statement(&mut self) -> Result<Statement> {
        match self.peek() {
            Some(Token::Let) => {
                self.advance();
                self.parse_let_statement()
            },
            Some(Token::If) => {
                self.advance();
                self.parse_if_statement()
            },
            Some(Token::While) => {
                self.advance();
                self.parse_while_statement()
            },
            Some(Token::Return) => {
                self.advance();
                self.parse_return_statement()
            },
            _ => {
                let expr = self.parse_expression()?;
                if self.check(&Token::Assign) {
                    self.advance();
                    if let Expression::Identifier(target) = expr {
                        let value = self.parse_expression()?;
                        Ok(Statement::Assignment { target, value })
                    } else {
                        Err(CompilerError::ParseError("Invalid assignment target".to_string()))
                    }
                } else {
                    Ok(Statement::Expression(expr))
                }
            }
        }
    }
    
    fn parse_let_statement(&mut self) -> Result<Statement> {
        let name = if let Some(Token::Identifier(name)) = self.advance() {
            name
        } else {
            return Err(CompilerError::ParseError("Expected variable name".to_string()));
        };
        
        let ty = if self.check(&Token::Colon) {
            self.advance();
            Some(self.parse_type()?)
        } else {
            None
        };
        
        self.consume(Token::Assign, "Expected '=' in let statement")?;
        let value = self.parse_expression()?;
        
        Ok(Statement::Let { name, ty, value })
    }
    
    fn parse_if_statement(&mut self) -> Result<Statement> {
        let condition = self.parse_expression()?;
        self.consume(Token::LeftBrace, "Expected '{' after if condition")?;
        
        let mut then_branch = Vec::new();
        while !self.check(&Token::RightBrace) {
            then_branch.push(self.parse_statement()?);
        }
        self.consume(Token::RightBrace, "Expected '}' to close if body")?;
        
        let else_branch = if self.check(&Token::Else) {
            self.advance();
            self.consume(Token::LeftBrace, "Expected '{' after else")?;
            let mut else_body = Vec::new();
            while !self.check(&Token::RightBrace) {
                else_body.push(self.parse_statement()?);
            }
            self.consume(Token::RightBrace, "Expected '}' to close else body")?;
            Some(else_body)
        } else {
            None
        };
        
        Ok(Statement::If {
            condition,
            then_branch,
            else_branch,
        })
    }
    
    fn parse_while_statement(&mut self) -> Result<Statement> {
        let condition = self.parse_expression()?;
        self.consume(Token::LeftBrace, "Expected '{' after while condition")?;
        
        let mut body = Vec::new();
        while !self.check(&Token::RightBrace) {
            body.push(self.parse_statement()?);
        }
        self.consume(Token::RightBrace, "Expected '}' to close while body")?;
        
        Ok(Statement::While { condition, body })
    }
    
    fn parse_return_statement(&mut self) -> Result<Statement> {
        let value = if !self.is_at_end() && !self.check(&Token::Semicolon) {
            Some(self.parse_expression()?)
        } else {
            None
        };
        
        Ok(Statement::Return(value))
    }
    
    fn parse_expression(&mut self) -> Result<Expression> {
        self.parse_or()
    }
    
    fn parse_or(&mut self) -> Result<Expression> {
        let mut expr = self.parse_and()?;
        
        while self.check(&Token::Or) {
            self.advance();
            let right = self.parse_and()?;
            expr = Expression::Binary {
                left: Box::new(expr),
                op: BinaryOp::Or,
                right: Box::new(right),
            };
        }
        
        Ok(expr)
    }
    
    fn parse_and(&mut self) -> Result<Expression> {
        let mut expr = self.parse_equality()?;
        
        while self.check(&Token::And) {
            self.advance();
            let right = self.parse_equality()?;
            expr = Expression::Binary {
                left: Box::new(expr),
                op: BinaryOp::And,
                right: Box::new(right),
            };
        }
        
        Ok(expr)
    }
    
    fn parse_equality(&mut self) -> Result<Expression> {
        let mut expr = self.parse_comparison()?;
        
        while let Some(token) = self.peek() {
            let op = match token {
                Token::Equal => BinaryOp::Equal,
                Token::NotEqual => BinaryOp::NotEqual,
                _ => break,
            };
            self.advance();
            let right = self.parse_comparison()?;
            expr = Expression::Binary {
                left: Box::new(expr),
                op,
                right: Box::new(right),
            };
        }
        
        Ok(expr)
    }
    
    fn parse_comparison(&mut self) -> Result<Expression> {
        let mut expr = self.parse_term()?;
        
        while let Some(token) = self.peek() {
            let op = match token {
                Token::Less => BinaryOp::Less,
                Token::Greater => BinaryOp::Greater,
                Token::LessEqual => BinaryOp::LessEqual,
                Token::GreaterEqual => BinaryOp::GreaterEqual,
                _ => break,
            };
            self.advance();
            let right = self.parse_term()?;
            expr = Expression::Binary {
                left: Box::new(expr),
                op,
                right: Box::new(right),
            };
        }
        
        Ok(expr)
    }
    
    fn parse_term(&mut self) -> Result<Expression> {
        let mut expr = self.parse_factor()?;
        
        while let Some(token) = self.peek() {
            let op = match token {
                Token::Plus => BinaryOp::Add,
                Token::Minus => BinaryOp::Subtract,
                _ => break,
            };
            self.advance();
            let right = self.parse_factor()?;
            expr = Expression::Binary {
                left: Box::new(expr),
                op,
                right: Box::new(right),
            };
        }
        
        Ok(expr)
    }
    
    fn parse_factor(&mut self) -> Result<Expression> {
        let mut expr = self.parse_unary()?;
        
        while let Some(token) = self.peek() {
            let op = match token {
                Token::Star => BinaryOp::Multiply,
                Token::Slash => BinaryOp::Divide,
                Token::Percent => BinaryOp::Modulo,
                _ => break,
            };
            self.advance();
            let right = self.parse_unary()?;
            expr = Expression::Binary {
                left: Box::new(expr),
                op,
                right: Box::new(right),
            };
        }
        
        Ok(expr)
    }
    
    fn parse_unary(&mut self) -> Result<Expression> {
        match self.peek() {
            Some(Token::Not) => {
                self.advance();
                let expr = self.parse_unary()?;
                Ok(Expression::Unary {
                    op: UnaryOp::Not,
                    expr: Box::new(expr),
                })
            },
            Some(Token::Minus) => {
                self.advance();
                let expr = self.parse_unary()?;
                Ok(Expression::Unary {
                    op: UnaryOp::Negate,
                    expr: Box::new(expr),
                })
            },
            _ => self.parse_postfix(),
        }
    }
    
    fn parse_postfix(&mut self) -> Result<Expression> {
        let mut expr = self.parse_primary()?;
        
        loop {
            match self.peek() {
                Some(Token::LeftParen) => {
                    self.advance();
                    let mut arguments = Vec::new();
                    
                    if !self.check(&Token::RightParen) {
                        loop {
                            arguments.push(self.parse_expression()?);
                            if !self.check(&Token::Comma) {
                                break;
                            }
                            self.advance();
                        }
                    }
                    
                    self.consume(Token::RightParen, "Expected ')' after arguments")?;
                    
                    if let Expression::Identifier(function) = expr {
                        expr = Expression::Call { function, arguments };
                    } else {
                        return Err(CompilerError::ParseError("Invalid function call".to_string()));
                    }
                },
                Some(Token::Dot) => {
                    self.advance();
                    if let Some(Token::Identifier(field)) = self.advance() {
                        expr = Expression::Field {
                            object: Box::new(expr),
                            field,
                        };
                    } else {
                        return Err(CompilerError::ParseError("Expected field name after '.'".to_string()));
                    }
                },
                Some(Token::LeftBracket) => {
                    self.advance();
                    let index = self.parse_expression()?;
                    self.consume(Token::RightBracket, "Expected ']' after index")?;
                    expr = Expression::Index {
                        object: Box::new(expr),
                        index: Box::new(index),
                    };
                },
                _ => break,
            }
        }
        
        Ok(expr)
    }
    
    fn parse_primary(&mut self) -> Result<Expression> {
        match self.advance() {
            Some(Token::Integer(n)) => Ok(Expression::Integer(n)),
            Some(Token::Float(f)) => Ok(Expression::Float(f)),
            Some(Token::String(s)) => Ok(Expression::String(s)),
            Some(Token::True) => Ok(Expression::Boolean(true)),
            Some(Token::False) => Ok(Expression::Boolean(false)),
            Some(Token::Identifier(name)) => Ok(Expression::Identifier(name)),
            Some(Token::LeftParen) => {
                let expr = self.parse_expression()?;
                self.consume(Token::RightParen, "Expected ')' after expression")?;
                Ok(expr)
            },
            Some(Token::LeftBracket) => {
                let mut items = Vec::new();
                
                if !self.check(&Token::RightBracket) {
                    loop {
                        items.push(self.parse_expression()?);
                        if !self.check(&Token::Comma) {
                            break;
                        }
                        self.advance();
                    }
                }
                
                self.consume(Token::RightBracket, "Expected ']' after array items")?;
                Ok(Expression::Array(items))
            },
            _ => Err(CompilerError::ParseError("Unexpected token in expression".to_string())),
        }
    }
}

pub fn parse(tokens: Vec<Token>) -> Result<Program> {
    let mut parser = Parser::new(tokens);
    parser.parse_program()
}