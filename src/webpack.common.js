const path = require("path");

module.exports = {
    entry: {
        main: "./static/js/index.js",
        vendor: "./static/js/vendor.js",
    },
    output: {
        filename: "js/[name].bundle.js",
        path: path.resolve(__dirname, "dist"),
    },
}