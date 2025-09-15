use crate::ast::*;
use crate::error::{CompilerError, Result};
use crate::CompilerOptions;
use std::io::Write;

pub struct CodeGenerator {
    options: CompilerOptions,
    output: Vec<u8>,
}

impl CodeGenerator {
    pub fn new(options: &CompilerOptions) -> Self {
        Self {
            options: options.clone(),
            output: Vec::new(),
        }
    }
    
    pub fn generate(&mut self, program: Program) -> Result<Vec<u8>> {
        self.emit_header()?;
        
        for node in program.nodes {
            self.generate_node(node)?;
        }
        
        self.emit_footer()?;
        
        Ok(self.output.clone())
    }
    
    fn emit_header(&mut self) -> Result<()> {
        let header = b"MYCELIUM_BYTECODE_V1\x00";
        self.output.extend_from_slice(header);
        Ok(())
    }
    
    fn emit_footer(&mut self) -> Result<()> {
        let footer = b"\x00END";
        self.output.extend_from_slice(footer);
        Ok(())
    }
    
    fn generate_node(&mut self, node: AstNode) -> Result<()> {
        match node {
            AstNode::Environment(env) => self.generate_environment(env),
            AstNode::Function(func) => self.generate_function(func),
            AstNode::Statement(stmt) => self.generate_statement(stmt),
            AstNode::Expression(expr) => self.generate_expression(expr),
        }
    }
    
    fn generate_environment(&mut self, env: Environment) -> Result<()> {
        self.emit_opcode(OpCode::EnvStart)?;
        
        for param in env.parameters {
            self.emit_opcode(OpCode::EnvParam)?;
            self.emit_string(&param.name)?;
            self.emit_f64(param.value)?;
        }
        
        self.emit_opcode(OpCode::EnvEnd)?;
        Ok(())
    }
    
    fn generate_function(&mut self, func: Function) -> Result<()> {
        self.emit_opcode(OpCode::FuncStart)?;
        self.emit_string(&func.name)?;
        self.emit_u32(func.parameters.len() as u32)?;
        
        for param in func.parameters {
            self.emit_string(&param.name)?;
        }
        
        for stmt in func.body {
            self.generate_statement(stmt)?;
        }
        
        self.emit_opcode(OpCode::FuncEnd)?;
        Ok(())
    }
    
    fn generate_statement(&mut self, stmt: Statement) -> Result<()> {
        match stmt {
            Statement::Let { name, value, .. } => {
                self.generate_expression(value)?;
                self.emit_opcode(OpCode::Store)?;
                self.emit_string(&name)?;
            },
            Statement::Assignment { target, value } => {
                self.generate_expression(value)?;
                self.emit_opcode(OpCode::Store)?;
                self.emit_string(&target)?;
            },
            Statement::If { condition, then_branch, else_branch } => {
                self.generate_expression(condition)?;
                self.emit_opcode(OpCode::JumpIfFalse)?;
                let jump_addr = self.output.len();
                self.emit_u32(0)?;
                
                for stmt in then_branch {
                    self.generate_statement(stmt)?;
                }
                
                if let Some(else_branch) = else_branch {
                    self.emit_opcode(OpCode::Jump)?;
                    let else_jump_addr = self.output.len();
                    self.emit_u32(0)?;
                    
                    let else_start = self.output.len();
                    self.patch_jump(jump_addr, else_start as u32)?;
                    
                    for stmt in else_branch {
                        self.generate_statement(stmt)?;
                    }
                    
                    let end = self.output.len();
                    self.patch_jump(else_jump_addr, end as u32)?;
                } else {
                    let end = self.output.len();
                    self.patch_jump(jump_addr, end as u32)?;
                }
            },
            Statement::While { condition, body } => {
                let loop_start = self.output.len();
                
                self.generate_expression(condition)?;
                self.emit_opcode(OpCode::JumpIfFalse)?;
                let exit_addr = self.output.len();
                self.emit_u32(0)?;
                
                for stmt in body {
                    self.generate_statement(stmt)?;
                }
                
                self.emit_opcode(OpCode::Jump)?;
                self.emit_u32(loop_start as u32)?;
                
                let loop_end = self.output.len();
                self.patch_jump(exit_addr, loop_end as u32)?;
            },
            Statement::For { variable, iterable, body } => {
                self.generate_expression(iterable)?;
                self.emit_opcode(OpCode::IterStart)?;
                
                let loop_start = self.output.len();
                self.emit_opcode(OpCode::IterNext)?;
                self.emit_string(&variable)?;
                
                self.emit_opcode(OpCode::JumpIfFalse)?;
                let exit_addr = self.output.len();
                self.emit_u32(0)?;
                
                for stmt in body {
                    self.generate_statement(stmt)?;
                }
                
                self.emit_opcode(OpCode::Jump)?;
                self.emit_u32(loop_start as u32)?;
                
                let loop_end = self.output.len();
                self.patch_jump(exit_addr, loop_end as u32)?;
            },
            Statement::Return(expr) => {
                if let Some(expr) = expr {
                    self.generate_expression(expr)?;
                    self.emit_opcode(OpCode::Return)?;
                } else {
                    self.emit_opcode(OpCode::ReturnVoid)?;
                }
            },
            Statement::Expression(expr) => {
                self.generate_expression(expr)?;
                self.emit_opcode(OpCode::Pop)?;
            },
        }
        Ok(())
    }
    
