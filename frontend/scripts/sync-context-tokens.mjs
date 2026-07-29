import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const webRoot = path.join(__dirname, "..");
const srcDir = path.join(webRoot, "..", "design-tokens");
const outDir = path.join(webRoot, "styles", "context");

const mappings = [
  ["personal-tokens.css", "personal.css", "personal"],
  ["group-tokens.css", "group.css", "group"],
  ["business-tokens.css", "business.css", "business"],
];

const sourcesPresent = mappings.every(([srcName]) =>
  fs.existsSync(path.join(srcDir, srcName)),
);
const outputsPresent = mappings.every(([, destName]) =>
  fs.existsSync(path.join(outDir, destName)),
);

if (!sourcesPresent) {
  if (outputsPresent) {
    console.warn(
      "skip context token sync: design-tokens/*-tokens.css not found; using committed web/styles/context/*.css",
    );
    process.exit(0);
  }
  console.error(
    "missing design-tokens/*-tokens.css and one or more web/styles/context/*.css files",
  );
  process.exit(1);
}

fs.mkdirSync(outDir, { recursive: true });

for (const [srcName, destName, context] of mappings) {
  const srcPath = path.join(srcDir, srcName);
  const content = fs.readFileSync(srcPath, "utf8");
  const transformed = content.replace(
    /^:root\s*\{/m,
    `[data-momentra-context="${context}"] {`,
  );
  fs.writeFileSync(path.join(outDir, destName), transformed);
  console.log(`synced ${destName} from ${srcName}`);
}
