import fs from "fs";
import path from "path";

// Settings
// Only enforce naming conventions on the Next.js frontend. The Python backend
// (apps/api) uses PEP 8 snake_case and is checked by ruff instead.
const ROOT_DIR = path.join(process.cwd(), "apps", "web");
const IGNORE_DIRS = ["node_modules", ".git", ".husky", ".next", "dist", "build", "public", "test-utils"];
const IGNORE_FILES = [".eslintrc.cjs", ".eslintrc.js", "eslint.config.js", "eslint.config.mjs", "eslint-plugin-naming-convention.cjs"];

// Special Next.js / app-router convention files excluded from naming rules.
const NEXTJS_SPECIAL_FILES = [
  "page.tsx", "page.ts",
  "layout.tsx", "layout.ts",
  "loading.tsx", "error.tsx", "global-error.tsx",
  "not-found.tsx", "route.ts",
  "template.tsx", "default.tsx",
  "providers.tsx", "providers.ts",
  "middleware.ts", "instrumentation.ts",
];

let errors = [];

// Check if the first character is uppercase
function isFirstCharUppercase(name) {
  const firstChar = name.charAt(0);
  return firstChar === firstChar.toUpperCase() && firstChar !== firstChar.toLowerCase();
}

// Check if the first character is lowercase
function isFirstCharLowercase(name) {
  const firstChar = name.charAt(0);
  return firstChar === firstChar.toLowerCase() && firstChar !== firstChar.toUpperCase();
}

// Process a file
function processFile(filePath, relativePath) {
  const fileName = path.basename(filePath);

  // Skip ignored files and dot files
  if (IGNORE_FILES.includes(fileName) || fileName.startsWith(".")) {
    return;
  }

  // Skip Next.js special files like page.tsx, layout.tsx, etc.
  if (NEXTJS_SPECIAL_FILES.includes(fileName)) {
    return;
  }

  if (fileName.endsWith(".tsx")) {
    const isInHooksDir = relativePath.split(path.sep).includes("hooks");
    if (!isInHooksDir && !isFirstCharUppercase(fileName)) {
      errors.push(`TSX file must start with a capital letter: ${relativePath}`);
    }
  } else if (fileName.endsWith(".ts")) {
    if (!isFirstCharLowercase(fileName)) {
      errors.push(`TS file must start with a small letter: ${relativePath}`);
    }
  }
}

// Process a directory
function processDirectory(dirPath, relativePath = "") {
  try {
    const entries = fs.readdirSync(dirPath, { withFileTypes: true });

    // Check folder name first (except for the root directory)
    if (relativePath) {
      const folderName = path.basename(dirPath);

      // Skip if it's in the ignore list or a Next.js route parameter folder (starting with [)
      if (!IGNORE_DIRS.includes(folderName) &&
        ![".", "[", "(", "_"].some(prefix => folderName.startsWith(prefix))) {
        if (!isFirstCharLowercase(folderName)) {
          errors.push(`Folder must start with a small letter: ${relativePath}`);
        }
      }
    }

    // Process entries
    for (const entry of entries) {
      const entryPath = path.join(dirPath, entry.name);
      const entryRelativePath = path.join(relativePath, entry.name);

      if (entry.isDirectory()) {
        // Skip directories in the ignore list
        if (!IGNORE_DIRS.includes(entry.name) && !entry.name.startsWith(".")) {
          processDirectory(entryPath, entryRelativePath);
        }
      } else if (entry.isFile()) {
        processFile(entryPath, entryRelativePath);
      }
    }
  } catch (err) {
    console.error(`Error processing directory ${dirPath}: ${err.message}`);
  }
}

// Start processing from the root directory
console.log("Checking file naming conventions...");
processDirectory(ROOT_DIR);

// Report errors
if (errors.length > 0) {
  console.error("\n❌ File naming convention check failed. Please fix the following issues before committing:");
  errors.forEach(error => console.error(`  - ${error}`));
  console.error("\nNaming conventions:");
  console.error("  🔹 TSX files must start with a capital letter (except in hooks/ directory)");
  console.error("  🔹 TS files must start with a small letter");
  console.error("  🔹 Folders must start with a small letter");
  process.exit(1);
} else {
  console.log("✅ File naming convention check passed.");
  process.exit(0);
}
