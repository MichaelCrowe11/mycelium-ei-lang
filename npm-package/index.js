/**
 * Mycelium-EI-Lang for Node.js
 * Bio-inspired programming language with quantum computing integration
 * 
 * @author Michael Benjamin Crowe
 * @license Proprietary
 */

const { spawn } = require('child_process');
const path = require('path');

class MyceliumCompiler {
    constructor(options = {}) {
        this.pythonPath = options.pythonPath || 'python';
        this.debug = options.debug || false;
    }

    /**
     * Compile Mycelium code
     * @param {string} code - Mycelium source code
     * @returns {Promise<Object>} Compilation result
     */
    async compile(code) {
        return new Promise((resolve, reject) => {
            const process = spawn(this.pythonPath, ['-m', 'mycelium_ei', '--compile'], {
                stdio: ['pipe', 'pipe', 'pipe']
            });

            let stdout = '';
            let stderr = '';

            process.stdout.on('data', (data) => {
                stdout += data.toString();
            });

            process.stderr.on('data', (data) => {
                stderr += data.toString();
            });

            process.on('close', (code) => {
                if (code === 0) {
                    resolve({ success: true, output: stdout });
                } else {
                    reject(new Error(`Compilation failed: ${stderr}`));
                }
            });

            process.stdin.write(code);
            process.stdin.end();
        });
    }

    /**
     * Run Mycelium file
     * @param {string} filePath - Path to .myc file
     * @returns {Promise<Object>} Execution result
     */
    async run(filePath) {
        return new Promise((resolve, reject) => {
            const process = spawn(this.pythonPath, ['-m', 'mycelium_ei', filePath]);

            let stdout = '';
            let stderr = '';

            process.stdout.on('data', (data) => {
                stdout += data.toString();
                if (this.debug) console.log(data.toString());
            });

            process.stderr.on('data', (data) => {
                stderr += data.toString();
                if (this.debug) console.error(data.toString());
            });

            process.on('close', (code) => {
                if (code === 0) {
                    resolve({ success: true, output: stdout });
                } else {
                    reject(new Error(`Execution failed: ${stderr}`));
                }
            });
        });
    }
}

class BioOptimizer {
    constructor(compiler = null) {
        this.compiler = compiler || new MyceliumCompiler();
    }

    /**
     * Run genetic algorithm optimization
     * @param {Object} options - Optimization parameters
     * @returns {Promise<Object>} Optimization results
     */
    async genetic(options) {
        const code = `
            result = genetic_optimize(
                fitness_function="${options.fitness}",
                dimensions=${options.dimensions || 2},
                population_size=${options.population || 50},
                generations=${options.generations || 100}
            )
            print(result)
        `;
        return this.compiler.compile(code);
    }

    /**
     * Run particle swarm optimization
     * @param {Object} options - Optimization parameters
     * @returns {Promise<Object>} Optimization results
     */
    async swarm(options) {
        const code = `
            result = swarm_optimize(
                fitness_function="${options.fitness}",
                dimensions=${options.dimensions || 2},
                num_particles=${options.particles || 30},
                iterations=${options.iterations || 100}
            )
            print(result)
        `;
        return this.compiler.compile(code);
    }

    /**
     * Run ant colony optimization
     * @param {Object} options - Optimization parameters
     * @returns {Promise<Object>} Optimization results
     */
    async antColony(options) {
        const code = `
            result = ant_optimize(
                fitness_function="${options.fitness}",
                dimensions=${options.dimensions || 2},
                num_ants=${options.ants || 20},
                iterations=${options.iterations || 100}
            )
            print(result)
        `;
        return this.compiler.compile(code);
    }
}

module.exports = {
    MyceliumCompiler,
    BioOptimizer,
    version: '0.1.0'
};