const common = require("./webpack.common");
const { merge } = require('webpack-merge');
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const CssMinimizerPlugin = require("css-minimizer-webpack-plugin");

module.exports = merge(common, {
    mode: "production",
    devtool: 'source-map',
    plugins: [
        new MiniCssExtractPlugin({ 
            filename: "css/[name].[contenthash].bundle.css",
            chunkFilename: "[id].css",
         })
    ],
    module: {
        rules: [
            {
                test: /\.scss$/,
                use: [
                    MiniCssExtractPlugin.loader, // Extracts CSS from js
                    "css-loader", // CSS into JS
                    "sass-loader", // SCSS into CSS
                ]
            }
        ]
    },
    optimization: {
        minimizer: [
          `...`,
          new CssMinimizerPlugin(),
        ],
      },
})