// Template from the scaffold's typescript module (docs/process/modules/typescript.md, "Repository setup").
// Copied by the bootstrap to the repository root; from then on it is the project's own.
//
// Correctness rules only, no style rules (docs/process/code.md, "Static analysis"). Every rule is an error: a
// warning nobody has to fix is noise. The one warning is cognitive complexity, a size trigger (code.md).
// An eslint-disable comment must say why (principle 2); an unused one is an error.
// Run without --cache: with type information a change in one file can create a finding in another.
import { defineConfig } from "eslint/config";
import tseslint from "typescript-eslint";
import comments from "@eslint-community/eslint-plugin-eslint-comments";
import sonarjs from "eslint-plugin-sonarjs";

export default defineConfig(
  { ignores: ["**/node_modules/**", "**/dist/**", "**/coverage/**", "tmp/**"] },
  {
    files: ["**/*.{ts,tsx,mts,cts}"],
    languageOptions: {
      parser: tseslint.parser,
      parserOptions: { projectService: true, tsconfigRootDir: import.meta.dirname },
    },
    linterOptions: { reportUnusedDisableDirectives: "error" },
    plugins: {
      "@typescript-eslint": tseslint.plugin,
      "@eslint-community/eslint-comments": comments,
      sonarjs,
    },
    rules: {
      // Promises (principle 3, 5): a promise nobody awaits loses its error and its order.
      // node:test's test() returns a promise the runner awaits itself.
      "@typescript-eslint/no-floating-promises": [
        "error",
        { allowForKnownSafeCalls: [{ from: "package", package: "node:test", name: ["test", "describe", "it", "suite"] }] },
      ],
      "@typescript-eslint/no-misused-promises": "error",
      "@typescript-eslint/return-await": ["error", "in-try-catch"],

      // Every case decided: a new member of a union is an error wherever it is not handled; a default does not count.
      "@typescript-eslint/switch-exhaustiveness-check": [
        "error",
        { considerDefaultExhaustiveForUnions: false, requireDefaultForNonUnion: false },
      ],

      // Type safety is not worn away (principle 2): any, unchecked casts, the non-null !.
      "@typescript-eslint/no-explicit-any": "error",
      "@typescript-eslint/no-unsafe-assignment": "error",
      "@typescript-eslint/no-unsafe-member-access": "error",
      "@typescript-eslint/no-unsafe-call": "error",
      "@typescript-eslint/no-unsafe-return": "error",
      "@typescript-eslint/no-unsafe-argument": "error",
      "@typescript-eslint/no-non-null-assertion": "error",
      "@typescript-eslint/consistent-type-assertions": [
        "error",
        { assertionStyle: "as", objectLiteralTypeAssertions: "never" },
      ],

      // Errors say what and where (principle 5): only Error objects are thrown or rejected.
      "@typescript-eslint/only-throw-error": "error",
      "@typescript-eslint/prefer-promise-reject-errors": "error",

      eqeqeq: ["error", "always"],

      // Escapes carry their reason, and no blanket disables.
      "@eslint-community/eslint-comments/require-description": ["error", { ignore: ["eslint-enable"] }],
      "@eslint-community/eslint-comments/no-unlimited-disable": "error",

      // Size trigger: a second look, not a limit.
      "sonarjs/cognitive-complexity": ["warn", 15],
    },
  },
);
