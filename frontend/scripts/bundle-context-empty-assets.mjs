#!/usr/bin/env node
import { spawnSync } from "child_process";
import path from "path";
import { fileURLToPath } from "url";

const rootScript = path.join(
  path.dirname(fileURLToPath(import.meta.url)),
  "..",
  "..",
  "scripts",
  "bundle-context-empty-assets.mjs",
);

const { status } = spawnSync(process.execPath, [rootScript], { stdio: "inherit" });
process.exit(status ?? 1);
