import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { resolve } from "node:path";
import test from "node:test";

const root = resolve(import.meta.dirname, "..");

test("demo frontend source entrypoints exist", () => {
    for (const relativePath of [
        "src/app/page.tsx",
        "src/app/solver/page.tsx",
        "src/app/comparison/page.tsx",
        "src/components/cube/RubiksCube3D.tsx",
        "src/lib/solver.ts",
    ]) {
        assert.equal(existsSync(resolve(root, relativePath)), true, relativePath);
    }
});

test("synthetic solver source declares demo-only telemetry contract", () => {
    const source = readFileSync(resolve(root, "src/lib/solver.ts"), "utf8");

    assert.match(source, /export async function solveCube/);
    assert.match(source, /demoOnly:\s*true/);
    assert.match(source, /Synthetic preview/);
    assert.match(source, /generateDemoSolution/);
});

test("solver and comparison pages render the demo solver surfaces", () => {
    const solverPage = readFileSync(resolve(root, "src/app/solver/page.tsx"), "utf8");
    const comparisonPage = readFileSync(resolve(root, "src/app/comparison/page.tsx"), "utf8");

    assert.match(solverPage, /solveCube/);
    assert.match(solverPage, /RubiksCube3D|CubeNet/);
    assert.match(comparisonPage, /Comparison|comparison/i);
    assert.match(comparisonPage, /synthetic preview data|inverse/);
});
