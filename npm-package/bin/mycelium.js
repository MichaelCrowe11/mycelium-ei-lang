#!/usr/bin/env node

/**
 * Mycelium-EI-Lang CLI for Node.js
 */

const { MyceliumCompiler } = require('../index');
const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);

if (args.length === 0) {
    console.log(`
Mycelium-EI-Lang v0.1.0
Bio-inspired programming language with quantum computing

Usage:
  mycelium <file.myc>     Run a Mycelium file
  mycelium --help         Show this help message
  mycelium --version      Show version

Examples:
  mycelium script.myc
  mycelium examples/genetic.myc
`);
    process.exit(0);
}

if (args[0] === '--version') {
    console.log('0.1.0');
    process.exit(0);
}

if (args[0] === '--help') {
    console.log('Mycelium-EI-Lang - Bio-inspired programming language');
    process.exit(0);
}

const filePath = args[0];
if (!fs.existsSync(filePath)) {
    console.error(`Error: File not found: ${filePath}`);
    process.exit(1);
}

const compiler = new MyceliumCompiler({ debug: true });
compiler.run(filePath)
    .then(result => {
        console.log(result.output);
    })
    .catch(error => {
        console.error('Error:', error.message);
        process.exit(1);
    });