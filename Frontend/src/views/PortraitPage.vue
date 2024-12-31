<template>
    <div>
        <BgCover :show-cover="showDialogFlag"></BgCover>
        <div class="page-wrapper">
            <div class="page-content">
                <div class="card">
                    <div class="card-body">
                        <div class="page-breadcrumb d-none d-sm-flex align-items-center mb-3">
                            <div class="logo-container ps-3">
                                <img src="../assets/images/icon.png" alt="Logo" class="logo-img" style="width: 30px; height: auto;" />
                            </div>
                            <div class="breadcrumb-title pe-3 ps-2" style="border-right: none;">IP画像</div>
                            <div class="d-flex align-items-center ms-auto">
                                <!-- 输入 IP 地址部分 -->
                                <div class="me-3">
                                    <div class="input-group">
                                        <span class="input-group-text" id="basic-addon3">输入要画像的IP地址</span>
                                        <input type="text" class="form-control" id="basic-url" aria-describedby="basic-addon3" v-model="inputTartgetIp">
                                        <button :class="btnClassPortrait" @click="portraintByInput">进行画像</button>
                                    </div>
                                </div>
                                <!-- 查看详情按钮 -->
                                <div class="me-3">
                                    <button class="btn btn-outline-primary" @click="openMore">查看详情</button>
                                </div>
                                <!-- 显示地图按钮 -->
                                <div>
                                    <button class="btn btn-outline-primary" @click="toggleMap">显示地图</button>
                                </div>
                            </div>
                        </div>
                        <hr />
                <div style="position: relative; width: 100%; height: calc(100vh - 110px);">
                    <div class="viz-background"></div>
                    <div id="viz1" style="position: relative; width: 100%;height: calc(100vh - 110px);z-index: 2;" v-show="load_process == 'ok' && !showMap"></div>
                    <div id="map" v-show="showMap" style="width: 100%; height: calc(100vh - 110px);z-index: 3;"></div>
                    <div id="viz-mask" style="width: 100%;height: calc(100vh - 110px);z-index: 2;" v-if="load_process != 'ok'" class="d-flex flex-column justify-content-center">
                        <div class="progress col-4 align-self-center">
                            <div class="progress-bar progress-bar-striped .progress-bar-animated" role="progressbar" :style="{width: load_percent+'%'}" :aria-valuenow="load_percent" aria-valuemin="0" aria-valuemax="100">
                                {{ load_percent < 100 ? Math.floor(load_percent)+'%' : load_process }}
                            </div>
                        </div>
                    </div>
                </div>
                <div class="modal" id="exampleSmallModal" tabindex="-1" :style="{'display': (showDialogFlag==true?'block':'none')}">
                    <div class="modal-dialog modal-xl">
                        <div class="modal-content">
                            <div class="modal-header" style="background-color: #154ec1 !important; width: 100%; z-index: 100; height: 50px; display: flex; align-items: center; padding: 0 20px;">
                                <div class="breadcrumb-title pe-3" style="color: white; font-size: 18px; margin-right: 20px; border-right:none;">IP画像信息</div>
                                <!-- <button type="button" class="btn-close" @click="dialogNo"></button> -->
                                <button class="close-button" @click="dialogNo" style="position: absolute; top: 5px; right: 20px; font-size: 30px; width: 40px; height: 40px; line-height: 40px; border: none;">x</button>
                            </div>
                            <div class="modal-body m-auto">
                                <div v-if="portrailtingFlag" class="spinner-border" role="status"> 
                                    <span class="visually-hidden">Loading...</span>
                                </div>
                                <div v-else>
                                    <div v-if="hasPortrailtFlag">
                                        <ul style="list-style-type:none">
                                            <li style="padding-bottom:5px;">
                                                <span style="display:inline-block;width:150px;">IP地址</span>
                                                <span style="display:inline-block;width:200px;">{{ target_ip }}</span>
                                            </li>
                                            <hr/>
                                            <li style="padding-bottom:5px">
                                                <span style="display:inline-block;width:150px">最新画像生成时间</span>
                                                <span style="display:inline-block;width:200px">{{latestPortraitTime}}</span>
                                            </li>
                                            <div class="card-header">
                                                <ul class="nav nav-tabs">
                                                    <!-- 条件渲染 Tab -->
                                                    <li v-if="lineChartTabs.sumpkts" class="nav-item">
                                                        <a class="nav-link" :class="{ active: activeTab === 'sumpkts' }" @click="switchTab('sumpkts')">总报文数</a>
                                                    </li>
                                                    <li v-if="lineChartTabs.sumbytes" class="nav-item">
                                                        <a class="nav-link" :class="{ active: activeTab === 'sumbytes' }" @click="switchTab('sumbytes')">总字节数</a>
                                                    </li>
                                                    <li v-if="lineChartTabs.avgduration" class="nav-item">
                                                        <a class="nav-link" :class="{ active: activeTab === 'avgduration' }" @click="switchTab('avgduration')">流持续时长均值</a>
                                                    </li>
                                                </ul>
                                            </div>
                                            <div class="card-body">
                                                <!-- 根据选中的 Tab 动态渲染对应的图表 -->
                                                <div v-if="activeTab === 'sumpkts' && shouldRenderSumpkts">
                                                    <div id="sumpktsChartLine" style="width: 700px; min-width: 100%; height:300px;"></div>
                                                </div>
                                                <div v-if="activeTab === 'sumbytes' && shouldRenderSumbytes">
                                                    <div id="sumbytesChartLine" style="width: 700px; min-width: 100%; height:300px;"></div>
                                                </div>
                                                <div v-if="activeTab === 'avgduration' && shouldRenderAvgduration">
                                                    <div id="avgdurationChartLine" style="width: 700px; min-width: 100%; height:300px;"></div>
                                                </div>
                                            </div>
                                            <hr/>
                                            <li style="padding-bottom:5px">
                                                <div class="d-flex flex-column">
                                                    <span style="display:inline-block;width:150px">业务分类</span>
                                                    <div v-if="ipHasClsFlag">
                                                        <div id="distribution"
                                                            style="width: 700px; min-width: 100%; height:400px;"></div>
                                                    </div>
                                                    <div v-else>
                                                        该ip暂未进行业务分类
                                                    </div>
                                                </div>
                                            </li>
                                        </ul>
                                    </div>
                                    <div v-else>
                                        <li style="padding-bottom:5px;">
                                            <span style="display:inline-block;width:150px;">IP地址</span>
                                            <span style="display:inline-block;width:200px;">{{ target_ip }}</span>
                                        </li>
                                        <hr/>
                                        <li style="padding-bottom:5px;">
                                                <span style="display:inline-block;width:150px;">该IP地址暂无画像</span>
                                            </li>
                                    </div>
                                </div>
                            </div>
                            <!-- <div class="modal-footer">
                                <button type="button" class="btn btn-primary" @click="dialogNo">确定</button>
                            </div> -->
                        </div>
                    </div>
                </div>
            </div>
        </div>
                </div>
        </div>
    </div>
