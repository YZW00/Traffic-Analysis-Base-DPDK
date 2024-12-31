<template>
    <!-- <div class="page-wrapper">
        <div class="page-content"> -->
            <!--breadcrumb-->
            <div class="card">
                <div class="card-body">
                    <div style="background-color: #154ec1 !important; position: fixed; top: 0; left: 0; width: 100%; z-index: 1000; height: 50px; display: flex; align-items: center; padding: 0 20px;">
                        <div class="breadcrumb-title pe-3" style="color: white; font-size: 18px; margin-right: 20px;">异常报告详情</div>
                        <div class="ps-3 d-flex justify-content-center" style="flex-grow: 1;">
                            <div class="align-self-center">
                                <nav aria-label="breadcrumb">
                                    <ol class="breadcrumb mb-0 p-0" style="color: white; font-size: 16px; margin-left: -600px;">
                                        <li class="breadcrumb-item" aria-current="page">异常IP：{{ anomalyIp }}</li>
                                        <li class="breadcrumb-item" aria-current="page">报告时间：{{ anomalyTime }}</li>
                                    </ol>
                                </nav>
                            </div>
                        </div>
                    </div>
                    <hr />
                    <div class="card" v-if="lineChartTabs.pkts || lineChartTabs.bytes || lineChartTabs.duration">
                        <div class="card-header">
                            <ul class="nav nav-tabs">
                                <!-- 条件渲染 Tab -->
                                <li v-if="lineChartTabs.pkts" class="nav-item">
                                <a class="nav-link" :class="{ active: activeTab === 'pkts' }" @click="switchTab('pkts')">流量报文数异常</a>
                                </li>
                                <li v-if="lineChartTabs.bytes" class="nav-item">
                                <a class="nav-link" :class="{ active: activeTab === 'bytes' }" @click="switchTab('bytes')">流量数据量异常</a>
                                </li>
                                <li v-if="lineChartTabs.duration" class="nav-item">
                                <a class="nav-link" :class="{ active: activeTab === 'duration' }" @click="switchTab('duration')">流量时间异常</a>
                                </li>
                            </ul>
                        </div>
                        <div class="card-body">
                            <!-- 根据选中的 Tab 动态渲染对应的图表 -->
                            <div v-if="activeTab === 'pkts' && lineChartTabs.pkts && shouldRenderPkts">
                                <div id="anomalypkts" style="width: 100%; height: 350px;"></div>
                            </div>
                            <div v-if="activeTab === 'bytes' && lineChartTabs.bytes && shouldRenderBytes">
                                <div id="anomalybytes" style="width: 100%; height: 350px;"></div>
                            </div>
                            <div v-if="activeTab === 'duration' && lineChartTabs.duration && shouldRenderDuration">
                                <div id="anomalyduration" style="width: 100%; height: 350px;"></div>
                            </div>
                        </div>
                    </div>
                    <div class="content">
                        <div class="card" v-if="ano_flow">
                            <h6>流业务类型异常</h6>
                            <table id="anomalyflow" class="table table-striped table-bordered" data-locale="zh-CN">
                                <thead>
                                    <tr>
                                        <th>检测时间</th>
                                        <th>源地址</th>
                                        <th>宿地址</th>
                                        <th>源端口</th>
                                        <th>宿端口</th>
                                        <th>协议号</th>
                                        <th>报文数</th>
                                        <th>字节数</th>
                                        <th>持续时间</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr v-for="item in result.anomaly_flow" :key="item.id">
                                        <td>{{ item["time"] }}</td>
                                        <td>{{ item['sip'] }}</td>
                                        <td>{{ item['dip'] }}</td>
                                        <td>{{ item['sport'] }}</td>
                                        <td>{{ item['dport'] }}</td>
                                        <td>{{ item['protocol'] }}</td>
                                        <td>{{ item['pkts'] }}</td>
                                        <td>{{ item['bytes'] }}</td>
                                        <td>{{ item['duration'] }}</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                        <!-- 其他异常类型的展示可以在这里继续添加 -->
                    </div>
                </div>
            </div>
        <!-- </div>
    </div> -->
</template>

<style scoped>
.breadcrumb-title{
    border-right:none;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter, .fade-leave-to {
  opacity: 0;
}

.floating-back-btn {
  position: fixed; /* 固定位置 */
  right: 20px; /* 距离页面右侧 20px */
  top: 50%; /* 垂直居中 */
  transform: translateY(-50%); /* 调整居中对齐 */
  z-index: 1050; /* 保证按钮浮在页面最上层 */
  width: 50px; /* 按钮宽度 */
  height: 50px; /* 按钮高度 */
  border-radius: 50%; /* 圆形按钮 */
  background: transparent;
  color: transparent; /* 图标颜色 */
  border: none;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 20px; /* 图标大小 */
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2); /* 按钮阴影 */
  transition: all 0.3s ease; /* 添加过渡效果 */
  cursor: pointer;
}

