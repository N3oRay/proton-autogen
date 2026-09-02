module.exports = {
  multipass: true,

  plugins: [
    {
      name: "preset-default",
      params: {
        overrides: {
          cleanupIds: {
            minify: true,
            remove: true,
          },

          cleanupNumericValues: {
            floatPrecision: 1,
            leadingZero: false,
            defaultPx: true,
          },

          convertPathData: {
            floatPrecision: 1,
            transformPrecision: 1,
            straightCurves: true,
            lineShorthands: true,
            curveSmoothShorthands: true,
            convertToQ: true,
            removeUseless: true,
            collapseRepeated: true,
            leadingZero: false,
            negativeExtraSpace: true,
          },

          convertTransform: {
            floatPrecision: 1,
            transformPrecision: 1,
            convertToShorts: true,
            matrixToTransform: true,
            shortTranslate: true,
            shortScale: true,
            shortRotate: true,
            removeUseless: true,
            collapseIntoOne: true,
          },

          mergePaths: {
            floatPrecision: 1,
          },
        },
      },
    },

    "removeTitle",
    "removeDesc",
    "removeMetadata",
    "removeEditorsNSData",
    "removeEmptyContainers",
    "removeEmptyText",
    "removeHiddenElems",
    "removeUselessDefs",
    "convertShapeToPath",
    "mergePaths",
    "sortDefsChildren",
  ],
};
