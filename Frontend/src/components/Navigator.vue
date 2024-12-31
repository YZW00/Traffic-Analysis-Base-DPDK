<template>
  <div>
    <div class="navbar" 
         @mouseenter="handleMouseEnter" 
         @mouseleave="handleMouseLeave" 
         :style="{ opacity: navbarOpacity }">
      <div class="navbar-left">
        <img src="@/assets/images/icon.png" alt="Logo" class="navbar-logo" />
      </div>
      <el-menu mode="horizontal" class="navbar-menu" active-text-color="#409EFF">
        <el-menu-item index="1" @click="navigateTo('/landing')">首页</el-menu-item>
        <el-menu-item index="2" @click="navigateTo('/collect')">流量采集</el-menu-item>
        <el-menu-item index="3" @click="navigateTo('/anomaly')">异常检测</el-menu-item>
        <el-menu-item index="4" @click="navigateTo('/portrait')">用户画像</el-menu-item>
        <el-menu-item index="5" @click="navigateTo('/serviceCls')">业务分类</el-menu-item>
      </el-menu>
    </div>
    <div class="user-box">
    </div>
    <!--wrapper-->
    <div class="wrapper">
        <!--start overlay-->
        <div class="overlay toggle-icon"></div>
        <!--end overlay-->
        <!--Start Back To Top Button--> <a href="javaScript:;" class="back-to-top"><i class='bx bxs-up-arrow-alt'></i></a>
        <!--End Back To Top Button-->
        <footer class="page-footer">
            <p class="mb-0">Copyright © 2023. All right reserved.</p>
        </footer>
    </div>
    <!--end wrapper-->
    <!--start switcher-->
    <div class="switcher-wrapper">
        
        <div class="switcher-body">
            <div class="d-flex align-items-center">
                <h5 class="mb-0 text-uppercase">主题设置</h5>
                <button type="button" class="btn-close ms-auto close-switcher" aria-label="Close"></button>
            </div>
            <hr/>
            <h6 class="mb-0">主题样式</h6>
            <hr/>
            <div class="d-flex align-items-center justify-content-between">
                <div class="form-check">
                    <input class="form-check-input" type="radio" name="flexRadioDefault" id="lightmode" checked>
                    <label class="form-check-label" for="lightmode">白色</label>
                </div>
                <div class="form-check">
                    <input class="form-check-input" type="radio" name="flexRadioDefault" id="darkmode">
                    <label class="form-check-label" for="darkmode">黑色</label>
                </div>
                <div class="form-check">
                    <input class="form-check-input" type="radio" name="flexRadioDefault" id="semidark">
                    <label class="form-check-label" for="semidark">半黑色</label>
                </div>
            </div>
            <hr/>
            <h6 class="mb-0">头部颜色</h6>
            <hr/>
            <div class="header-colors-indigators">
                <div class="row row-cols-auto g-3">
                    <div class="col">
                        <div class="indigator headercolor1" id="headercolor1"></div>
                    </div>
                    <div class="col">
                        <div class="indigator headercolor2" id="headercolor2"></div>
                    </div>
                    <div class="col">
                        <div class="indigator headercolor3" id="headercolor3"></div>
                    </div>
                    <div class="col">
                        <div class="indigator headercolor4" id="headercolor4"></div>
                    </div>
                    <div class="col">
                        <div class="indigator headercolor5" id="headercolor5"></div>
                    </div>
                    <div class="col">
                        <div class="indigator headercolor6" id="headercolor6"></div>
                    </div>
                    <div class="col">
                        <div class="indigator headercolor7" id="headercolor7"></div>
                    </div>
                    <div class="col">
                        <div class="indigator headercolor8" id="headercolor8"></div>
                    </div>
                </div>
            </div>
            <hr/>
            <h6 class="mb-0">边栏颜色</h6>
            <hr/>
            <div class="header-colors-indigators">
                <div class="row row-cols-auto g-3">
                    <div class="col">
                        <div class="indigator sidebarcolor1" id="sidebarcolor1"></div>
                    </div>
                    <div class="col">
                        <div class="indigator sidebarcolor2" id="sidebarcolor2"></div>
                    </div>
                    <div class="col">
                        <div class="indigator sidebarcolor3" id="sidebarcolor3"></div>
                    </div>
                    <div class="col">
                        <div class="indigator sidebarcolor4" id="sidebarcolor4"></div>
                    </div>
                    <div class="col">
                        <div class="indigator sidebarcolor5" id="sidebarcolor5"></div>
                    </div>
                    <div class="col">
                        <div class="indigator sidebarcolor6" id="sidebarcolor6"></div>
                    </div>
                    <div class="col">
                        <div class="indigator sidebarcolor7" id="sidebarcolor7"></div>
                    </div>
                    <div class="col">
                        <div class="indigator sidebarcolor8" id="sidebarcolor8"></div>
                    </div>
                </div>
            </div>
        </div>
      </div>
      <router-view></router-view>
    </div>
</template>

<script>
export default {
    name:"Navigator",
    data() {
        return {
        navbarOpacity: 1,  // 初始完全不透明
        timer: null,  // 用于存储倒计时的定时器
        };
    },
    mounted() {
        // 页面加载时开始倒计时
        this.startOpacityCountdown();
    },
    methods: {
        // 导航跳转方法
        navigateTo(path) {
            // 使用 Vue Router 的 push 方法进行页面跳转
            this.$router.push(path);
        },
        // 鼠标进入时恢复完全不透明
        handleMouseEnter() {
            if (this.timer) {
                clearTimeout(this.timer);  // 清除之前的定时器
            }
            this.navbarOpacity = 1;  // 恢复完全不透明
        },
        // 鼠标离开时开始倒计时
        handleMouseLeave() {
            this.startOpacityCountdown();
        },
        startOpacityCountdown() {
            this.timer = setTimeout(() => {
                this.navbarOpacity = 0.3;
            }, 1000);
        },
    }
}
</script>

<style scoped>
.navbar {
  position: fixed;
  top: 10px; /* 离页面顶部 20px */
  left: 50%;
  transform: translateX(-50%); /* 居中 */
  background-color: rgba(255, 255, 255, 0.9); /* 半透明背景 */
  padding: 0px 20px; /* 上下内边距 10px，左右内边距 20px */
  border-radius: 20px; /* 圆角矩形 */
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); /* 阴影效果 */
  z-index: 9999; /* 确保显示在最顶层 */
  max-width: 80%; /* 防止过宽 */
  min-width: 300px; /* 防止过窄 */
  transition: opacity 0.5s ease; /* 透明度变化的平滑过渡 */
}

.navbar-menu {
  display: flex; /* 让菜单项水平排列 */
  justify-content: space-around; /* 平均分布每个菜单项 */
}

.el-menu-item {
  font-size: 16px;
  font-weight: 500;
  padding: 0 10px;
}

.el-menu-item:hover {
  background-color: rgba(0, 0, 0, 0.05); /* 悬浮时的背景色 */
}

/* 左侧图标样式 */
.navbar-left {
  flex: 1;
  margin-right: 20px;
}

.navbar-logo {
  height: 30px; /* 使图标的高度与导航栏一致 */
}

/* 中间菜单项居中 */
.navbar-menu {
  flex: 8;
  text-align: center;
}
</style>