const path = require("path");
const HtmlWebpackPlugin = require("html-webpack-plugin");
const { CleanWebpackPlugin } = require("clean-webpack-plugin");

module.exports = {
    entry: {
        main: "./static/js/index.js",
        vendor: "./static/js/vendor.js",
    },
    output: {
        filename: "js/[name].bundle.js",
        path: path.resolve(__dirname, "dist"),
    },
    plugins: [
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
}