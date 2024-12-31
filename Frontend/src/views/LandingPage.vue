<template>
  <div style="margin: 0; padding: 0; width: 100vw; height: 100vh; overflow: hidden;">
    <!-- 使用 iframe 嵌入 HTML 页面 -->
    <iframe src="/landingPage.html" style="width: 100vw; height: 100vh; border: none;"></iframe>
  </div>
</template>

<script>
export default {
  name: 'LandingPage',
  mounted() {
    // 监听 iframe 消息
    window.addEventListener('message', this.handleMessage);
  },
  beforeDestroy() {
    window.removeEventListener('message', this.handleMessage);
  },
  methods: {
    handleMessage(event) {
      if (event.origin !== window.location.origin) return; // 确保消息来源安全

      const { action, path, url, text } = event.data || {};
      if (action === 'navigate' && path) {
        this.$router.push(path); // 使用 Vue Router 进行跳转
      } else if (action === 'open-url' && url) {
        window.open(url, '_blank'); // 在新标签页中打开外部链接
      } else if (action === 'copy-to-clipboard' && text) {
        // 复制到剪贴板
        navigator.clipboard.writeText(text)
          .then(() => {
            console.log(`Copied to clipboard: ${text}`);
            alert('Email已复制到剪贴板！'); // 提示用户复制成功
          })
          .catch((err) => {
            console.error('Failed to copy text: ', err);
            alert('复制失败，请重试！');
          });
      } else {
        console.warn('Invalid message data:', event.data);
      }
    },
  },
};
</script>

<style scoped>
</style>
