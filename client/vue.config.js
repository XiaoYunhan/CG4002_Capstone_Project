module.exports = {
  transpileDependencies: ["vuetify"],
  devServer: {
    proxy: {
      "/dashboard": {
        target: "http://localhost:4000",
        ws: true,
        changeOrigin: true,
      },
    },
  },
};