    fn generate_expression(&mut self, expr: Expression) -> Result<()> {
        match expr {
            Expression::Integer(n) => {
                self.emit_opcode(OpCode::PushInt)?;
                self.emit_i64(n)?;
            },
            Expression::Float(f) => {
                self.emit_opcode(OpCode::PushFloat)?;
                self.emit_f64(f)?;
            },
            Expression::String(s) => {
                self.emit_opcode(OpCode::PushString)?;
                self.emit_string(&s)?;
            },
            Expression::Boolean(b) => {
                self.emit_opcode(if b { OpCode::PushTrue } else { OpCode::PushFalse })?;
            },
            Expression::Identifier(name) => {
                self.emit_opcode(OpCode::Load)?;
                self.emit_string(&name)?;
            },
            Expression::Binary { left, op, right } => {
                self.generate_expression(*left)?;
                self.generate_expression(*right)?;
                self.emit_binary_op(op)?;
            },
            Expression::Unary { op, expr } => {
                self.generate_expression(*expr)?;
                self.emit_unary_op(op)?;
            },
            Expression::Call { function, arguments } => {
                for arg in arguments {
                    self.generate_expression(arg)?;
                }
                self.emit_opcode(OpCode::Call)?;
                self.emit_string(&function)?;
            },
            Expression::Index { object, index } => {
                self.generate_expression(*object)?;
                self.generate_expression(*index)?;
                self.emit_opcode(OpCode::Index)?;
            },
            Expression::Field { object, field } => {
                self.generate_expression(*object)?;
                self.emit_opcode(OpCode::GetField)?;
                self.emit_string(&field)?;
            },
            Expression::Array(items) => {
                for item in items.iter().rev() {
                    self.generate_expression(item.clone())?;
                }
                self.emit_opcode(OpCode::MakeArray)?;
                self.emit_u32(items.len() as u32)?;
            },
        }
        Ok(())
    }
    
    fn emit_binary_op(&mut self, op: BinaryOp) -> Result<()> {
        let opcode = match op {
            BinaryOp::Add => OpCode::Add,
            BinaryOp::Subtract => OpCode::Sub,
            BinaryOp::Multiply => OpCode::Mul,
            BinaryOp::Divide => OpCode::Div,
            BinaryOp::Modulo => OpCode::Mod,
            BinaryOp::Equal => OpCode::Eq,
            BinaryOp::NotEqual => OpCode::Ne,
            BinaryOp::Less => OpCode::Lt,
            BinaryOp::Greater => OpCode::Gt,
            BinaryOp::LessEqual => OpCode::Le,
            BinaryOp::GreaterEqual => OpCode::Ge,
            BinaryOp::And => OpCode::And,
            BinaryOp::Or => OpCode::Or,
        };
        self.emit_opcode(opcode)
    }
    
    fn emit_unary_op(&mut self, op: UnaryOp) -> Result<()> {
        let opcode = match op {
            UnaryOp::Not => OpCode::Not,
            UnaryOp::Negate => OpCode::Neg,
        };
        self.emit_opcode(opcode)
    }
    
    fn emit_opcode(&mut self, opcode: OpCode) -> Result<()> {
        self.output.push(opcode as u8);
        Ok(())
    }
    
    fn emit_u32(&mut self, value: u32) -> Result<()> {
        self.output.write_all(&value.to_le_bytes())?;
        Ok(())
    }
    
    fn emit_i64(&mut self, value: i64) -> Result<()> {
        self.output.write_all(&value.to_le_bytes())?;
        Ok(())
    }
    
    fn emit_f64(&mut self, value: f64) -> Result<()> {
        self.output.write_all(&value.to_le_bytes())?;
        Ok(())
    }
    
    fn emit_string(&mut self, s: &str) -> Result<()> {
        let bytes = s.as_bytes();
        self.emit_u32(bytes.len() as u32)?;
        self.output.write_all(bytes)?;
        Ok(())
    }
    
    fn patch_jump(&mut self, addr: usize, target: u32) -> Result<()> {
        let bytes = target.to_le_bytes();
        self.output[addr..addr + 4].copy_from_slice(&bytes);
        Ok(())
    }
}

#[repr(u8)]
enum OpCode {
    Nop = 0x00,
    
    PushInt = 0x10,
    PushFloat = 0x11,
    PushString = 0x12,
    PushTrue = 0x13,
    PushFalse = 0x14,
    
    Pop = 0x20,
    Load = 0x21,
    Store = 0x22,
    
    Add = 0x30,
    Sub = 0x31,
    Mul = 0x32,
    Div = 0x33,
    Mod = 0x34,
    Neg = 0x35,
    
    Eq = 0x40,
    Ne = 0x41,
    Lt = 0x42,
    Gt = 0x43,
    Le = 0x44,
    Ge = 0x45,
    
    And = 0x50,
    Or = 0x51,
    Not = 0x52,
    
    Jump = 0x60,
    JumpIfFalse = 0x61,
    
    Call = 0x70,
    Return = 0x71,
    ReturnVoid = 0x72,
    
    MakeArray = 0x80,
    Index = 0x81,
    GetField = 0x82,
    
    IterStart = 0x90,
    IterNext = 0x91,
    
    EnvStart = 0xA0,
    EnvParam = 0xA1,
    EnvEnd = 0xA2,
    
    FuncStart = 0xB0,
    FuncEnd = 0xB1,
}

pub fn generate(program: Program, options: &CompilerOptions) -> Result<Vec<u8>> {
    let mut generator = CodeGenerator::new(options);
    generator.generate(program)
}