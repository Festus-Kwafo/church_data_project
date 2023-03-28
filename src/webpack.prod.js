const common = require("./webpack.common");
const { merge } = require('webpack-merge');
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const CssMinimizerPlugin = require("css-minimizer-webpack-plugin");
const HtmlWebpackPlugin = require("html-webpack-plugin");
const {CleanWebpackPlugin} = require("clean-webpack-plugin");

module.exports = merge(common, {
    mode: "production",
    devtool: 'source-map',
    plugins: [

    ],
    plugins: [
        new MiniCssExtractPlugin({
            filename: "css/[name].bundle.css",
            chunkFilename: "[id].css",
         }),
        new HtmlWebpackPlugin({
            template:
                "./templates/pages/base.html",
            filename: "templates/pages/base.html",
            publicPath: "https://clcdata-static.s3.amazonaws.com/static/",
            inject: "body"
        }),
        new HtmlWebpackPlugin({
            template:
                "./templates/dashboard/base.html",
            filename: "templates/dashboard/base.html",
            publicPath: "https://clcdata-static.s3.amazonaws.com/static/",
            inject: "body"
        }),
        new CleanWebpackPlugin(),
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