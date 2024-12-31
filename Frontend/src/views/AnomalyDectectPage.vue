<template>
    <div>
    <transition name="fade">
      <router-view />
    <div class="page-wrapper">
	    <div class="page-content">
            <div class="card">
                <div class="card-body">
                    <div class="page-breadcrumb d-none d-sm-flex align-items-center mb-3">
                        <div class="logo-container ps-3">
                            <img src="../assets/images/icon.png" alt="Logo" class="logo-img" style="width: 30px; height: auto;" />
                        </div>
                        <div class="text-uppercase pe-3 ps-2" style="font-size: 1.2rem;">异常检测</div>
                        <div class="ms-auto" style="margin-right: 50px;">
                            <!-- 开始检测按钮 -->
                            <button 
                                v-if="!detectingFlag" 
                                class="btn btn-detect shadow-lg" 
                                @click="startAnomalDectect">
                                <i class="fas fa-play me-2"></i>开始检测&nbsp;
                            </button>

                            <!-- 检测中按钮 -->
                            <button 
                                v-else 
                                class="btn btn-detecting shadow-lg px-5 radius-30" 
                                type="button" 
                                disabled>
                                <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>检测中...&nbsp;
                            </button>

                            <!-- 结束按钮 -->
                            <button 
                                v-if="detectingFlag && !stopping" 
                                class="btn btn-stop shadow-lg ms-2" 
                                @click="stopAnomalDectect">
                                <i class="fas fa-stop me-2"></i>结束&nbsp;
                            </button>

                            <!-- 结束中按钮 -->
                            <button 
                                v-if="stopping" 
                                class="btn btn-stop shadow-lg ms-2" 
                                disabled>
                                <i class="fas fa-spinner fa-spin me-2"></i>结束中&nbsp;
                            </button>
                        </div>
                    </div>

                    <div v-if="detectingFlag || ischart">                  
                        <hr style="margin-left: 16px;"/>
                        <!-- <h4 class="mb-0 text-uppercase" style="text-align: left; font-size: 20px; margin-left: 16px;" >动态监测异常</h4> -->
                        <div class="container-fluid py-2">
                            <div class="row g-3">
                                <!-- Line Chart -->
                                <div class="col-md-8">
                                    <div class="card h-100" style="box-shadow: 0 4px 8px rgba(44, 62, 80, 0.5); border: none; border-radius: 15px;">
                                        <div class="card-body p-2 bg-light rounded">
                                            <div ref="charts" class="chart chart--line w-100" style="height: 360px; width: 10px"></div>
                                        </div>
                                    </div>
                                </div>
                                <!-- Pie Chart -->
                                <div class="col-md-4">
                                    <div class="card h-100" style="box-shadow: 0 4px 8px rgba(44, 62, 80, 0.5); border: none; border-radius: 15px;">
                                        <div class="card-body p-2 bg-light rounded">
                                            <div ref="pieChart" class="chart chart--pie w-100" style="height: 360px;"></div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <hr v-if="!isDashed" style="margin-left: 16px;" />
                    <hr v-else style="border: none; border-top: 2px dashed #ccc; margin: 20px 0; margin-left: 12px;" />

                    <h4 class="mb-0 text-uppercase" style="font-size: 20px; margin-left: 16px;">异常检测历史</h4>
                    
                    <div style="height: 20px;"></div>
                    <div class="table-responsive" style="width: calc(100% - 20px); padding-right: 20px;">
                        <table id="example2" ref="anomalTable" class="table table-bordered" data-locale="zh-CN" 
                            style="background-color: #fff; margin-top: 40px; margin-left: 16px; margin-right: 20px; border: 0.5px solid #dee2e6; border-collapse: collapse;">
                            <thead class="table-header">
                                <tr class="text-muted fs-5" track-by="id" style="border: 0.5px solid #dee2e6;">
                                    <th style="border: 0.5px solid #dee2e6;">&nbsp;&nbsp;&nbsp;异常检测时间</th>
                                    <th style="border: 0.5px solid #dee2e6;">&nbsp;&nbsp;&nbsp;异常ip</th>
                                    <th style="border: 0.5px solid #dee2e6;">&nbsp;&nbsp;&nbsp;异常类型</th>
                                    <th style="border: 0.5px solid #dee2e6;">&nbsp;&nbsp;&nbsp;异常检测报告</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="item in items" class="fs-6" style="border: 0.5px solid #dee2e6;">
                                    <td style="border: 0.5px solid #dee2e6;">{{item.timeStamp}}</td>
                                    <td style="border: 0.5px solid #dee2e6;">{{item.targetIP}}</td>
                                    <td style="border: 0.5px solid #dee2e6;"><span 
                                        v-for="type in [...new Set(item.anomalyType)]" 
                                        :key="type"
                                        :style="{ 
                                            backgroundColor: anomalyColors[type] || '#ffffff', 
                                            padding: '5px 10px', 
                                            borderRadius: '5px', 
                                            marginRight: '5px',
                                            marginBottom: '5px',
                                            display: 'inline-block',
                                            color: '#000'
                                        }"
                                        >
                                        {{ type }}
                                        </span>
                                    </td>
                                    <td style="border: 0.5px solid #dee2e6; display: flex; justify-content: center; align-items: center;">
                                        <div>
                                          <!-- 按钮触发显示新界面 -->
                                          <button 
                                            type="button" 
                                            class="btn-icon" 
                                            style="border: none; background: none; display: flex; align-items: center;" 
                                            @click="showEmbeddedView(item.targetIP, item.timeStamp)">
                                            <img 
                                              src="../assets/images/report.png" 
                                              alt="Share Icon" 
                                              class="btn-image"
                                              style="width: 20px; height: auto;" 
                                            />
                                            <span style="margin-left: 8px; font-size: 18px; color: #007bff; cursor: pointer;">查看</span>
                                          </button>

                                          <!-- 嵌入显示的界面 -->
                                          <div v-if="embeddedViewVisible" class="overlay">
                                            <div class="overlay-content">
                                              <button 
                                                class="close-button" 
                                                @click="hideEmbeddedView" 
                                                style="position: absolute; top: 5px; right: 20px; font-size: 30px; width: 40px; height: 40px; line-height: 40px; border: none;">
                                                ×
                                              </button>
                                              <iframe
                                                :src="`http://【Your_ip_addr_main】/#/anomaly/detail/${currentTargetIP}/${currentTimeStamp}`"
                                                frameborder="0"
                                                style="width: 100%; height: 100%;"
                                              ></iframe>
                                            </div>
                                          </div>
                                        </div>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>

        <div class="modal" id="exampleLargeModal" tabindex="-1" :style="{'display': (showDetailDialogFlag==true?'block':'none')}">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title"></h5>
                            <button type="button" class="btn-close" @click="closeExitDialog"></button>
                        </div>
                        <div class="modal-body m-auto">

                            <div v-if="loaddingFlag" class="spinner-border" style="width: 3rem; height: 3rem;" role="status"> 
                                <span class="visually-hidden">Loading...</span>
                            </div>

                            <div v-else>
                                <div id="chartDetail" width="685" height="320"
                                                    style="display: block; width: 685px; height: 320px;"
                                                    class="chartjs-render-monitor">
                                </div>
                            </div>
                            
                            <!-- <div id = 'chartDetail'>

                            </div> -->
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" @click="closeExitDialog">确定</button>
                        </div>
                    </div>
                </div>
            </div>
            <BgCover :show-cover="showDetailDialogFlag"></BgCover>
    </div>
    </transition>
    </div>
