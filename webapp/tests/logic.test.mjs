import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";
import ts from "typescript";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const moduleCache = new Map();

function loadTs(relativePath) {
    const absolutePath = resolve(root, relativePath);
    if (moduleCache.has(absolutePath)) {
        return moduleCache.get(absolutePath).exports;
    }

    const source = readFileSync(absolutePath, "utf8");
    const { outputText } = ts.transpileModule(source, {
        compilerOptions: {
            module: ts.ModuleKind.CommonJS,
            target: ts.ScriptTarget.ES2022,
            esModuleInterop: true,
        },
        fileName: absolutePath,
    });

    const moduleRecord = { exports: {} };
    moduleCache.set(absolutePath, moduleRecord);

    const localRequire = (specifier) => {
        if (specifier.startsWith("./") || specifier.startsWith("../")) {
            return loadTs(resolve(dirname(absolutePath), `${specifier}.ts`).slice(root.length + 1));
        }
        throw new Error(`Unexpected test import: ${specifier}`);
    };

    const fn = new Function("require", "module", "exports", outputText);
    fn(localRequire, moduleRecord, moduleRecord.exports);
    return moduleRecord.exports;
}

const cube = loadTs("src/lib/cube.ts");
const solver = loadTs("src/lib/solver.ts");
const constants = loadTs("src/lib/constants.ts");

test("cube move and inverse logic solves round trips", () => {
    const scramble = ["R", "U", "F2", "L'"];
    const scrambled = cube.applyMoves(cube.cloneCubeState(constants.SOLVED_STATE), scramble);

    assert.equal(cube.isSolved(scrambled), false);
    assert.deepEqual(cube.inverseMoves(scramble), ["L", "F2", "U'", "R'"]);
    assert.equal(
        cube.isSolved(cube.applyMoves(scrambled, cube.inverseMoves(scramble))),
        true
    );
});

test("cube parser rejects invalid move tokens", () => {
    assert.throws(() => cube.parseMoves("R X U"), /Invalid move token: X/);
    assert.throws(() => cube.inverseMove("X"), /Invalid move token: X/);
});

test("synthetic solveCube returns a verified inverse solution", async () => {
    const scramble = ["R", "U", "F2"];
    const state = cube.applyMoves(cube.cloneCubeState(constants.SOLVED_STATE), scramble);
    const result = await solver.solveCube(state, scramble, "kociemba", 30_000);

    assert.equal(result.solved, true);
    assert.equal(result.demoOnly, true);
    assert.equal(
        cube.isSolved(cube.applyMoves(state, result.solution)),
        true
    );
});

test("synthetic solver timeout path is executable", async () => {
    const scramble = Array.from({ length: 20 }, (_, index) => (index % 2 === 0 ? "R" : "U"));
    const state = cube.applyMoves(cube.cloneCubeState(constants.SOLVED_STATE), scramble);
    const result = await solver.solveCube(state, scramble, "korf", 1);

    assert.equal(result.solved, false);
    assert.match(result.error ?? "", /timed out|exceeded/);
});

test("comparison aggregation executes and reports winners", async () => {
    const scramble = ["R", "U", "R'"];
    const results = await solver.compareAlgorithms(scramble, {
        thistlethwaite: 30_000,
        kociemba: 30_000,
        korf: 30_000,
    });
    const analysis = solver.analyzeResults(results);

    assert.equal(results.length, 3);
    assert.ok(analysis.fastest === null || ["thistlethwaite", "kociemba", "korf"].includes(analysis.fastest));
    assert.ok(analysis.fewestMoves === null || ["thistlethwaite", "kociemba", "korf"].includes(analysis.fewestMoves));
    assert.ok(analysis.leastMemory === null || ["thistlethwaite", "kociemba", "korf"].includes(analysis.leastMemory));
});
