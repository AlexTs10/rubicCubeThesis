import assert from "node:assert/strict";
import { existsSync } from "node:fs";
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
