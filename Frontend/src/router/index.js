import Vue from 'vue'
import Router from 'vue-router'
import index from '@/components/Navigator'
import collect from '@/views/CollectPage'
import anomalyDetail from '@/views/AnomalyDetailPage'
import anomaly from '@/views/AnomalyDectectPage'
import portrait from '@/views/PortraitPage'
import setting from '@/views/SettingPage'
import serviceCls from '@/views/ServiceClsPage'
import landing from '@/views/LandingPage.vue';


Vue.use(Router)

let router = new Router({
  routes: [
    {
      path: '/',
      redirect: '/landing'
    },
    {
      path: '/landing',
      component: landing, index
    },
    {
      path:'/index',
      component:index,
      meta:{
        requireAuth:true
      },
      redirect:'/collect',
      children:[
        {
          path:'/collect',  // 流量采集页面路由
          component:collect,
          meta:{
            requireAuth:true
          },
          // name:'navContent'
        },
        {
          path:'/serviceCls',  // 业务分类页面路由
          component:serviceCls,
          meta:{
            requireAuth:true
          },
          // name:'navContent'
        },
        {
          path:'/anomaly',  // 异常检测页面路由
          component:anomaly,
          meta:{
            requireAuth:true
          },
          // name:'navContent'
        },
        {
          path:'/portrait', // 用户画像页面路由
          component:portrait,
          meta:{
            requireAuth:true
          },
          // name:'navContent'
        },
        {
          path:'/setting',
          component:setting,
          meta:{
            requireAuth:true
          },
        }
      ]
    },
    {
      path:'/anomaly/detail/:anomalyIp/:anomalyTs',  // 数据分析页面路由
      // path:'/anomaly/detail',
      component:anomalyDetail,
      meta:{
        requireAuth:true
      },
    }
  ]
})

export default router