.floating-back-btn:hover {
  background: linear-gradient(135deg, #0056b3, #003d80); /* 悬停时更深的蓝色 */
  transform: translateY(-50%) scale(1.2); /* 鼠标悬停放大效果 */
  box-shadow: 0 6px 10px rgba(0, 0, 0, 0.3); /* 更明显的阴影 */
}


.table {
    font-size: 10px;
    background-color: #fff;
    margin-top: 40px;
    font-weight: 200;
}

.content div div {
    height: 300px;
    width: 100%;
}
.card{
    padding: 10px 10px 10px 10px
}
/* .page-breadcrumb {
    background-color: #154ec1; 
} */
</style>

<script>

// import '../assets/bootstrap-5.1.3-dist/css/bootstrap.min.css'
// import '../assets/css/bootstrap-table.css'

export default {
    data() {
        return{
            contentVisible: false, // 控制内容是否显示
            result:{},
            ano_pkts: false,
            ano_bytes: false,
            ano_duration: false,
            ano_flow:false,
            anomalyTime:'',
            anomalyIp:'',
            lineChartTabs: {
                pkts: false,
                bytes: false,
                duration: false
            },
            activeTab: 'pkts', // 默认显示 'pkts' Tab
            // 新增的属性，控制是否渲染对应的图表
            shouldRenderPkts: false,
            shouldRenderBytes: false,
            shouldRenderDuration: false
        }
    },
    mounted() {
        setTimeout(() => {
          this.contentVisible = true; // 延迟显示内容
        }, 300); // 与过渡动画时长一致
        console.log(this.$route.params)
        this.anomalyTime = this.$route.params.anomalyTs
        this.anomalyIp = this.$route.params.anomalyIp
        this.initTable()
        this.getData(this.$route.params.anomalyTs);
    },
    methods: {
        methods: {
          handleSmoothTransition(ip, timestamp) {
            setTimeout(() => {
              this.$router.push(`/anomaly/detail/${ip}/${timestamp}`);
            }, 300); // 延迟跳转，确保当前页面动画完成
          },
        },

        goBack() {
          // 使用 Vue Router 跳转到 /anomaly 路由
          this.$router.push('/anomaly');
        },
        getData(anomalyTime) {
            this.$axios.post('/nmas/detect/showAnomalyDetail', { time: anomalyTime })
            .then(resp => {
            if (resp.data.status === 'success') {
                this.result = resp.data.result;
                // 更新 Tabs 状态
                this.lineChartTabs.pkts = this.result.hasOwnProperty('anomaly_pkts');
                this.lineChartTabs.bytes = this.result.hasOwnProperty('anomaly_bytes');
                this.lineChartTabs.duration = this.result.hasOwnProperty('anomaly_duration');
                    
                    // 在这里控制每个图表是否需要渲染
                    this.shouldRenderPkts = this.lineChartTabs.pkts;
                    this.shouldRenderBytes = this.lineChartTabs.bytes;
                    this.shouldRenderDuration = this.lineChartTabs.duration;
                    // 初始化折线图
                    if (this.lineChartTabs.pkts) this.draw_anomaly_pkts();
                    if (this.lineChartTabs.bytes) this.draw_anomaly_bytes();
                    if (this.lineChartTabs.duration) this.draw_anomaly_duration();
                } else {
                    alert('获取异常详细信息出错');
                }
            })
            .catch(() => {
            alert('获取异常详细信息出错');
            });
        },
        initTable() {
            console.log($('#anomalyflow'))
            var table = $('#anomalyflow').DataTable();
            var dtOption = {
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
                    "lengthMenu": "显示 _MENU_ 项结果",
                    "zeroRecords": "没有匹配结果",
                    "info": "显示第 _START_ 至 _END_ 项结果，共 _TOTAL_ 项",
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
                $('#anomalyflow').DataTable(dtOption)
                // table.buttons().container().appendTo( '#example2_wrapper .col-md-6:eq(0)' );
            })
            
        },
        switchTab(tabName) {
            this.activeTab = tabName;
            // 切换 Tab 后，控制是否渲染该图表
            if (tabName === 'pkts' && this.lineChartTabs.pkts) {
                this.shouldRenderPkts = true;
                this.draw_anomaly_pkts();
            } else {
                this.shouldRenderPkts = false;
            }
            if (tabName === 'bytes' && this.lineChartTabs.bytes) {
                this.shouldRenderBytes = true;
                this.draw_anomaly_bytes();
            } else {
                this.shouldRenderBytes = false;
            }
            if (tabName === 'duration' && this.lineChartTabs.duration) {
                this.shouldRenderDuration = true;
                this.draw_anomaly_duration();
            } else {
            this.shouldRenderDuration = false;
            }
        },
        draw_anomaly_pkts() {
            if (!this.lineChartTabs.pkts) return;
            var xLableList = this.result.time_list
            var yList = this.result.anomaly_pkts["data"]
            const maxVal = Math.max(...yList)
            let that = this
            var option = {
                visualMap: [
                    {
                    show: false,
                    type: 'continuous',
                    seriesIndex: 0,
                    min: 0,
                    max: maxVal,
                    inRange: {
                        color: ['#154EC1', 'red'] // 从浅蓝色到深蓝色的渐变
                    },
                    },
                ],
                tooltip: {
                    trigger: 'axis'
                },
                xAxis: {
                    type: "category",
                    name: "时间",
                    boundaryGap: false,
                    data: xLableList,
                },
                yAxis: {
                    type: "value",
                    name: "报文数量",
                },
                series: [{
                    name: "报文数量",
                    type: "line",
                    stack: "pktcount",
                    data: yList,
                    areaStyle: {},
                    markPoint: {
                        data: (function () {
                            let d = []
                            for (var i in that.result.anomaly_pkts["ano_index"]) {
                                d.push({
                                    coord: [that.result.anomaly_pkts["ano_index"][i], that.result.anomaly_pkts["data"][that.result.anomaly_pkts["ano_index"][i]]],
                                    symbol: 'triangle',
                                    symbolSize: 15,
                                    animation: true,
                                    label: {
                                        show: true,
                                        color: '#000'
                                    },
                                    itemStyle: { color: '#f00' }
                                })
                            }
                            return d
                        })()
                    }
                }]
            }
            this.$nextTick(() => {
                let chart = this.$echarts.init(document.getElementById("anomalypkts")); // 修正了这里的ID
                chart.setOption(option);
            });
        },
        draw_anomaly_bytes() {
            if (!this.lineChartTabs.bytes) return;
            var xLableList = this.result.time_list
            var yList = this.result.anomaly_bytes["data"]
            const maxVal = Math.max(...yList)
            let that = this

            var option = {
                visualMap: [
                    {
                    show: false,
                    type: 'continuous',
                    seriesIndex: 0,
                    min: 0,
                    max: maxVal,
                    inRange: {
                        color: ['#154EC1', 'red'] // 从浅蓝色到深蓝色的渐变
                    },
                    },
                ],
                tooltip: {
                    trigger: 'axis'
                },
                xAxis: {
                    type: "category",
                    name: "时间",
                    boundaryGap: false,
                    data: xLableList,
                },
                yAxis: {
                    type: "value",
                    name: "字节数量",
                },
                series: [{
                    name: "字节数量",
                    type: "line",
                    stack: "bytescount",
                    data: yList,
                    areaStyle: {},
                    markPoint: {
                        data: (function () {
                            let d = []
                            for (var i in that.result.anomaly_bytes["ano_index"]) {
                                d.push({
                                    coord: [that.result.anomaly_bytes["ano_index"][i], that.result.anomaly_bytes["data"][that.result.anomaly_bytes["ano_index"][i]]],
                                    symbol: 'triangle',
                                    symbolSize: 15,
                                    animation: true,
                                    label: {
                                        show: true,
                                        color: '#000'
                                    },
                                    itemStyle: { color: '#f00' }
                                })
                            }
                            return d
                        })()
                    }
                }]
            }
            this.$nextTick(() => {
                let chart = this.$echarts.init(document.getElementById("anomalybytes"));
                chart.setOption(option);
            });
        },
        draw_anomaly_duration() {
            if (!this.lineChartTabs.duration) return;
            var xLableList = this.result.time_list
            var yList = this.result.anomaly_duration["data"]
            const maxVal = Math.max(...yList)
            let that = this

            var option = {
                visualMap: [
                    {
                    show: false,
                    type: 'continuous',
                    seriesIndex: 0,
                    min: 0,
                    max: maxVal,
                    inRange: {
                        color: ['#154EC1', 'red'] // 从浅蓝色到深蓝色的渐变
                    },
                    },
                ],
                tooltip: {
                    trigger: 'axis'
                },
                xAxis: {
                    type: "category",
                    name: "时间",
                    boundaryGap: false,
                    data: xLableList,
                },
                yAxis: {
                    type: "value",
                    name: "持续时间",
                },
                series: [{
                    name: "持续时间",
                    type: "line",
                    stack: "duration",
                    data: yList,
                    areaStyle: {},
                    markPoint: {
                        data: (function () {
                            let d = []
                            for (var i in that.result.anomaly_duration["ano_index"]) {
                                d.push({
                                    coord: [that.result.anomaly_duration["ano_index"][i], that.result.anomaly_duration["data"][that.result.anomaly_duration["ano_index"][i]]],
                                    symbol: 'triangle',
                                    symbolSize: 15,
                                    animation: true,
                                    label: {
                                        show: true,
                                        color: '#000'
                                    },
                                    itemStyle: { color: '#f00' }
                                })
                            }
                            return d
                        })()
                    }
                }]
            }
            
            this.$nextTick(() => {
                let chart = this.$echarts.init(document.getElementById("anomalyduration"));
                chart.setOption(option);
            });
        },
        // initpage() {
        //     this.initTable()
        //     this.draw_anomaly_pkts()
        //     this.draw_anomaly_bytes()
        //     this.draw_anomaly_duration()
        // },
    }
}
</script>