</template>

<script>

import BgCover from '../components/BgCover.vue'
import * as echarts from 'echarts';
import '../assets/bootstrap-5.1.3-dist/css/bootstrap.min.css'
import '../assets/css/bootstrap-table.css'

    export default{
        props: ['item'], // 接收 item 对象
        data(){
            return{
                currentTargetIP: null,
                currentTimeStamp: null,
                embeddedViewVisible: false, // 控制嵌入视图显示状态
                embeddedViewUrl: "", // 嵌入视图的 URL
                fullscreenDialogVisible: false, // 控制弹窗显示
                dialogUrl: '', // 弹窗中 iframe 的地址
                anomalyColors: {
                "流量报文数异常": "#ffcccc", // 浅红色
                "流量数据量异常": "#cce5ff", // 浅蓝色
                "流量时间异常": "#d4edda", // 浅绿色
                "流业务类型异常": "#f8d7da", // 浅粉色
                "业务流分布异常": "#fff3cd", // 浅黄色
                "正常": "#e2e3e5" // 浅灰色
                },
                showDetailDialogFlag: false,
                loaddingFlag:true,
                detectingFlag:false,
                isDashed: false, // 记录是否切换为虚线
                items:[],
                dynamicImageUrl: '', // 不再使用GIF图像，而是动态更新数据
                list: [], // 存储实时数据
                timer: null, // 定时器
                myChart: null, // ECharts 实例
                stopping: false,
                ischart:false,
                ipData: [], // 存储 detect_ipimage.csv 中的 ip 数据
                anomalyData: [], // 存储 detect_anomalyrecord.csv 中的 targetIP 数据
                shownIPs: new Set(), // 初始化 shownIPs 为 Set 类型
                ip:0,
                pieChart: null,
                anomalyTypeMapping: {
            "流量报文数异常": "abnormal0",
            "流量数据量异常": "abnormal1",
            "流量时间异常": "abnormal2",
            "流业务类型异常": "abnormal3",
            "业务流分布异常": "abnormal4"
            },
                typeCount: {
                normal: 0,
                abnormal0: 0,
                abnormal1: 0,
                abnormal2: 0,
                abnormal3: 0,
                abnormal4: 0
            },
            }
        },
        watch: {
          detectingFlag(newValue) {
            // 如果 detectingFlag 变为 true，就固定 isDashed 为 true
            if (newValue) {
              this.isDashed = true;
            }
          }
        },
        mounted(){
            this.initTable()
            this.getData()
            this.$nextTick(() => {
                this.initPieChart(); // 初始化饼状图
            });

        },
        props: ['data'],
        created() {
            this.initData();
            this.initPieChart();
        },
        components: { BgCover },
        methods: {
            showEmbeddedView(targetIP, timeStamp) {
              this.currentTargetIP = targetIP;
              this.currentTimeStamp = timeStamp;
              this.embeddedViewVisible = true;
            },
            hideEmbeddedView() {
              this.embeddedViewVisible = false;
              this.currentTargetIP = null;
              this.currentTimeStamp = null;
            },
            handleSmoothTransition(ip, timestamp) {
              this.openFullscreenDialog(ip, timestamp); // 打开弹窗逻辑
              setTimeout(() => {
                this.$router.push(`/anomaly/detail/${ip}/${timestamp}`);
              }, 300); // 延迟跳转，等待动画完成
            },
            openFullscreenDialog(ip, timestamp) {
                this.dialogUrl = `http://【Your_ip_addr_main】/#/anomaly/detail/${encodeURIComponent(ip)}/${encodeURIComponent(timestamp)}`;
                this.fullscreenDialogVisible = true;
            },
            closeFullscreenDialog() {
                this.fullscreenDialogVisible = false;
                this.dialogUrl = ''; // 清空地址
            },
            initTable() {
                console.log($('#example2'))
                var table = $('#example2').DataTable();
                var dtOption = {
                    initComplete: function () {
                        $('.dataTables_paginate').css('margin-right', '-16px'); // 向右移动分页部分
                    },
                    lengthChange: true,
                    order:[[0,'desc']],
                    buttons: [
                        {
                            extend: 'csv',
                            filename: 'test',
                            charset: 'UTF-8',
                            bom: true,
                            text:'导出csv'
                        },
                        {
                            extend: 'excel',
                            filename: 'test',
                            charset: 'UTF-8',
                            bom: true,
                            text:'导出excel'
                        },
                    ],
                    language:{
                        "processing": "处理中...",
                        "lengthMenu": "&nbsp;&nbsp;&nbsp;显示 _MENU_ 项结果",
                        "zeroRecords": "没有匹配结果",
                        "info": "&nbsp;&nbsp;&nbsp;显示第 _START_ 至 _END_ 项结果，共 _TOTAL_ 项",
                        "infoEmpty": "显示第 0 至 0 项结果，共 0 项",
                        "infoFiltered": "(由 _MAX_ 项结果过滤)",
                        "infoPostFix": "",
                        "search": "搜索:",
                        "searchPlaceholder": "搜索...",
                        "url": "",
                        "emptyTable": "表中数据为空",
                        "loadingRecords": "载入中...",
                        "infoThousands": ",",
                        "paginate": {
                            "first": "首页",
                            "previous": "上页",
                            "next": "下页",
                            "last": "末页"
                        },
                        "aria": {
                            "paginate": {
                                "first": "首页",
                                "previous": "上页",
                                "next": "下页",
                                "last": "末页"
                            },
                            "sortAscending": "以升序排列此列",
                            "sortDescending": "以降序排列此列"
                        },
                        "thousands": "."
                    }
                } 
                table.destroy()
                this.$nextTick(()=>{
                    $('#example2').DataTable(dtOption)
                    // table.buttons().container().appendTo( '#example2_wrapper .col-md-6:eq(0)' );
                })
            },

            getData(){
                this.$axios.get('/nmas/detect/showAnomaly').then(res => {
                    if (res.data.status == 'success') {
                        this.items = res.data.result
                        this.initTable()
                    } else {
                        console.log(res)
                        alert('服务器发生错误')
                    }

                }, res => {
                    console.log(res)
                    alert('服务器错误')
                })
            },

            startAnomalDectect(){
                this.detectingFlag = true
                this.dynamicImageUrl = ''; // 动态图像的URL更新
                this.ischart = true;  // 设置 ischart 为 true，确保渲染 ECharts 容器
                this.$nextTick(() => {
                    this.echartsInit();
                    this.initPieChart(); // 初始化饼状图
                });

                this.$axios.get('/nmas/detect/anomalyDetect').then(res=>{
                    if(res.data.status == 'success'){
                        if(res.data.anomaly_count == 0){
                            alert('未检测出新异常')
                        }else{
                            alert('已检测出新异常记录')//alert('检测出'+res.data.anomaly_count+'条新异常记录')
                        }
                        this.getData()
                        this.detectingFlag = false
                    }else{
                        alert("异常检测失败，请重试")
                        this.detectingFlag = false
                    }
                },res=>{
                    console.log(res)
                    alert('异常检测失败，请重试')
                    this.detectingFlag = false
                })
            },
            stopAnomalDectect() {
                this.stopping = true; // 设置停止状态
                clearInterval(this.timer); // 停止定时器

                this.$axios.get('/nmas/detect/stopAnomalyDetect').then(res => {
                    if (res.data.status === 'success') {
                        this.stopping = false; // 停止状态取消
                        this.detectingFlag = false; // 停止检测标志
                        alert('异常检测已停止');

                        // 调用 getData() 更新异常数据量显示
                        this.getData(); 
                    } else {
                        alert("停止异常检测失败，请重试");
                        this.stopping = false;
                    }
                }).catch(error => {
                    console.log(error);
                    alert('停止异常检测失败，请重试');
                    this.stopping = false;
                });

                // 保留图像内容，设置最终状态显示数据
                if (this.myChart) {
                    this.myChart.setOption({
                        series: [{
                            data: this.list.map(item => item.value[1]) // 停止更新后的最终数据
                        }]
                    });
                }
            },
            echartsInit() {
                const chartsElement = this.$refs.charts;
                if (!chartsElement) {
                    console.error("ECharts 容器元素未找到");
                    return;
                }

                this.myChart = echarts.init(chartsElement);
                const option = {
                    title: { 
                        text: '异常类型动态检测', 
                        left: 'center',
                        top: 'top',
                        textStyle: {
                            fontSize: 16,
                            fontWeight: 'bold'
                        }
                    },
                    tooltip: {
                        trigger: 'axis',
                        axisPointer: { animation: false },
                    },
                    xAxis: {
                        type: 'category',
                        data: [],
                    },
                    yAxis: {
                        type: 'value',
                        name: 'IP正常/异常',
                        nameTextStyle: {
                            fontSize: 12, 
                            fontWeight: 'bold',  
                            color: '#000', 
                        }
                    },
                    series: [{
                        name: '实时流量',
                        type: 'line',
                        showSymbol: false,
                        data: [],
                        label: {
                            show: true,
                            position: 'top',
                            formatter: (params) => params.data.ip,
                        }
                    }],
                    visualMap: {
                        show: false,
                        pieces: [
                            { gt: 0, lte: 1, color: '#33CC33' },
                            { lt: 0, color: '#CC3300' },
                            { gte: 1, color: '#CC3300' },
                        ],
                    },
                    graphic: [
                        {
                            type: 'text',
                            left: '90%',
                            bottom: '10%',
                            style: {
                                text: 'IP数量',
                                fontSize: 12,
                                fontWeight: 'bold',
                                fill: '#000',
                            },
                        },
                    ],
                };
                // 更新图表配置
                this.myChart.setOption(option);

                // 启动定时器进行数据更新
                this.initTimer();
            },

            initData() {
                this.ipList = [];
                this.anomalyTypeMap = {}; // 确保 anomalyTypeMap 存在
                // 初始化 typeCount 为0
                this.typeCount = { 
                    normal: 0, 
                    abnormal0: 0, 
                    abnormal1: 0, 
                    abnormal2: 0, 
                    abnormal3: 0, 
                    abnormal4: 0 
                };

                this.$axios.get('/nmas/detect/showAnomalyEchart', {})
                .then(res => {
                    const response = res.data;
                    if (response.status === 'success' && response.result) {
                        const resultList = response.result;
                        resultList.forEach(item => {
                            const ip = item.targetIP;
                            this.ipList.push(ip);
                            this.anomalyTypeMap[ip] = {
                                anomalyType: item.anomalyType,
                                value: item.value
                            };
                        });
                        // 不再在这里更新 typeCount
                        this.initTimer(); // 初始化定时器
                    } else {
                        console.error('数据加载失败:', response.err || '未获取到结果数据');
                    }
                })
                .catch(error => {
                    console.error('请求后端数据失败:', error);
                });
            },

            compareIP(ip) {
                // 检查 anomalyTypeMap 是否包含该 IP
                const anomalyData = this.anomalyTypeMap[ip] || { value: 1, anomalyType: "正常" }; // 默认值
                const value = anomalyData.value;
                const anomalyType = anomalyData.anomalyType;

                // 拆分异常类型并统计
                const anomalies = anomalyType.split(' '); // 假设异常类型以空格分隔
                anomalies.forEach(anomaly => {
                    const typeKey = this.anomalyTypeMapping[anomaly.trim()] || "normal";
                    // 确保在统计之前 typeCount 对象中已经初始化了相应的键
                    if (!this.typeCount.hasOwnProperty(typeKey)) {
                        this.typeCount[typeKey] = 0;
                    }
                    this.typeCount[typeKey] += 1;
                });

                // 更新饼状图
                this.updatePieChart();

                // 当前时间标签
                const current = new Date();
                const label = `${current.getFullYear()}-${String(current.getMonth() + 1).padStart(2, '0')}-${String(current.getDate()).padStart(2, '0')} ${String(current.getHours()).padStart(2, '0')}:${String(current.getMinutes()).padStart(2, '0')}:${String(current.getSeconds()).padStart(2, '0')}`;

                // 打印以确认数据内容
                console.log(`IP: ${ip}, Value: ${value}, AnomalyType: ${anomalyType}`);

                return {
                    value: [ip, value, label, anomalyType],
                };
            },
            initTimer() {
                this.timer = setInterval(() => {
                    if (this.detectingFlag) { // 仅当检测未停止时更新数据
                        const nextIP = this.getNextIP();
                        if (nextIP) {
                            this.list.push(this.compareIP(nextIP)); // 每次获取下一个 IP 并进行对比
                            this.shownIPs.add(nextIP); // 记录已显示的IP

                            this.myChart.setOption({
                                xAxis: {
                                    type: 'category',
                                    min: 0,  // 固定x轴的0位置
                                    max: this.list.length, // x轴最大值动态增加
                                    data: Array.from({ length: this.list.length }, (_, i) => i), // x轴显示当前IP数量
                                    axisLabel: {
                                        interval: (index, value) => {
                                            if (this.list.length > 1000) {
                                                return value % 500 === 0 && (value % 1000 === 0 || value % 1500 === 0);
                                            } else if (this.list.length > 100) {
                                                return value % 100 === 0;
                                            } else if (this.list.length > 50) {
                                                return value % 50 === 0;
                                            } else {
                                                return value % 10 === 0;
                                            }
                                        }
                                    }
                                },
                                series: [{
                                    type: 'line',
                                    data: this.list.map(item => ({
                                        value: item.value[1], // y 轴数值
                                        itemStyle: {
                                            color: item.value[1] > 0 ? 'green' : 'red' // 正值为绿色，负值为红色
                                        }
                                    })),
                                    lineStyle: {
                                        width: 2
                                    }
                                }],
                                tooltip: {
                                    trigger: 'axis',
                                    formatter: (params) => {
                                        const dataPoint = this.list[params[0].dataIndex];
                                        const ip = dataPoint.value[0];
                                        const value = dataPoint.value[1];
                                        const time = dataPoint.value[2];
                                        const anomalyType = dataPoint.value[3];
                                        const status = value === 1 ? '正常' : `异常`;
                                        return `时间: ${time}<br>IP: ${ip}<br>状态: ${status}<br>异常类型: ${anomalyType}`;
                                    }
                                },
                                animationDurationUpdate: 0,  // 禁用动画更新
                                animationEasingUpdate: 'linear',  // 设置线性过渡
                            });
                        }
                        this.updatePieChart();
                    }
                }, 300);
            },
            getNextIP() {
                // 获取未展示过的IP
                const unseenIP = this.ipList.find(ip => !this.shownIPs.has(ip));
                if (unseenIP) {
                    return unseenIP;
                }
                return null; // 如果没有新的IP，则返回 null
            },
            updateChart() {
                if (this.myChart) {
                    this.myChart.setOption(this.option);
                }
            },
            // 初始化饼状图
            initPieChart() {
                const pieChartElement = this.$refs.pieChart;
                if (!pieChartElement) {
                    console.error("饼状图容器未找到");
                    return;
                }
                this.pieChart = echarts.init(pieChartElement);

                const option = {
                    title: { 
                        text: '异常类型占比分布', 
                        left: 'center',  // 标题水平居中
                        top: 'top',  // 标题在饼图上方
                        textStyle: {
                            fontSize: 16,  // 调整字体大小
                            fontWeight: 'bold'
                        }
                    },
                    tooltip: { trigger: 'item', formatter: '{b} : {c} ({d}%)' },
                    legend: {
                        orient: 'vertical',       // 垂直布局
                        left: 'left',             // 图例靠左
                        left: 5,
                        bottom: '5%',            // 图例距离底部 5%
                        data: ['正常', '流量报文数异常', '流量数据量异常', '流量时间异常', '流业务类型异常', '业务流分布异常'],
                        textStyle: {
                            fontSize: 12,         // 图例文字大小
                            color: '#333'         // 图例文字颜色
                        }
                    },
                    series: [{
                        name: '异常类型',
                        type: 'pie',
                        animation: false,
                        radius: ['40%', '70%'],//设置扇形图格式
                        itemStyle: {
                            borderRadius: 10,
                            borderColor: '#fff',
                            borderWidth: 2
                        },
                        center: ['60%', '50%'],   // 饼图居中
                        animation: false,
                        data: [
                            { value: this.typeCount.normal, name: '正常'}, 
                            { value: this.typeCount.abnormal0, name: '流量报文数异常'}, 
                            { value: this.typeCount.abnormal1, name: '流量数据量异常'}, 
                            { value: this.typeCount.abnormal2, name: '流量时间异常'}, 
                            { value: this.typeCount.abnormal3, name: '流业务类型异常'}, 
                            { value: this.typeCount.abnormal4, name: '业务流分布异常'} 
                        ],
                        label: {
                                show: false,
                                position: 'center'
                            // position: 'right', // 强制文字显示在左侧
                            // align: 'right', // 对齐方式，保证文字靠右对齐
                            // formatter: '{b}',  // 仅显示异常类型
                            // position: 'outside'  // 将标签移到饼图外
                        },
                        labelLine: {
                            show:false,
                            // show: true,  // 显示标签的指示线
                            // length: 20,  // 调整指示线的长度
                            // length2: 20  // 调整指示线的延伸长度
                        },
                        emphasis: {
                            label: {
                            show: true,
                            fontSize: 16,
                            fontWeight: 'bold'
                            },
                            itemStyle: {
                                shadowBlur: 10,
                                shadowOffsetX: 0,
                                shadowColor: 'rgba(0, 0, 0, 0.5)'
                            }
                        }
                    }]
                };

                this.pieChart.setOption(option);
            },

            // 更新饼状图数据
            updatePieChart() {
                if (this.pieChart) {
                    const newSeriesData = [
                        { value: this.typeCount.normal, name: '正常'},
                        { value: this.typeCount.abnormal0, name: '流量报文数异常'},
                        { value: this.typeCount.abnormal1, name: '流量数据量异常'},
                        { value: this.typeCount.abnormal2, name: '流量时间异常'},
                        { value: this.typeCount.abnormal3, name: '流业务类型异常'},
                        { value: this.typeCount.abnormal4+0.01, name: '业务流分布异常'}
                    ];
                    this.pieChart.setOption({
                        series: [{
                            data: newSeriesData
                        }]
                    });
                }
            },
            toDetail(anomalId,anomalType){
                this.showDetailDialogFlag = true
                setTimeout(() => {
                    if(anomalType == '设备流量规模异常'){
                        this.loaddingFlag = false
                        var xLableList = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '60', '61', '62', '63', '64', '65', '66', '67', '68', '69', '70', '71', '72', '73', '74', '75', '76', '77', '78', '79', '80', '81', '82', '83', '84', '85', '86', '87', '88', '89', '90', '91', '92', '93', '94', '95', '96', '97', '98', '99', '100', '101', '102', '103', '104', '105', '106', '107', '108', '109', '110', '111', '112', '113', '114', '115', '116', '117', '118', '119', '120', '121', '122', '123', '124', '125', '126', '127', '128', '129', '130', '131', '132', '133', '134', '135', '136', '137', '138', '139', '140', '141', '142', '143', '144', '145', '146', '147', '148', '149', '150', '151', '152', '153', '154', '155', '156', '157', '158', '159', '160', '161', '162', '163', '164', '165', '166', '167', '168', '169', '170', '171', '172', '173', '174', '175', '176', '177', '178', '179', '180', '181', '182', '183', '184', '185', '186', '187', '188', '189', '190', '191', '192', '193', '194', '195', '196', '197', '198', '199', '200']
                        var lossList = [1.4512, 1.2206, 1.1962, 1.1761, 1.1622, 1.1533, 1.1446, 1.136, 1.1297, 1.1233, 1.1201, 1.1168, 1.1141, 1.1113, 1.1093, 1.1088, 1.1074, 1.1061, 1.1065, 1.1042, 1.1028, 1.1014, 1.1001, 1.0992, 1.0985, 1.0982, 1.098, 1.0984, 1.097, 1.0974, 1.0969, 1.0965, 1.096, 1.0961, 1.095, 1.0957, 1.0958, 1.0966, 1.0953, 1.095, 1.0951, 1.0945, 1.0948, 1.0951, 1.0958, 1.0946, 1.0945, 1.0939, 1.0944, 1.0931, 1.093, 1.0913, 1.0872, 1.0868, 1.087, 1.0871, 1.0869, 1.0871, 1.0876, 1.0872, 1.0869, 1.0866, 1.0856, 1.0853, 1.0851, 1.0853, 1.0849, 1.0849, 1.085, 1.0857, 1.0844, 1.0842, 1.084, 1.0838, 1.0835, 1.0836, 1.0832, 1.0837, 1.0831, 1.0824, 1.0825, 1.0823, 1.0823, 1.082, 1.0822, 1.082, 1.0822, 1.082, 1.0818, 1.082, 1.0821, 1.0823, 1.0816, 1.0821, 1.0815, 1.0813, 1.0817, 1.0816, 1.0817, 1.0816, 1.0813, 1.0816, 1.0815, 1.0814, 1.0817, 1.0815, 1.0812, 1.0817, 1.0814, 1.0815, 1.0813, 1.0815, 1.0814, 1.0808, 1.0812, 1.0811, 1.0813, 1.0809, 1.081, 1.081, 1.081, 1.0814, 1.0807, 1.081, 1.0809, 1.0811, 1.0811, 1.0814, 1.0809, 1.081, 1.0813, 1.0809, 1.081, 1.0809, 1.0814, 1.0807, 1.0813, 1.0809, 1.0809, 1.081, 1.081, 1.0807, 1.0812, 1.0809, 1.0811, 1.0809, 1.081, 1.0811, 1.0809, 1.081, 1.0809, 1.0808, 1.0809, 1.0811, 1.081, 1.0806, 1.081, 1.0809, 1.0814, 1.0808, 1.0809, 1.0811, 1.0811, 1.0812, 1.0809, 1.0809, 1.0808, 1.0809, 1.0812, 1.0807, 1.0807, 1.0807, 1.0808, 1.0809, 1.0808, 1.0806, 1.0808, 1.0808, 1.081, 1.0809, 1.0807, 1.0807, 1.0809, 1.0808, 1.0808, 1.0809, 1.081, 1.0806, 1.0806, 1.0807, 1.0811, 1.0808, 1.0808, 1.0808, 1.0808, 1.0807, 1.0807, 1.0808, 1.0806, 1.0811]
                        var option = {
                            title: {
                                text: '设备流量规模异常',
                            },
                            tooltip: {
                                trigger: 'axis'
                            },
                            xAxis: {
                                type: "category",
                                name: "epoch",
                                boundaryGap: false,
                                data: xLableList,
                            },
                            yAxis: {
                                type: "value",
                                name: "loss",
                            },
                            series: [{
                                name: "模型训练loss",
                                type: "line",
                                stack: "loss",
                                data: lossList,
                                markPoint:{
                                    data:[{
                                        coord:['10',1.1233],
                                        symbol:'pin',
                                        symbolSize:50,
                                        animation:true,
                                        label:{
                                            show:true,
                                            color:'#000'
                                        },
                                        itemStyle:{color:'#f00'}
                                    }]
                                }
                            }],
                        }

                        this.$nextTick(()=>{
                            this.drawLine('chartDetail',option)
                        })
                    }else{
                        this.loaddingFlag = false
                        var data = {
                            legendData: ['chat', 'p2p', 'video', 'text', 'game'],
                            data: [
                                { value: 20, name: 'chat' },
                                { value: 20, name: 'p2p' },
                                { value: 20, name: 'video' },
                                { value: 20, name: 'text' },
                                { value: 20, name: 'game' }
                            ]
                        }

                        var option = {
                            title: {
                                text: '业务标签异常',
                            },
                            //鼠标划过时饼状图上显示的数据
                            tooltip: {
                                trigger: 'item',
                                triggerOn: "mousemove",
                                axisPointer: {
                                    // 坐标轴指示器，坐标轴触发有效
                                    type: 'shadow', // 默认为直线，可选为：'line' | 'shadow'
                                },
                                showContent: true,                       //是否显示提示框浮层
                                formatter: '{a}<br/>{b}:{c} ({d}%)'
                            },
                            //图例
                            legend: {
                                bottom: 10,//控制图例出现的距离  默认左上角
                                left: 'center',//控制图例的位置
                                // itemWidth: 16,//图例颜色块的宽度和高度
                                // itemHeight: 12,
                                textStyle: {//图例中文字的样式
                                    color: '#000',
                                    fontSize: 16
                                },
                                data: data.legendData//图例上显示的饼图各模块上的名字
                            },
                            series: [{
                                type: 'pie',             //echarts图的类型   pie代表饼图
                                radius: ['50%', '70%'],           //饼图中饼状部分的大小所占整个父元素的百分比
                                center: ['50%', '50%'],
                                data: data.data,
                                itemStyle: {
                                    normal: {
                                        label: {
                                            show: true, //饼图上是否出现标注文字 标注各模块代表什么  默认是true
                                        },
                                        labelLine: {
                                            show: true, //官网demo里外部标注上的小细线的显示隐藏    默认显示
                                        }
                                    }
                                }
                            }]
                        }

                        this.$nextTick(()=>{
                            this.drawPie('chartDetail',option)
                        })

                    }
                }, 1000);
                // console.log(anomalId)
            },

            closeExitDialog(){
                this.showDetailDialogFlag = false
                this.loaddingFlag = true
            },

            drawPie(id, option) {
            let chart = this.$echarts.init(document.getElementById(id), "roma");
            chart.setOption(option)
            },

            drawLine(id, option) {
                let chart = this.$echarts.init(document.getElementById(id));
                chart.setOption(option)
            }
        }
        
    }
