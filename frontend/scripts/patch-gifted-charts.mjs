import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const root = path.dirname(fileURLToPath(import.meta.url));
const target = path.join(
  root,
  "../node_modules/gifted-charts-core/dist/PieChart/main.js",
);

if (!fs.existsSync(target)) {
  process.exit(0);
}

const source = fs.readFileSync(target, "utf8");
const needle = "    console.log('showTooltip----->', showTooltip);\n";
if (!source.includes(needle)) {
  process.exit(0);
}

fs.writeFileSync(target, source.replace(needle, ""));
console.log("patched gifted-charts-core: removed showTooltip debug log");
