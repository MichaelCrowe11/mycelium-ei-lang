use crate::ast::*;
use crate::error::{CompilerError, Result};
use crate::CompilerOptions;
use std::collections::HashMap;

pub struct SemanticAnalyzer {
    symbol_table: SymbolTable,
    options: CompilerOptions,
}

struct SymbolTable {
    scopes: Vec<HashMap<String, Symbol>>,
}

struct Symbol {
    name: String,
    ty: Type,
    mutable: bool,
}

impl SymbolTable {
    fn new() -> Self {
        Self {
            scopes: vec![HashMap::new()],
        }
    }
    
    fn push_scope(&mut self) {
        self.scopes.push(HashMap::new());
    }
    
    fn pop_scope(&mut self) {
        self.scopes.pop();
    }
    
    fn define(&mut self, name: String, ty: Type, mutable: bool) -> Result<()> {
        if let Some(scope) = self.scopes.last_mut() {
            if scope.contains_key(&name) {
                return Err(CompilerError::SemanticError(
                    format!("Variable '{}' already defined in this scope", name)
                ));
            }
            scope.insert(name.clone(), Symbol { name, ty, mutable });
            Ok(())
        } else {
            Err(CompilerError::SemanticError("No active scope".to_string()))
        }
    }
    
    fn lookup(&self, name: &str) -> Option<&Symbol> {
        for scope in self.scopes.iter().rev() {
            if let Some(symbol) = scope.get(name) {
                return Some(symbol);
            }
        }
        None
    }
}

impl SemanticAnalyzer {
    pub fn new(options: &CompilerOptions) -> Self {
        Self {
            symbol_table: SymbolTable::new(),
            options: options.clone(),
        }
    }
    
    pub fn analyze(&mut self, program: Program) -> Result<Program> {
        let mut analyzed_nodes = Vec::new();
        
        for node in program.nodes {
            analyzed_nodes.push(self.analyze_node(node)?);
        }
        
        Ok(Program { nodes: analyzed_nodes })
    }
    
    fn analyze_node(&mut self, node: AstNode) -> Result<AstNode> {
        match node {
            AstNode::Environment(env) => {
                self.analyze_environment(&env)?;
                Ok(AstNode::Environment(env))
            },
            AstNode::Function(func) => {
                let analyzed_func = self.analyze_function(func)?;
                Ok(AstNode::Function(analyzed_func))
            },
            AstNode::Statement(stmt) => {
                let analyzed_stmt = self.analyze_statement(stmt)?;
                Ok(AstNode::Statement(analyzed_stmt))
            },
            AstNode::Expression(expr) => {
                let (analyzed_expr, _) = self.analyze_expression(expr)?;
                Ok(AstNode::Expression(analyzed_expr))
            },
        }
    }
    
    fn analyze_environment(&mut self, env: &Environment) -> Result<()> {
        for param in &env.parameters {
            self.symbol_table.define(
                param.name.clone(),
                Type::Float,
                false,
            )?;
        }
        Ok(())
    }
    
    fn analyze_function(&mut self, func: Function) -> Result<Function> {
        self.symbol_table.push_scope();
        
        for param in &func.parameters {
            self.symbol_table.define(
                param.name.clone(),
                param.ty.clone(),
                false,
            )?;
        }
        
        let mut analyzed_body = Vec::new();
        for stmt in func.body {
            analyzed_body.push(self.analyze_statement(stmt)?);
        }
        
        self.symbol_table.pop_scope();
        
        Ok(Function {
            name: func.name,
            parameters: func.parameters,
            return_type: func.return_type,
            body: analyzed_body,
        })
    }
    
    fn analyze_statement(&mut self, stmt: Statement) -> Result<Statement> {
        match stmt {
            Statement::Let { name, ty, value } => {
                let (analyzed_value, value_type) = self.analyze_expression(value)?;
                
                let var_type = ty.clone().unwrap_or(value_type);
                self.symbol_table.define(name.clone(), var_type, true)?;
                
                Ok(Statement::Let {
                    name,
                    ty,
                    value: analyzed_value,
                })
            },
            Statement::Assignment { target, value } => {
                if self.symbol_table.lookup(&target).is_none() {
                    return Err(CompilerError::SemanticError(
                        format!("Undefined variable '{}'", target)
                    ));
                }
                
                let (analyzed_value, _) = self.analyze_expression(value)?;
                Ok(Statement::Assignment {
                    target,
                    value: analyzed_value,
                })
            },
            Statement::If { condition, then_branch, else_branch } => {
                let (analyzed_condition, _) = self.analyze_expression(condition)?;
                
                self.symbol_table.push_scope();
                let mut analyzed_then = Vec::new();
                for stmt in then_branch {
                    analyzed_then.push(self.analyze_statement(stmt)?);
                }
                self.symbol_table.pop_scope();
                
                let analyzed_else = if let Some(else_branch) = else_branch {
                    self.symbol_table.push_scope();
                    let mut analyzed = Vec::new();
                    for stmt in else_branch {
                        analyzed.push(self.analyze_statement(stmt)?);
                    }
                    self.symbol_table.pop_scope();
                    Some(analyzed)
                } else {
                    None
                };
                
                Ok(Statement::If {
                    condition: analyzed_condition,
                    then_branch: analyzed_then,
                    else_branch: analyzed_else,
                })
            },
            Statement::While { condition, body } => {
                let (analyzed_condition, _) = self.analyze_expression(condition)?;
                
                self.symbol_table.push_scope();
                let mut analyzed_body = Vec::new();
                for stmt in body {
                    analyzed_body.push(self.analyze_statement(stmt)?);
                }
                self.symbol_table.pop_scope();
                
                Ok(Statement::While {
                    condition: analyzed_condition,
                    body: analyzed_body,
                })
            },
            Statement::For { variable, iterable, body } => {
                let (analyzed_iterable, _) = self.analyze_expression(iterable)?;
                
                self.symbol_table.push_scope();
                self.symbol_table.define(variable.clone(), Type::Integer, false)?;
                
                let mut analyzed_body = Vec::new();
                for stmt in body {
                    analyzed_body.push(self.analyze_statement(stmt)?);
                }
                self.symbol_table.pop_scope();
                
                Ok(Statement::For {
                    variable,
                    iterable: analyzed_iterable,
                    body: analyzed_body,
                })
            },
            Statement::Return(expr) => {
                let analyzed_expr = if let Some(expr) = expr {
                    let (analyzed, _) = self.analyze_expression(expr)?;
                    Some(analyzed)
                } else {
                    None
                };
                Ok(Statement::Return(analyzed_expr))
            },
            Statement::Expression(expr) => {
                let (analyzed_expr, _) = self.analyze_expression(expr)?;
                Ok(Statement::Expression(analyzed_expr))
            },
        }
    }
    