</script>

<style scoped>
.overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.overlay-content {
  position: relative;
  background: #fff;
  width: 90%;
  height: 57%;
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
  overflow: hidden;
}

.close-button {
  position: absolute;
  top: 10px;
  right: 15px;
  background: #154ec1;
  color: white;
  border: none;
  border-radius: 0%;
  width: 30px;
  height: 30px;
  font-size: 18px;
  line-height: 30px;
  text-align: center;
  cursor: pointer;
}

.close-button:hover {
  background: #ff4040;
}

/* 嵌入显示视图的样式 */
.embedded-view {
  position: relative;
  width: 100%;
  margin-top: 20px;
  border: 1px solid #ccc;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  overflow: hidden;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease; /* 控制动画时长与效果 */
}

.fade-enter, .fade-leave-to {
  opacity: 0; /* 动画开始或结束时的透明度 */
}

.fullscreen-dialog {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background-color: rgba(0, 0, 0, 0.5); /* 半透明背景 */
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1050;
}

.dialog-content {
    background: #fff;
    width: 90%; /* 占屏幕宽度的 90% */
    height: 90%; /* 占屏幕高度的 90% */
    border-radius: 15px;
    overflow: hidden;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.dialog-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px;
    border-bottom: 1px solid #ddd;
}

.dialog-header h5 {
    margin: 0;
}

