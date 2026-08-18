module.exports = {
  multipass: true,
  plugins: [
    "preset-default",
    {
      name: "convertPathData",
      params: {
        floatPrecision: 2,
      },
    },
    {
      name: "cleanupNumericValues",
      params: {
        floatPrecision: 2,
      },
    },
  ],
};
