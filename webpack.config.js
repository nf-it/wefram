const production = process.env.NODE_ENV === 'production'
const path = require('path')
const HtmlWebpackPlugin = require('html-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const TsconfigPathsPlugin = require('tsconfig-paths-webpack-plugin');
const ForkTsCheckerWebpackPlugin = require('fork-ts-checker-webpack-plugin');
// const CleanWebpackPlugin = require('clean-webpack-plugin')

const buildConfig = require('./build.json')
const appsDir = buildConfig.appsDir
const coreDir = buildConfig.coreDir

module.exports = {
  mode: process.env.NODE_ENV || 'production',
  context: __dirname,
  entry: `./${coreDir}/web/main.tsx`,
  output: {
    path: path.resolve(__dirname, buildConfig.staticsDir),
    publicPath: `${buildConfig.staticsUrl}/`,
    filename: 'app.[contenthash].js',
    chunkFilename: '[name].[chunkhash].js'
  },
  target: 'web',
  resolve: {
    extensions: ['.js', '.ts', '.tsx'],
    mainFields: ['module', 'browser', 'main'],
    plugins: [
      new TsconfigPathsPlugin({ configFile: "./tsconfig.json" })
    ],
    alias: {
      system: path.resolve(__dirname, coreDir, 'web'),
      project: path.resolve(__dirname, appsDir)
    }
  },
  module: {
    rules: [
      {
        test: /\.(ts|tsx)$/,
        use: [
          {
            loader: 'ts-loader',
            options: {
              logLevel: 'error',
              silent: true,
              // happyPackMode: true,
              transpileOnly: true
            }
          }
        ]
        // use: [{
        //   loader: require.resolve('babel-loader'),
        //   options: {
        //     configFile: false,
        //     cacheDirectory: !production ? '.cache/babel' : false,
        //     cacheCompression: false,
        //     presets: [
        //       '@babel/preset-react',
        //       '@babel/preset-typescript',
        //       '@babel/preset-env',
        //     ],
        //     plugins: [
        //       '@babel/plugin-transform-regenerator'
        //     ]
        //   }
        // }]
      },
      {
        test: /\.css$/,
        use: [
          MiniCssExtractPlugin.loader,
          {
            loader: "css-loader"
          },
          // {
          //   loader: "postcss-loader"
          // }
        ]
      },
      {
        test: /\.html$/,
        use: [
          'html-loader'
        ]
      },
      {
        test: /\.(a?png|svg)$/,
        use: [
          'url-loader?limit=10000'
        ]
      },
      {
        test: /\.(jpe?g|gif|bmp|mp3|mp4|ogg|wav|eot|ttf|woff|woff2)$/,
        use: [
          'file-loader'
        ]
      }
    ]
  },
  optimization: {
    splitChunks: {
      name: false,
      cacheGroups: {
        commons: {
          chunks: 'initial',
          minChunks: 2
        },
        vendors: {
          test: /[\\/]node_modules[\\/]/,
          chunks: 'all',
          filename: 'vendor.[contenthash].js',
          priority: -10
        }
      }
    },
    runtimeChunk: true
  },
  // devtool: production ? undefined : 'source-map',
  // devtool: 'source-map',
  devtool: false,
  plugins: [
    new ForkTsCheckerWebpackPlugin(),
    new MiniCssExtractPlugin({
        filename: 'app.[contenthash].css'
    }),
    new HtmlWebpackPlugin({
      template: `${coreDir}/web/dist/index.html`,
      minify: {
          minifyJS: true,
          minifyCSS: true,
          removeComments: true,
          useShortDoctype: true,
          collapseWhitespace: true,
          collapseInlineTagWhitespace: true
      },
      append: {
          head: `<script src="//cdn.polyfill.io/v3/polyfill.min.js"></script>`
      }
    }),
  ]
};
