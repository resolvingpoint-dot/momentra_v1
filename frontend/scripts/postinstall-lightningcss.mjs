import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const root = path.dirname(fileURLToPath(import.meta.url));
const platform = process.platform;
const arch = process.arch;

const platformPkg =
  platform === "darwin" && arch === "arm64"
    ? "lightningcss-darwin-arm64"
    : platform === "darwin" && arch === "x64"
      ? "lightningcss-darwin-x64"
      : platform === "linux" && arch === "x64"
        ? "lightningcss-linux-x64-gnu"
        : null;

if (!platformPkg) {
  process.exit(0);
}

const src = path.join(root, `../node_modules/${platformPkg}`);
const destDir = path.join(root, "../node_modules/lightningcss");
const binaryName = `lightningcss.${platform}-${arch === "arm64" ? "arm64" : arch}.node`;
const srcFile = path.join(src, binaryName);
const destFile = path.join(destDir, binaryName);

if (!fs.existsSync(srcFile) || !fs.existsSync(destDir)) {
  process.exit(0);
}

fs.copyFileSync(srcFile, destFile);
