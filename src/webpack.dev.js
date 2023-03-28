const common = require("./webpack.common");
const { merge } = require('webpack-merge');
const HtmlWebpackPlugin = require("html-webpack-plugin");
const {CleanWebpackPlugin} = require("clean-webpack-plugin");

module.exports = merge(common, {
    mode: "development",
    module: {
        rules: [
            {
                test: /\.scss$/,
                use: [
                    "style-loader", // Inject CSS into DOM
                    "css-loader", // CSS into JS
                    "sass-loader", // SCSS into CSS
                ]
            }
        ]
    },
    plugins: [
        new HtmlWebpackPlugin({
            template:
                "./templates/pages/base.html",
            filename: "templates/pages/base.html",
            publicPath: "/static/",
            inject: "body"
        }),
        new HtmlWebpackPlugin({
            template:
                "./templates/dashboard/base.html",
            filename: "templates/dashboard/base.html",
            publicPath: "/static/",
            inject: "body"
        }),
        new CleanWebpackPlugin(),
    ],

});