// Template from the scaffold's typescript module (docs/process/modules/typescript.md, "Repository setup").
// Copied by the bootstrap to .dependency-cruiser.cjs at the repository root; from then on it is the project's own.
//
// Only boundaries, no style. The project's own rules come from AGENTS.md, "Rules the code keeps": one rule each,
// with the same words in its comment. Existing violations go to a baseline (depcruise-baseline), never around it.
/** @type {import('dependency-cruiser').IConfiguration} */
module.exports = {
  forbidden: [
    // --- The project's boundaries (from AGENTS.md, "Rules the code keeps"). Example:
    // {
    //   name: "core-not-to-ui",
    //   comment: "core/ imports nothing from ui/.",
    //   severity: "error",
    //   from: { path: "^src/core/" },
    //   to: { path: "^src/ui/" },
    // },

    // --- General
    {
      name: "no-circular",
      comment: "A cycle between modules wears the layering away (principle 2).",
      severity: "error",
      from: {},
      to: { circular: true },
    },
    {
      name: "not-to-unresolvable",
      comment: "An import that resolves to nothing is a typo or a missing dependency.",
      severity: "error",
      from: {},
      to: { couldNotResolve: true },
    },
    {
      name: "not-to-dev-dep",
      comment: "Code that ships may not import a devDependency: it is missing when installed for production.",
      severity: "error",
      from: { path: "^(src|packages/[^/]+/src|apps/[^/]+/src)/", pathNot: "\\.(test|spec)\\.[cm]?tsx?$" },
      to: { dependencyTypes: ["npm-dev"], dependencyTypesNot: ["type-only"], pathNot: "node_modules/@types/" },
    },
  ],
  options: {
    doNotFollow: { path: "node_modules" },
    // Not node_modules here: excluding it hides every package import (and so not-to-dev-dep); doNotFollow is enough.
    exclude: { path: "(^|/)(dist|coverage|tmp)/" },
    // Type-only imports count: a type pulled across a boundary is still a dependency on the other side.
    tsPreCompilationDeps: true,
    tsConfig: { fileName: "tsconfig.json" },
    enhancedResolveOptions: {
      exportsFields: ["exports"],
      conditionNames: ["import", "require", "node", "default", "types"],
      extensions: [".ts", ".tsx", ".mts", ".cts", ".js", ".mjs", ".cjs", ".json"],
    },
  },
};