    fn analyze_expression(&mut self, expr: Expression) -> Result<(Expression, Type)> {
        match expr {
            Expression::Integer(n) => Ok((Expression::Integer(n), Type::Integer)),
            Expression::Float(f) => Ok((Expression::Float(f), Type::Float)),
            Expression::String(s) => Ok((Expression::String(s.clone()), Type::String)),
            Expression::Boolean(b) => Ok((Expression::Boolean(b), Type::Boolean)),
            Expression::Identifier(name) => {
                if let Some(symbol) = self.symbol_table.lookup(&name) {
                    Ok((Expression::Identifier(name), symbol.ty.clone()))
                } else {
                    Err(CompilerError::SemanticError(
                        format!("Undefined variable '{}'", name)
                    ))
                }
            },
            Expression::Binary { left, op, right } => {
                let (analyzed_left, left_type) = self.analyze_expression(*left)?;
                let (analyzed_right, right_type) = self.analyze_expression(*right)?;
                
                let result_type = self.infer_binary_type(&op, &left_type, &right_type)?;
                
                Ok((
                    Expression::Binary {
                        left: Box::new(analyzed_left),
                        op,
                        right: Box::new(analyzed_right),
                    },
                    result_type,
                ))
            },
            Expression::Unary { op, expr } => {
                let (analyzed_expr, expr_type) = self.analyze_expression(*expr)?;
                let result_type = self.infer_unary_type(&op, &expr_type)?;
                
                Ok((
                    Expression::Unary {
                        op,
                        expr: Box::new(analyzed_expr),
                    },
                    result_type,
                ))
            },
            Expression::Call { function, arguments } => {
                let mut analyzed_args = Vec::new();
                for arg in arguments {
                    let (analyzed_arg, _) = self.analyze_expression(arg)?;
                    analyzed_args.push(analyzed_arg);
                }
                
                Ok((
                    Expression::Call {
                        function,
                        arguments: analyzed_args,
                    },
                    Type::Integer,
                ))
            },
            Expression::Index { object, index } => {
                let (analyzed_object, object_type) = self.analyze_expression(*object)?;
                let (analyzed_index, _) = self.analyze_expression(*index)?;
                
                let element_type = if let Type::Array(elem_type) = object_type {
                    *elem_type
                } else {
                    Type::Integer
                };
                
                Ok((
                    Expression::Index {
                        object: Box::new(analyzed_object),
                        index: Box::new(analyzed_index),
                    },
                    element_type,
                ))
            },
            Expression::Field { object, field } => {
                let (analyzed_object, _) = self.analyze_expression(*object)?;
                
                Ok((
                    Expression::Field {
                        object: Box::new(analyzed_object),
                        field,
                    },
                    Type::Integer,
                ))
            },
            Expression::Array(items) => {
                let mut analyzed_items = Vec::new();
                let mut item_type = Type::Integer;
                
                for (i, item) in items.into_iter().enumerate() {
                    let (analyzed_item, ty) = self.analyze_expression(item)?;
                    if i == 0 {
                        item_type = ty;
                    }
                    analyzed_items.push(analyzed_item);
                }
                
                Ok((
                    Expression::Array(analyzed_items),
                    Type::Array(Box::new(item_type)),
                ))
            },
        }
    }
    
    fn infer_binary_type(&self, op: &BinaryOp, left: &Type, right: &Type) -> Result<Type> {
        match op {
            BinaryOp::Add | BinaryOp::Subtract | BinaryOp::Multiply | BinaryOp::Divide | BinaryOp::Modulo => {
                if matches!(left, Type::Float) || matches!(right, Type::Float) {
                    Ok(Type::Float)
                } else {
                    Ok(Type::Integer)
                }
            },
            BinaryOp::Equal | BinaryOp::NotEqual | BinaryOp::Less | BinaryOp::Greater 
            | BinaryOp::LessEqual | BinaryOp::GreaterEqual | BinaryOp::And | BinaryOp::Or => {
                Ok(Type::Boolean)
            },
        }
    }
    
    fn infer_unary_type(&self, op: &UnaryOp, expr_type: &Type) -> Result<Type> {
        match op {
            UnaryOp::Not => Ok(Type::Boolean),
            UnaryOp::Negate => Ok(expr_type.clone()),
        }
    }
}

pub fn analyze(program: Program, options: &CompilerOptions) -> Result<Program> {
    let mut analyzer = SemanticAnalyzer::new(options);
    analyzer.analyze(program)
}