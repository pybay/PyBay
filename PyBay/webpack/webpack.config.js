const webpack = require("webpack");
const path = require("path");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");

module.exports = {
  entry: {
    app: "./js/main.js",
    styles: "./scss/main.scss",
  },
  output: {
    path: path.join(path.dirname(__dirname), "assets", "static", "gen"),
    filename: "[name].js",
  },
  devtool: "source-map",
  mode: "production",
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: [
          {
            loader: "babel-loader",
            options: {
              presets: ["@babel/preset-env"],
            },
          },
        ],
      },
      {
        test: /\.scss$/,
        use: [MiniCssExtractPlugin.loader, "css-loader", "sass-loader"],
      },
      {
        test: /\.css$/,
        use: [MiniCssExtractPlugin.loader, "css-loader"],
      },
      {
        test: /\.(woff2?|ttf|eot|svg|png|jpe?g|gif)$/,
        type: "asset",
      },
    ],
  },
  plugins: [
      new webpack.ProvidePlugin({
      jQuery: "jquery",
    }),
  new MiniCssExtractPlugin()],
};