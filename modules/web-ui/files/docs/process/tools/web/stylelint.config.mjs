// Template from the scaffold's web-ui module (docs/process/modules/web-ui.md, "Repository setup").
// Copied by the bootstrap to the repository root; from then on it is the project's own.
//
// One rule kept by a machine: colours come from the design tokens only (principle 6, one way). A colour literal is
// allowed only in the token files, named in TOKEN_FILES. No style or formatting rules.
const TOKEN_FILES = ["**/tokens.css", "**/theme*.css"];

const COLOUR_FUNCTIONS = ["rgb", "rgba", "hsl", "hsla", "hwb", "lab", "lch", "oklab", "oklch", "color"];

export default {
  rules: {
    "color-no-hex": [true, { message: "Use a colour token (var(--...)), not a hex colour" }],
    "color-named": ["never", { message: "Use a colour token (var(--...)), not a named colour" }],
    "function-disallowed-list": [COLOUR_FUNCTIONS, { message: "Use a colour token (var(--...)), not a colour function" }],
    "color-no-invalid-hex": true,
  },
  overrides: [
    {
      files: TOKEN_FILES,
      rules: { "color-no-hex": null, "color-named": null, "function-disallowed-list": null },
    },
  ],
};
