use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Program {
    pub nodes: Vec<AstNode>,
}

impl Program {
    pub fn node_count(&self) -> usize {
        self.nodes.len() + self.nodes.iter().map(|n| n.child_count()).sum::<usize>()
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum AstNode {
    Environment(Environment),
    Function(Function),
    Statement(Statement),
    Expression(Expression),
}

impl AstNode {
    pub fn child_count(&self) -> usize {
        match self {
            AstNode::Environment(_) => 1,
            AstNode::Function(f) => f.body.len(),
            AstNode::Statement(s) => s.child_count(),
            AstNode::Expression(e) => e.child_count(),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Environment {
    pub parameters: Vec<EnvironmentParam>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EnvironmentParam {
    pub name: String,
    pub value: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Function {
    pub name: String,
    pub parameters: Vec<Parameter>,
    pub return_type: Option<Type>,
    pub body: Vec<Statement>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Parameter {
    pub name: String,
    pub ty: Type,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum Type {
    Integer,
    Float,
    String,
    Boolean,
    Mycelium,
    Network,
    Signal,
    Array(Box<Type>),
    Custom(String),
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum Statement {
    Let {
        name: String,
        ty: Option<Type>,
        value: Expression,
    },
    Assignment {
        target: String,
        value: Expression,
    },
    If {
        condition: Expression,
        then_branch: Vec<Statement>,
        else_branch: Option<Vec<Statement>>,
    },
    While {
        condition: Expression,
        body: Vec<Statement>,
    },
    For {
        variable: String,
        iterable: Expression,
        body: Vec<Statement>,
    },
    Return(Option<Expression>),
    Expression(Expression),
}

impl Statement {
    pub fn child_count(&self) -> usize {
        match self {
            Statement::Let { .. } => 1,
            Statement::Assignment { .. } => 1,
            Statement::If { then_branch, else_branch, .. } => {
                then_branch.len() + else_branch.as_ref().map_or(0, |b| b.len())
            },
            Statement::While { body, .. } => body.len(),
            Statement::For { body, .. } => body.len(),
            Statement::Return(_) => 1,
            Statement::Expression(_) => 1,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum Expression {
    Integer(i64),
    Float(f64),
    String(String),
    Boolean(bool),
    Identifier(String),
    Binary {
        left: Box<Expression>,
        op: BinaryOp,
        right: Box<Expression>,
    },
    Unary {
        op: UnaryOp,
        expr: Box<Expression>,
    },
    Call {
        function: String,
        arguments: Vec<Expression>,
    },
    Index {
        object: Box<Expression>,
        index: Box<Expression>,
    },
    Field {
        object: Box<Expression>,
        field: String,
    },
    Array(Vec<Expression>),
}

impl Expression {
    pub fn child_count(&self) -> usize {
        match self {
            Expression::Binary { .. } => 2,
            Expression::Unary { .. } => 1,
            Expression::Call { arguments, .. } => arguments.len(),
            Expression::Index { .. } => 2,
            Expression::Field { .. } => 1,
            Expression::Array(items) => items.len(),
            _ => 0,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum BinaryOp {
    Add,
    Subtract,
    Multiply,
    Divide,
    Modulo,
    Equal,
    NotEqual,
    Less,
    Greater,
    LessEqual,
    GreaterEqual,
    And,
    Or,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum UnaryOp {
    Not,
    Negate,
}