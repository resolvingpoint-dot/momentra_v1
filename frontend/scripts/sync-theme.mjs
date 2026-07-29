import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const source = path.join(root, "..", "design", "momentra_theme.css");
const target = path.join(root, "styles", "momentra_theme.css");

fs.mkdirSync(path.dirname(target), { recursive: true });

if (fs.existsSync(source)) {
  fs.copyFileSync(source, target);
  console.log("synced momentra_theme.css from design/momentra_theme.css");
} else if (fs.existsSync(target)) {
  console.warn(
    "skip theme sync: design/momentra_theme.css not found; using committed web/styles/momentra_theme.css",
  );
} else {
  console.error(
    "missing theme: neither design/momentra_theme.css nor web/styles/momentra_theme.css exists",
  );
  process.exit(1);
}