.dialog-body {
    height: calc(100% - 60px); /* 减去 header 的高度 */
    overflow: hidden;
}
/* 开始检测按钮 */
.btn-detect {
    background: linear-gradient(135deg, #0d6efd, #6da5f9); /* 绿色渐变 */
    color: #fff;
    font-weight: bold;
    padding: 10px 20px;
    border: none;
    border-radius: 10px;
    transition: all 0.3s ease;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.btn-detect:hover {
    background: linear-gradient(135deg, #0d6efd, #6da5f9);
    box-shadow: 0 6px 10px rgba(0, 0, 0, 0.2);
    transform: translateY(-2px);
}

.btn-detect:active {
    background: linear-gradient(135deg, #0d6efd, #6da5f9);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    transform: translateY(1px);
}

/* 检测中按钮 */
.btn-detecting {
    background: linear-gradient(135deg, #0d6efd, #6da5f9); /* 橙色渐变 */
    color: #fff;
    font-weight: bold;
    border: none;
    padding: 12px 20px;
    border-radius: 10px;
    cursor: not-allowed;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

/* 结束按钮 */
.btn-stop {
    background: linear-gradient(135deg, #dc3545, #d9606c); /* 红色渐变 */
    color: #fff;
    font-weight: bold;
    padding: 10px 20px;
    border: none;
    border-radius: 10px;
    transition: all 0.3s ease;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.btn-stop:hover {
    background: linear-gradient(135deg, #dc3545, #d9606c);
    box-shadow: 0 6px 10px rgba(0, 0, 0, 0.2);
    transform: translateY(-2px);
}

.btn-stop:active {
    background: linear-gradient(135deg, #dc3545, #d9606c);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    transform: translateY(1px);
}

.table-header {
    background-color: #e4ebf2;
}
.page-wrapper {
  background-color: #eff0f2; 
  min-height: 100vh; 
  margin: 0;
  padding: 0;
}
.page-content {
  margin: 0;
  padding: 0;
}
.btn-icon {
  background: none; 
  border: none; 
  padding: 5px; 
  cursor: pointer; 
  transition: transform 0.2s ease, background-color 0.2s ease; 
  border-radius: 10%; 
}

.btn-icon:hover {
  transform: scale(1.3); 
}

.btn-image {
  width: 20px; 
  height: 20px;
}
#example2 tbody tr:nth-of-type(even) {
    background-color: #e4ebf2; 
}
#example2 tbody tr:nth-of-type(odd) {
    background-color: #fff; 
}
td{
    vertical-align: middle;
}
th {
    font-size: 16px !important;
    color: rgba(52, 64, 80, 1) !important;
    font-weight: bold;
    padding: 0.75rem;
    border-bottom-width: 0;
}
tr {
    text-align: center;
}
.mb-0 {
    font-size: 12px;
    font-family: Microsoft YaHei, Arial, sans-serif;
}
.dynamic-monitor {
  text-align: center;
  padding: 20px;
}
.dynamic-image {
  max-width: 100%;
  height: auto;
}
.chart-container {
  display: flex;
  justify-content: space-between;
}

.chart {
  height: 400px;
}

.chart--line {
  width: 90%;
}

.chart--pie {
  width: 40%;
}
</style>