</template>

<script type="text/javascript">
    window._AMapSecurityConfig = {
        securityJsCode: "d2b65bf7585d652c5abf203afffa6eda",
    };
</script>
<script src="https://webapi.amap.com/loader.js"></script>
<script>
import NeoVis, { NEOVIS_ADVANCED_CONFIG } from 'neovis.js/dist/neovis.js'
import BgCover from '../components/BgCover.vue'
import neo4j from 'neo4j-driver'

export default {
    components: { BgCover },
    data() {
        return {
            showDialogFlag: false,
            inputTartgetIp:'',
            target_ip: null,
            hasPortrailtFlag:false,
            portrailtingFlag:false,
            ipHasClsFlag:false,
            latestPortraitTime:'',
            avgDurationChart:null,
            sumBytesChart:null,
            sumPktChart:null,
            pieChart:null,
            viz:null,
            load_process:'Loading...',
            load_percent:0,
            showMap: false,
            mapInstance: null,
            lineChartTabs: {
      pkts: true,
      bytes: true,
      duration: true,
      sumpkts: true,       // Enable "总报文数"
      sumbytes: true,      // Enable "总字节数"
      avgduration: true    // Enable "流持续时长均值"
    },
    activeTab: 'sumpkts',   // Default active tab
    shouldRenderSumpkts: true,
    shouldRenderSumbytes: false,
    shouldRenderAvgduration: false,
    avgDurationList: [],
                            sumBytesList: [],
                            sumPktsList: [],
                            timeList: []
        }
    },

    computed:{
        btnClassPortrait: function () {
            return [
                'btn', 'btn-primary',
                {
                    'disabled': this.inputTartgetIp == ''
                }
            ]
        },
    },

    mounted() {
        this.draw(`${document.location.hostname}:7687`)
    },
    methods: {
        switchTab(tab) {
            this.activeTab = tab;
            if (tab === 'sumpkts' && this.sumPktsList) {
                this.shouldRenderSumpkts = true;
                this.draw_sum_pkts();
            } else {
                this.shouldRenderSumpkts = false;
            }
            if (tab === 'sumbytes' && this.sumBytesList) {
                this.shouldRenderSumbytes = true;
                this.draw_sum_bytes();
            } else {
                this.shouldRenderSumbytes = false;
            }
            if (tab === 'avgduration' && this.avgDurationList) {
                this.shouldRenderAvgduration = true;
                this.draw_avg_duration();
            } else {
                this.shouldRenderAvgduration = false;
            }
        },
        draw_sum_pkts() {
            const maxP = Math.max(...this.sumPktsList);
            var sumPktsOption = {
                tooltip: {
                    trigger: 'axis'
                },
                xAxis: {
                    type: "category",
                    name: "time",
                    boundaryGap: false,
                    data: this.timeList,
                },
                yAxis: {
                    type: "value",
                    name: "sum pkts",
                },
                visualMap: [{
                    show: false,
                    type: 'continuous',
                    seriesIndex: 0,
                    min: 0,
                    max: maxP,
                    inRange: {
                        color: ['#154EC1', 'red']
                    },
                }],
                series: [{
                    name: "包总数",
                    type: "line",
                    stack: "sum pkts",
                    data: this.sumPktsList,
                    areaStyle: {},
                }],
            };
        
            // Initialize the chart for sum pkts
            this.$nextTick(() => {
                this.sumPktChart = this.$echarts.init(document.getElementById('sumpktsChartLine'), "roma");
                this.sumPktChart.setOption(sumPktsOption);
            });
        },
        draw_sum_bytes() {
            const maxB = Math.max(...this.sumBytesList);
            var sumBytesOption = {
                tooltip: {
                    trigger: 'axis'
                },
                xAxis: {
                    type: "category",
                    name: "time",
                    boundaryGap: false,
                    data: this.timeList,
                },
                yAxis: {
                    type: "value",
                    name: "sum bytes",
                },
                visualMap: [{
                    show: false,
                    type: 'continuous',
                    seriesIndex: 0,
                    min: 0,
                    max: maxB,
                    inRange: {
                        color: ['#154EC1', 'red']
                    },
                }],
                series: [{
                    name: "字节总数",
                    type: "line",
                    stack: "sum bytes",
                    data: this.sumBytesList,
                    areaStyle: {},
                }],
            };
        
            // Initialize the chart for sum bytes
            this.$nextTick(() => {
                this.sumBytesChart = this.$echarts.init(document.getElementById('sumbytesChartLine'), "roma");
                this.sumBytesChart.setOption(sumBytesOption);
            });
        },
        draw_avg_duration() {
            const maxD = Math.max(...this.avgDurationList);
            var avgDurationOption = {
                tooltip: {
                    trigger: 'axis'
                },
                xAxis: {
                    type: "category",
                    name: "time",
                    boundaryGap: false,
                    data: this.timeList,
                },
                yAxis: {
                    type: "value",
                    name: "avg duration",
                },
                visualMap: [{
                    show: false,
                    type: 'continuous',
                    seriesIndex: 0,
                    min: 0,
                    max: maxD,
                    inRange: {
                        color: ['#154EC1', 'red']
                    },
                }],
                series: [{
                    name: "平均流长度",
                    type: "line",
                    stack: "avg duration",
                    data: this.avgDurationList,
                    areaStyle: {},
                }],
            };
        
            // Initialize the chart for average duration
            this.$nextTick(() => {
                this.avgDurationChart = this.$echarts.init(document.getElementById('avgdurationChartLine'), "roma");
                this.avgDurationChart.setOption(avgDurationOption);
            });
        },
        

        toggleMap() {
            this.showMap = !this.showMap; // 切换显示状态
            if (this.showMap) {
                this.loadAmap();
            }
        },
        async fetchGraphData() {
            const driver = neo4j.driver(
                `bolt://${document.location.hostname}:7687`, // 替换为您的 Neo4j 服务器地址
                neo4j.auth.basic('neo4j', 'southeast2022.'), // 替换为您的用户名和密码
                {
                    encrypted: 'ENCRYPTION_OFF',
                    trust: 'TRUST_ALL_CERTIFICATES'
                }
            );
            const session = driver.session();

            try {
                const result = await session.run(`
                    MATCH p=(a)-[:to]-()
                    RETURN p
                    LIMIT 200
                `);
                // console.log(result);

                const nodes = new Map();
                const edges = [];

                result.records.forEach(record => {
                    const path = record.get('p'); // 获取路径对象

                    // 获取起点和终点节点
                    const startNode = path.start;
                    const endNode = path.end;
                    // console.log(startNode.identity)
                    // console.log(endNode.identity)

                    // 添加起点节点
                    if (!nodes.has(startNode.identity.low)) {
                        nodes.set(startNode.identity.low, {
                            id: startNode.identity.low,
                            name: startNode.properties.name,
                            lon: parseFloat(startNode.properties.lon || 0),
                            lat: parseFloat(startNode.properties.lat || 0),
                            isp_domain: startNode.properties.isp_domain || "未知运营商",
                            region: startNode.properties.region || "未知",
                            city: startNode.properties.city || "未知",
                            inDegree: startNode.properties.in_degree,
                            outDegree: startNode.properties.out_degree,
                            degree: startNode.properties.degree
                        });
                    }

                    // 添加终点节点
                    if (!nodes.has(endNode.identity.low)) {
                        nodes.set(endNode.identity.low, {
                            id: endNode.identity.low,
                            name: endNode.properties.name,
                            lon: parseFloat(endNode.properties.lon || 0),
                            lat: parseFloat(endNode.properties.lat || 0),
                            isp_domain: endNode.properties.isp_domain || "未知运营商",
                            region: endNode.properties.region || "未知",
                            city: endNode.properties.city || "未知",
                            inDegree: endNode.properties.in_degree,
                            outDegree: endNode.properties.out_degree,
                            degree: endNode.properties.degree
                        });
                    }

                    // 添加边信息
                    edges.push({
                        from: startNode.identity.low,
                        to: endNode.identity.low,
                        type: path.segments[0]?.relationship.type || "to"
                    });
                });
            
                return { nodes: Array.from(nodes.values()), edges };
            } catch (error) {
                console.error('Neo4j Query Error:', error);
                return { nodes: [], edges: [] };
            } finally {
                await session.close();
                await driver.close();
            }
        },
        plotGraphOnMap(nodes, edges) {
            if (!this.mapInstance) return;
            // this.mapInstance.clearMap();

            const existingPositions = new Set();
            // let pathSimplifier = null;
            const loca = new Loca.Container({
                map: this.mapInstance,
            });
            // 辅助函数：检查经纬度是否重合
            const isPositionOverlap = (lon, lat) => {
                const key = `${lon.toFixed(6)},${lat.toFixed(6)}`; // 使用字符串作为位置标识
                return existingPositions.has(key);
            };
            // 辅助函数：调整经纬度
            const adjustPosition = (lon, lat, step = 1) => {
                let newLon = lon;
                let newLat = lat;
                let iterations = 0;
                while (isPositionOverlap(newLon, newLat) && iterations < 100) { // 最多调整 100 次
                    newLon += (Math.random() - 0.5) * step; // 在 -step/2 到 +step/2 之间随机调整经度
                    newLat += (Math.random() - 0.5) * step; // 在 -step/2 到 +step/2 之间随机调整纬度
                    iterations++;
                }
                return [newLon, newLat];
            };
            
            const nodeMap = new Map();
            nodes.forEach(node => {
                if (node.lon !== undefined && node.lat !== undefined) {
                    // 检查并调整位置
                    let [lon, lat] = adjustPosition(node.lon, node.lat);

                    // 记录最终位置，避免后续节点重合
                    existingPositions.add(`${lon.toFixed(6)},${lat.toFixed(6)}`);

                    // 更新节点索引
                    nodeMap.set(node.id, { ...node, lon, lat });

                    // 根据度数动态计算标记大小
                    // console.log(node.degree)
                    

                } else {
                    console.warn(`节点 ${node.id} 缺少经纬度信息，跳过绘制`);
                }
            });

            // 构建飞线数据
            const pulseLineData = edges.map(edge => {
                const fromNode = nodeMap.get(edge.from);
                const toNode = nodeMap.get(edge.to);

                // const distance = AMap.GeometryUtil.distance(
                //     [fromNode.lon, fromNode.lat],
                //     [toNode.lon, toNode.lat]
                // );
        
                if (fromNode && toNode) {
                    return {
                        geometry: {
                            type: 'LineString',
                            coordinates: [
                                [fromNode.lon, fromNode.lat],
                                [toNode.lon, toNode.lat],
                            ],
                        },
                        properties: {
                            color: '#00FF00', // 默认线条颜色
                            weight: 2, // 线条权重
                            //distance: distance,
                            fromNodeID: fromNode.id,
                            toNodeID: toNode.id,
                        },
                    };
                } else {
                    console.warn(`边 (${edge.from} -> ${edge.to}) 的起点或终点缺失，跳过绘制`);
                    return null;
                }
            }).filter(data => data !== null);
        
            // 创建 PulseLinkLayer
            const pulseLinkLayer = new Loca.PulseLinkLayer({
                loca,
                zIndex: 120,
            });
        
            // 设置数据源
            const source = new Loca.GeoJSONSource({
                data: {
                    type: 'FeatureCollection',
                    features: pulseLineData,
                },
            });
        
            // pulseLinkLayer.setSource(source);
            const emptyData = [];
            const Emptysource = new Loca.GeoJSONSource({
                data: {
                    type: 'FeatureCollection',
                    features: emptyData,
                },
            });
            pulseLinkLayer.setSource(Emptysource);
        
            // 设置样式
            pulseLinkLayer.setStyle({
                unit: 'px',
                // height: 5000000 / 3,
                height: function (index, item) {
                    return item.distance / 3;
                }, 
                lineWidth: [2, 2], // 线宽
                // maxHeightScale: 0.3,
                // lineColors: ['#3366FF', '#0B8CFF', '#06F8FF'],  //蓝色线
                lineColors: ['#FF0000', '#FFAD1F', '#FF0000'],
                // headColor: '#3366FF',  //光线颜色
                // trailColor: '#06F8FF',
                headColor : '#FFFF00',
                trailColor : '#FFFF00',
                // Dark:
                // lineColors: ['#00F8FF', '#D0FFFE', '#00F8FF'],
                // headColor: '#00F8FF',
                // trailColor: '#D0FFFE',
                flowLength: 100,
                speed: 50,
            });

            // 设置 GeoJSON 数据
            const nodeData = {
                type: 'FeatureCollection',
                features: Array.from(nodeMap.values()).map(node => ({
                    type: 'Feature',
                    geometry: {
                        type: 'Point',
                        coordinates: [node.lon, node.lat],
                    },
                    properties: {
                        degree: node.degree || 1, // 节点的度数
                        id: node.id,
                        name: node.name,
                        isp: node.isp_domain || '未知',
                        region: node.region || '未知',
                        city: node.city || '未知',
                    },
                })),
            };
            const url_breath = {
                green: 'https://a.amap.com/Loca/static/static/green.png',
                yellow: 'https://a.amap.com/Loca/static/loca-v2/demos/images/breath_yellow.png',
                red: 'https://a.amap.com/Loca/static/loca-v2/demos/images/breath_red.png',
                orange: 'https://a.amap.com/Loca/static/static/orange.png',
                white: './breath_white.png'
            }

            // const scatterLayer = new Loca.ScatterLayer({
            //     loca,
            //     zIndex: 10,
            //     opacity: 1,
            //     visible: true,
            // });

            // scatterLayer.setSource(new Loca.GeoJSONSource({
            //     data: nodeData,
            // }));
            
            // scatterLayer.setStyle({
            //     unit: 'meter', // 使用米作为单位
            //     size: (index, item) => {
            //         // 根据度数计算扩散范围
            //         const size = 20000 * (Math.log10(Number(item.properties.degree) + 1) + 1);
            //         return [size, size];
            //     },
            //     borderWidth: 0,
            //     texture: url_breath.green,
            //     duration: 1000,
            //     animate: true,
            //     opacity: 0.8,
            // });
            // loca.add(scatterLayer);

            // 筛选数据
            const filterFeaturesByDegree = (features, min, max) =>
                features.filter(
                    feature => feature.properties.degree > min && feature.properties.degree <= max
                );
            
            // 使用 nodeData.features 进行筛选
            const greenData = {
                type: 'FeatureCollection',
                features: filterFeaturesByDegree(nodeData.features, 0, 50),
            };
            
            const yellowData = {
                type: 'FeatureCollection',
                features: filterFeaturesByDegree(nodeData.features, 50, 100),
            };
            
            const redData = {
                type: 'FeatureCollection',
                features: filterFeaturesByDegree(nodeData.features, 100, Infinity),
            };
            
            // 创建 ScatterLayer 并设置样式
            const createScatterLayer = (data, texture, zIndex) => {
                const layer = new Loca.ScatterLayer({
                    loca,
                    zIndex: zIndex,
                    opacity: 1,
                    visible: true,
                });
            
                layer.setSource(new Loca.GeoJSONSource({ data }));
            
                layer.setStyle({
                    unit: 'meter', // 使用米作为单位
                    size: (index, item) => {
                        const size = 20000 * (Math.log10(Number(item.properties.degree) + 1) + 1);
                        return [size, size];
                    },
                    borderWidth: 0,
                    texture: texture, // 使用指定纹理
                    duration: 1000,
                    animate: true,
                    opacity: 0.8,
                });
            
                loca.add(layer); // 添加到地图
            };
            
            // 创建不同区间的 ScatterLayer
            createScatterLayer(greenData, url_breath.green, 10);
            createScatterLayer(yellowData, url_breath.yellow, 20);
            createScatterLayer(redData, url_breath.red, 30);        
        
            // 渲染飞线
            // pulseLinkLayer.render();
            loca.animate.start();
        
            // 绘制节点
            nodeMap.forEach(node => {
                const markerSize = 10 * (Math.log10(Number(node.degree || 1) + 1) + 1);

                const marker = new AMap.Marker({
                    position: [node.lon, node.lat],
                    title: `${node.name} || ${node.city} || ${node.isp_domain}`,
                    map: this.mapInstance,
                    // label: {
                    //     content: `<div>${node.name} ${node.isp_domain}</div>`,
                    //     offset: new AMap.Pixel(10, -10),
                    // },
                    icon: new AMap.Icon({
                        // image: './loc_red.png',
                        // image: './loc_orange.png',
                        image: './fire_blue.png',
                        // Dark:
                        // image: './loc_white.png',
                        size: new AMap.Size(markerSize, markerSize),
                        imageSize: new AMap.Size(markerSize, markerSize),
                        anchor: new AMap.Pixel(markerSize / 2, markerSize),
                    }),
                    offset: new AMap.Pixel(-markerSize / 2, -markerSize),
                });
        
                // 鼠标事件
                marker.on('mouseover', () => {
                    // 高亮相关飞线
                    const relatedData = pulseLineData.filter(
                        data =>
                            data.properties.fromNodeID === node.id ||
                            data.properties.toNodeID === node.id
                    );
                    const Filteredsource = new Loca.GeoJSONSource({
                        data: {
                            type: 'FeatureCollection',
                            features: relatedData,
                        },
                    });
                    pulseLinkLayer.setSource(Filteredsource);
                });

                marker.on('mouseout', () => {
                    // 恢复所有飞线
                    const emptyData = [];
                    const Emptysource = new Loca.GeoJSONSource({
                        data: {
                            type: 'FeatureCollection',
                            features: emptyData,
                        },
                    });
                    pulseLinkLayer.setSource(Emptysource);
                });
        
                marker.on('click', () => {
                    const obj = {
                        node: {
                            raw: {
                                properties: {
                                    name: node.name,
                                },
                            },
                        },
                    };
                    this.nodeClick(obj);
                });
            });

            
            
            

            // edges.forEach(edge => {
            //     const fromNode = nodeMap.get(edge.from);
            //     const toNode = nodeMap.get(edge.to);
            //     if (fromNode && toNode) {
            //         const edgeKey = `${Math.min(edge.from, edge.to)}-${Math.max(edge.from, edge.to)}`;
            //         let setStrokeColor = '#3366FF';
            //         new AMap.Polyline({
            //             path: [
            //                 [fromNode.lon, fromNode.lat],
            //                 [toNode.lon, toNode.lat]
            //             ],
            //             strokeColor: setStrokeColor,
            //             strokeWeight: 2,
            //             map: this.mapInstance
            //         });

            //         // 记录当前边为已绘制
            //         drawnEdges.add(edgeKey);
            //     }else {
            //         console.warn(`边 (${edge.from} -> ${edge.to}) 的起点或终点缺失，跳过绘制`);
            //     }
            // });

        },
        
        loadAmap() {
            if (this.mapInstance) {
                this.plotGraphOnMap();
                return;
            }
            const script = document.createElement('script');
            script.src = 'https://webapi.amap.com/loader.js';
            script.onload = () => {
                AMapLoader.load({
                    key: "d04e7b04ad6dc644be113c03b51576cb", // 替换为您的应用Key
                    version: "2.0", // 加载 2.0 版本
                })
                    .then(async AMap => {
                        this.mapInstance = new AMap.Map('map', {
                            viewMode: '3D',
                            zoom: 4, // 初始缩放级别（全球视角）
                            center: [104.0668, 30.5728], // 初始中心点（全球视角）
                            mapStyle: 'amap://styles/01313ee60f8c93df51c4ff11520e1113',
                            // Dark:
                            // mapStyle: 'amap://styles/darkblue',
                            pitch: 28,
                        });
                        const uiScript = document.createElement('script');  // AMapUI
                        uiScript.src = 'https://webapi.amap.com/loca?v=2.0.0&key=d04e7b04ad6dc644be113c03b51576cb';
                        uiScript.onload = async () => {
                            const { nodes, edges } = await this.fetchGraphData();
                            this.plotGraphOnMap(nodes, edges); // 绘制节点和连线
                        };
                        uiScript.onerror = () => {
                            console.error('Luca 加载失败');
                        };
                        document.body.appendChild(uiScript);
                    })
                    .catch((e) => {
                        console.error('高德地图加载失败:', e);
                    });
            };
            document.body.appendChild(script);
        },
        VNodeRender(node) {
            const domNode = document.createElement(node.tag)
            if (node.data) {
                for (const data of Object.keys(node.data)) {
                    domNode.setAttribute(data, node.data[data])
                }
            }
            if (node.children) {
                for (const child of node.children) {
                    if (child.tag) {
                        const dom = this.VNodeRender(child)
                        domNode.appendChild(dom)
                    } else {
                        const dom = document.createTextNode(child.text)
                        domNode.appendChild(dom)
                    }
                }
            }
            if (node.text) {
                domNode.innerText = node.text
            }
            return domNode
        },
        renderHtml(node) {
            if (this.load_percent < 100) {
                this.load_percent += 1/10
            }
            let count
            if (this.viz.nodes.get(node.identity)) {
                count = this.viz.nodes.get(node.identity).size
                count = Math.pow(10, (count / 10) - 1) - 1
                count = Math.round(count)
            }
            const isp = node.properties?.isp_domain || "未知isp"
            const localtion = node.properties?.country == '中国' ? 
                node.properties?.region == node.properties?.city || !node.properties?.city 
                ? `${node.properties?.region}` : `${node.properties?.region} / ${node.properties?.city}` :
             node.properties?.country == node.properties?.region ? `${node.properties?.country}`
                                                                 : `${node.properties?.country} / ${node.properties?.region}`
            return this.VNodeRender(
                <div class="card text-dark bg-light font-monospace m-0" style="max-width: 20rem;">
                    <div class="card-header fs-6 fw-bold ps-2">
                        <i class="bx bx-info-circle pe-1" style="vertical-align: middle;" />
                        节点&nbsp;
                        { isp != '未知isp' ? <span class="badge rounded-pill bg-info text-dark">{isp}</span> : ''}
                    </div>
                    <div class="card-body">
                        <div class="text-muted fs-6 mb-1">IP: {node.properties.name}</div>
                        { count ? <div class="text-muted fs-6 mb-1">邻接节点数量: {count}</div>
                                : ''     
                        }
                        <div class="text-muted fs-6 mb-1">归属地: {localtion}</div>
                    </div>
                </div>
            )
        },
        openMore() {
            window.open(`http://${document.location.hostname}:7474`)
        },
        draw(neoUri) {
            // 创建veovis实例
            var viz

            var neoUrl = 'bolt://'+neoUri
            var config = {
                containerId: 'viz1',
                neo4j: {
                    serverUrl: neoUrl,
                    serverUser: '【neo4j_username】',
                    serverPassword: '【neo4j_password】'
                },
                labels: {
                    IP: {
                        [NEOVIS_ADVANCED_CONFIG]: {
                            cypher: {
                                size: "MATCH p=(n)--() WHERE id(n)=$id WITH 10*(log10(count(p)+1)+1) AS s RETURN s"
                            },
                            function: {
                                title: this.renderHtml
                            }
                        }
                    }
                },
                initialCypher: `\
                    MATCH p=(a)-[:to]-()
                    RETURN p
                    LIMIT 300
                `,
                visConfig: {
                    nodes: {
                        image: 'static/images/bg-trans.png',
                        shape: 'circularImage',
                        font: {
                            color: '#fff',
                            size: 12,
                            strokeWidth: 0
                        },
                        borderWidth: 2
                    },
                    edges: {
                        color: '#888',
                        smooth: false,
                        arrows: {
                            to: {
                                enabled: true,
                                type: 'triangle'
                            }
                        },
                        label: ' to ',
                        font: {
                            background: '#fff',
                            size: 10
                        }
                    },
                    physics: {
                        solver: 'forceAtlas2Based',
                        forceAtlas2Based: {
                            damping: 0.5,
                            springConstant: 0.04,
                            springLength: 100,
                            avoidOverlap: 0.8
                        }
                    }
                }
            }
            viz = new NeoVis(config)
            this.viz = viz
            // console.log(viz)
            const bgElement = document.querySelector('.viz-background')
            if (bgElement) {
                bgElement.style.position = 'absolute'
                bgElement.style.top = '0'
                bgElement.style.left = '0'
                bgElement.style.width = '100%'
                bgElement.style.height = '100%'
                bgElement.style.background = "url('/world-map.svg') no-repeat center center"
                bgElement.style.backgroundSize = 'contain'
                bgElement.style.opacity = '0.5' // 设置透明度
                bgElement.style.zIndex = '1'
                bgElement.style.pointerEvents = 'none'
            }
            viz.render()
            viz.registerOnEvent('clickNode', this.nodeClick)
            let isListenerAdded = false
            viz.registerOnEvent('completed', (recordCount)=> {
                this.load_process = 'ok'
                viz.network.removeAllListeners("click")
                if (!isListenerAdded) {
                    viz.network.addEventListener('oncontext', function (event) {
                        event.event.returnValue = false
                        const nodeId = this.getNodeAt(event.pointer.DOM)
                        if (nodeId) {
                            const node = viz.nodes.get(nodeId)
                            viz.updateWithCypher(`
                                MATCH path = (a)--(o)
                                WHERE id(a) = ${nodeId}
                                RETURN path
                                LIMIT 20
                            `)
                            // alert(node.raw.properties.value)
                        }
                        return false
                    })
                    isListenerAdded = true
                }
            })
        },

        drawModal() {
            let distributionData = {
                legendData: ['p2p', 'fileupload', 'streaming', 'webhttps', 'Unknow'],
                data: [
                    { value: 15248, name: 'p2p' },
                    { value: 22409, name: 'fileupload' },
                    { value: 246521, name: 'streaming' },
                    { value: 65729, name: 'webhttps' },
                    { value: 89755, name: 'Unknow' }
                ]
            }
            var option = {
                maintainAspectRatio: false,
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
                    itemWidth: 10,//图例颜色块的宽度和高度
                    itemHeight: 6,
                    textStyle: {//图例中文字的样式
                        color: '#000',
                        fontSize: 8
                    },
                    data: distributionData.legendData//图例上显示的饼图各模块上的名字
                },
                color: ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#91c7ae'],
                series: [{
                    type: 'pie',             //echarts图的类型   pie代表饼图
                    radius: ['40%', '70%'],           //饼图中饼状部分的大小所占整个父元素的百分比
                    center: ['50%', '50%'],
                    data: distributionData.data,
                    itemStyle: {
                        borderRadius: 10,
                            borderColor: '#fff',
                            borderWidth: 2,
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
            let chart = this.$echarts.init(document.getElementById('distribution'), "roma");
            chart.setOption(option)
        },

        portraintByInput(){
            const ipReg = /^(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])$/;
            if(!(this.inputTartgetIp == '' || ipReg.test(this.inputTartgetIp))){
                alert('请输入正确的IP地址')
                return
            }
            var obj = {
                node: {
                    raw: {
                        properties: {
                            name: this.inputTartgetIp
                        }
                    }
                }
            }
            this.nodeClick(obj)
        },

        isEmptyObject(obj){
            for(let n in obj){
                return false
            }
            return true
        },

        nodeClick(node) {
            console.log(node)
            console.log(node.node.raw.properties.name)  //这样获取节点对应的ip地址
            this.target_ip = node.node.raw.properties.name
            this.portrailtingFlag = true
            this.showDialogFlag = true
            this.hasPortrailtFlag = false
            this.ipHasClsFlag = false
            this.$axios.post("/nmas/detect/genIPImage", { "IPlist": [this.target_ip] }).then(response => {
                if (response.data.status == 'success') {
                    this.$axios.post("/nmas/detect/showIPImage",{'ip':this.target_ip}).then(resp=>{
                        if(resp.data.status == 'success'){
                            console.log(resp.data.result)
                            if(resp.data.result.length == 0){
                                alert('该IP还未生成画像')
                                // this.showDialogFlag = false
                                this.portrailtingFlag = false
                                return
                            }
                            console.log(resp.data.result)
                            this.avgDurationList = []
                            this.sumBytesList = []
                            this.sumPktsList = []
                            this.timeList = []
                            var label_num = {}
                            for(var idx in resp.data.result){
                                var item = resp.data.result[idx]
                                if(idx == 0){
                                    this.latestPortraitTime = item['time']
                                    label_num = item['label_num']
                                }
                                // else{
                                //     for(let k of item['label_num']){
                                //         label_num[k] = label_num[k] + item['label_num'][k]
                                //     }
                                // }
                                // console.log(item)
                                // console.log(item['avgDuration'])
                                // console.log(item.avgDuration)
                                this.avgDurationList.push(item['avgDuration'])
                                this.sumBytesList.push(item['sumBytes'])
                                this.sumPktsList.push(item['sumPkts'])
                                this.timeList.push(item['time'])
                            }
                            console.log(label_num)
                            if(this.isEmptyObject(label_num)){
                                this.$axios.post('/nmas/classify/modelPredSQL',{
                                    "threshold":"0.5",
                                    "method":"classic",
                                    "ip":this.target_ip
                                }).then(res=>{
                                    console.log(res)
                                    if(res.data.status == 'success'){
                                        label_num = res.data.result.label_count
                                        this.ipHasClsFlag = true
                                        let legendData = []
                                        let pieData = []
                                        for(let k in label_num){
                                            console.log(k)
                                            legendData.push(k)
                                            pieData.push({'value':label_num[k],'name':k})
                                        }
                                        let pieOption = {
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
                                                data: legendData//图例上显示的饼图各模块上的名字
                                            },
                                            color: ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#91c7ae'],
                                            series: [{
                                                type: 'pie',             //echarts图的类型   pie代表饼图
                                                radius: ['40%', '70%'],           //饼图中饼状部分的大小所占整个父元素的百分比
                                                center: ['50%', '50%'],
                                                data: pieData,
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
                                            if(this.ipHasClsFlag){
                                                this.pieChart = this.$echarts.init(document.getElementById('distribution'), "roma")
                                                this.pieChart.setOption(pieOption)
                                            }
                                        })
                                    }
                                })
                            }else{
                                this.ipHasClsFlag = true
                            }
                            
                            console.log(label_num)
                            let legendData = []
                            let pieData = []
                            for(let k in label_num){
                                console.log(k)
                                legendData.push(k)
                                pieData.push({'value':label_num[k],'name':k})
                            }
                            let pieOption = {
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
                                    data: legendData//图例上显示的饼图各模块上的名字
                                },
                                series: [{
                                    type: 'pie',             //echarts图的类型   pie代表饼图
                                    radius: ['50%', '70%'],           //饼图中饼状部分的大小所占整个父元素的百分比
                                    center: ['50%', '50%'],
                                    data: pieData,
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
                                        
                            this.portrailtingFlag = false
                            this.hasPortrailtFlag = true
                            this.$nextTick(()=>{
                                // this.avgDurationChart = this.$echarts.init(document.getElementById('avgdurationChartLine'), "roma")
                                // this.avgDurationChart.setOption(avgDurationOption)
                                // this.sumPktChart = this.$echarts.init(document.getElementById('sumpktsChartLine'), "roma")
                                // this.sumPktChart.setOption(sumPktsOption)
                                // this.sumBytesChart = this.$echarts.init(document.getElementById('sumbytesChartLine'), "roma")
                                // this.sumBytesChart.setOption(sumBytesOption)
                                if (this.shouldRenderSumpkts) {
                                    this.draw_sum_pkts();
                                }
                                if (this.shouldRenderSumbytes) {
                                    this.draw_sum_bytes();
                                }
                                if (this.shouldRenderAvgduration) {
                                    this.draw_avg_duration();
                                }
                                if(this.ipHasClsFlag){
                                    this.pieChart = this.$echarts.init(document.getElementById('distribution'), "roma")
                                    this.pieChart.setOption(pieOption)
                                }
                            })
                        }
                    },resp=>{
                        alert('画像获取失败，请重试')
                        console.log(response)
                        this.showDialogFlag = false
                    })


                }else{
                    alert('画像获取失败，请重试')
                    this.showDialogFlag = false
                }
            }, response => {
                alert('画像获取失败，请重试')
                console.log(response)
                this.showDialogFlag = false
            })
            // this.drawModal()
        },

        dialogNo(){
            this.target_ip = null
            this.showDialogFlag = false
        },

        closeDialog(){
            if(this.showDialogFlag==true){
                this.target_ip = null
                this.showDialogFlag = false
            }
        }
    }
}
</script>

<style scoped>
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
.modal-dialog {
  width: 80%; /* 默认宽度为视口宽度的80% */
  margin: auto; /* 使弹窗居中显示 */
}
.modal-content {
  width: 80%; /* 设置为80% */
  margin: auto; /* 确保在弹窗容器中居中 */
}
</style>