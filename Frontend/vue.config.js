const { defineConfig } = require('@vue/cli-service');

const backPath = 'http://【Your_ip_addr_main】:8080';

module.exports = defineConfig({
  publicPath: './',
  transpileDependencies: true,
  lintOnSave: false,
  configureWebpack: {
    resolve: {
      alias: {
        'vue$': 'vue/dist/vue.esm.js',
      },
    },
  },
  devServer: {
    proxy: {
      '/nmas': {
        target: backPath, // 指定目标服务器
        changeOrigin: true,
        secure: false,
        pathRewrite: {
          '^/nmas': '/',
        },
        onProxyRes(proxyRes, req, res) {
          // 移除 X-Frame-Options 头
          delete proxyRes.headers['x-frame-options'];
        },
      },
      '/nmas_data': {
        target: backPath, // 指定目标服务器
        changeOrigin: true,
        secure: false,
        pathRewrite: {
          '^/nmas_data': '/',
        },
        onProxyRes(proxyRes, req, res) {
          // 移除 X-Frame-Options 头
          delete proxyRes.headers['x-frame-options'];
        },
      },
    },
  },
});
