const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const CopyPlugin = require('copy-webpack-plugin');

module.exports = {
    entry: './src/index.js',

    output: {
        filename: 'bundle.js',
        path: path.resolve(__dirname, 'dist'),
        clean: true,
        publicPath: '/',
    },

    devServer: {
        port: 8080,
        hot: true,

        // IMPORTANT:
        // Serve files directly from /public
        static: {
            directory: path.resolve(__dirname, 'public'),
            publicPath: '/',
        },

        devMiddleware: {
            publicPath: '/',
        },

        historyApiFallback: true,
    },

    plugins: [
        new HtmlWebpackPlugin({
            template: './public/index.html',
        }),

        new CopyPlugin({
            patterns: [
                {
                    from: './public/assets',
                    to: 'assets',
                    noErrorOnMissing: true,
                },
            ],
        }),
    ],

    module: {
        rules: [
            {
                test: /\.css$/i,
                use: ['style-loader', 'css-loader'],
            },

            {
                test: /\.(png|svg|jpg|jpeg|gif)$/i,
                type: 'asset/resource',
            },
        ],
    },
};