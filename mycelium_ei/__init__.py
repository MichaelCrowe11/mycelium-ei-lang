"""
Mycelium-EI-Lang: Bio-Inspired Programming Language with Quantum Computing
Copyright (c) 2024 Michael Benjamin Crowe. All Rights Reserved.

This module provides the core functionality for the Mycelium-EI-Lang interpreter.
"""

__version__ = "0.1.1"
__author__ = "Michael Benjamin Crowe"
__license__ = "Proprietary"

import sys
import os

from .interpreter import MyceliumInterpreter

# Create aliases for compatibility
Interpreter = MyceliumInterpreter

# Public API
__all__ = [
    "MyceliumInterpreter",
    "Interpreter",
    "run_file", 
    "run_code",
    "main",
]

def run_file(filename: str) -> None:
    """Run a Mycelium-EI-Lang file"""
    with open(filename, 'r') as f:
        source = f.read()
    run_code(source)

def run_code(source: str) -> None:
    """Run Mycelium-EI-Lang code"""
    interpreter = Interpreter()
    interpreter.execute(source)

def main():
    """Main entry point for command-line usage"""
    if len(sys.argv) < 2:
        print(f"Mycelium-EI-Lang Interpreter v{__version__}")
        print("Usage: python -m mycelium_ei <script.myc>")
        print("       python -m mycelium_ei --version")
        print("       python -m mycelium_ei --help")
        return
    
    arg = sys.argv[1]
    
    if arg == "--version":
        print(__version__)
        return
    
    if arg == "--help":
        print(f"""
Mycelium-EI-Lang v{__version__}
Bio-inspired programming language with quantum computing integration

Usage:
    python -m mycelium_ei <script.myc>    Execute a Mycelium script
    python -m mycelium_ei --version       Show version
    python -m mycelium_ei --help          Show this help

Features:
    🧬 Genetic algorithm optimization
    🐜 Swarm intelligence algorithms  
    🧠 Bio-inspired neural networks
    ⚛️ Quantum computing primitives
    🌱 Environmental cultivation systems

Documentation: https://github.com/MichaelCrowe11/pulsar-lang
        """)
        return
    
    # Execute file
    try:
        run_file(arg)
    except FileNotFoundError:
        print(f"Error: File '{arg}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()