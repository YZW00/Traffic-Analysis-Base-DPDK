$(document).ready(function() {
  "use strict";

  // worl map

  jQuery('#geographic-map-2').vectorMap(
    {
      map: 'world_mill_en',
      backgroundColor: 'transparent',
      borderColor: '#818181',
      borderOpacity: 0.25,
      borderWidth: 1,
      zoomOnScroll: false,
      color: '#009efb',
      regionStyle: {
        initial: {
          fill: '#008cff'
        }
      },
      markerStyle: {
        initial: {
          r: 9,
          'fill': '#fff',
          'fill-opacity': 1,
          'stroke': '#000',
          'stroke-width': 5,
          'stroke-opacity': 0.4
        },
      },
      enableZoom: true,
      hoverColor: '#009efb',
      markers: [{
        latLng: [21.00, 78.00],
        name: 'Lorem Ipsum Dollar'

      }],
      hoverOpacity: null,
      normalizeFunction: 'linear',
      scaleColors: ['#b6d6ff', '#005ace'],
      selectedColor: '#c9dfaf',
      selectedRegions: [],
      showTooltip: true,
    });

  /* totaltraffic部分 */
  /* 分为BPS/PPS上下两个图; 每个图包含出和入两个序列 */

  moment.locale('zh-cn') /* 设置时间格式化语言为zh-cn */

  const totalTrafficStyle = (title) => ({ /* 流量图风格配置 */
    /* NOTE: 应使用函数形式, 防止共用data字段导致干扰 */
    /* TODO: 纵轴提示合并 */
    /* TODO: 纵轴单位 */
    type: 'line',
    options: {
      title: {
        display: true,
        text: title,
        fontSize: 15
      },
      maintainAspectRatio: false,
      legend: {
        position: 'bottom'
      },
      tooltips: {
        displayColors: false,
        mode: 'nearest',
        intersect: false,
        position: 'nearest',
        xPadding: 10,
        yPadding: 10,
        caretPadding: 10,
        callbacks: {
          label(tooltipItem, data) {
            const label = data.datasets[tooltipItem.datasetIndex].label.split(' ')[0]
            const value = tooltipItem.yLabel
            return `${label}: ${value} ${title}`;
          }
        }
      },
      scales: {
        xAxes: [{
          type: 'time',
          time: { unit: 'day' }
        }],
        yAxes: [{
          type: 'linear',

        }]
      }
    }
  })
  const totalTrafficChart = (id, title) => { /* 流量图工厂函数 */
    /* NOTE: 向chart中添加了strokeA, strokeB两个渐变色 */
    const ctx = document.getElementById(id).getContext('2d')
    const strokeA = ctx.createLinearGradient(0, 0, 0, 300)
    const strokeB = ctx.createLinearGradient(0, 0, 0, 300)
    strokeA.addColorStop(0, '#7cb5ec')
    strokeA.addColorStop(1, 'rgba(255,255,255,0)')
    strokeB.addColorStop(0, '#f7a35c')
    strokeB.addColorStop(1, 'rgba(255,255,255,0)')
    const chart = new Chart(ctx, totalTrafficStyle(title))
    chart.strokeA = strokeA
    chart.strokeB = strokeB
    return chart
  }

  /* 流量图对象, 存储为全局变量供更新使用 */
  const totalTrafficBps = totalTrafficChart('totaltraffic-bps', "Mbps")
  const totalTrafficPps = totalTrafficChart('totaltraffic-pps', "Kpps")

  function totalTraffic_update(response_data) { /* 流量图数据更新 */
    /* 横坐标标签 */
    const totalTrafficLabel = response_data.charts.totalTrafficBps[0].data.map(e => new Date(e[0]))
    /* 转换接口数据格式 */
    const totalTrafficDataParser = data => ({
      data: data.data.map(e => e[1]),
      label: data.name
    })
    const totalTrafficBpsData = response_data.charts.totalTrafficBps.map(totalTrafficDataParser)
    const totalTrafficPpsData = response_data.charts.totalTrafficPps.map(totalTrafficDataParser)
    /* 设置数据集样式 */
    const totalTrafficDataWithStyle = (data, color) => ({
      label: data.label,
      data: data.data,
      pointRadius: 0,
      pointBorderWidth: 2,
      backgroundColor: color,
      borderColor: color,
      borderWidth: 2
    })
    /* 更新图表数据 */
    /* NOTE: 调换了出入顺序以提高美观程度 */
    /* TODO: 总览绘制更新 */
    totalTrafficBps.data.labels = totalTrafficLabel
    totalTrafficBps.data.datasets[0] = totalTrafficDataWithStyle(totalTrafficBpsData[1], totalTrafficBps.strokeB)
    totalTrafficBps.data.datasets[1] = totalTrafficDataWithStyle(totalTrafficBpsData[0], totalTrafficBps.strokeA)
    totalTrafficBps.update()
    totalTrafficPps.data.labels = totalTrafficLabel
    totalTrafficPps.data.datasets[0] = totalTrafficDataWithStyle(totalTrafficPpsData[1], totalTrafficPps.strokeB)
    totalTrafficPps.data.datasets[1] = totalTrafficDataWithStyle(totalTrafficPpsData[0], totalTrafficPps.strokeA)
    totalTrafficPps.update()
  }

  /* portstatic部分 */
  /* 包含出/入两个图 */
  const portStaticStyle = () => ({ /* 端口统计图风格配置 */
    type: 'pie',
    options: {
      maintainAspectRatio: false,
      legend: {
        position: 'bottom',
        labels: {
          boxWidth: 25,
          fontSize: 10
        }
      },
      responsive: true
    }
  })
  const portStaticChart = id => { /* 端口统计图工厂函数 */
    const ctx = document.getElementById(id).getContext('2d')
    const chart = new Chart(ctx, portStaticStyle())
    return chart
  }

  /* 端口统计图对象, 存储为全局变量供更新使用 */
  const portStaticIn = portStaticChart('port-static-in')
  const portStaticOut = portStaticChart('port-static-out')

  function portStatic_update(response_data) { /* 端口统计图数据更新 */
    const portStaticInLabel = response_data.charts.inport.map(e => e.name)
    const portStaticInData = response_data.charts.inport.map(e => e.y)
    const portStaticOutLabel = response_data.charts.outport.map(e => e.name)
    const portStaticOutData = response_data.charts.outport.map(e => e.y)

    portStaticIn.data.labels = portStaticInLabel
    portStaticIn.data.datasets[0] = {
      data: portStaticInData,
      borderWidth: 1,
      backgroundColor: ["#7cb5ec", "#f7a35c", "#90ee7e", "#7798BF", "#aaeeee", "#ff0066", "#eeaaee", "#55BF3B", "#DF5353", "#7798BF"]
    }
    portStaticIn.update()
    portStaticOut.data.labels = portStaticOutLabel
    portStaticOut.data.datasets[0] = {
      data: portStaticOutData,
      borderWidth: 1,
      backgroundColor: ["#7cb5ec", "#f7a35c", "#90ee7e", "#7798BF", "#aaeeee", "#ff0066", "#eeaaee", "#55BF3B", "#DF5353", "#7798BF"]
    }
    portStaticOut.update()
  }

  function trafficGroupTable_update(response_json) {
    function toThousands(num) {
      return (num || 0).toString().replace(/(\d)(?=(?:\d{3})+$)/g, '$1,');
    }
    const src = ['网内地址', '网外地址']
    const dst = ['网内地址', '网外地址', 'CERNET保留地址', 'CERNET主干地址', '私有地址', '组播地址', 'Unkown地址']
    const col = ['流数', '报文数', '字节数']

    const ingroupTable = document.getElementById('ingroup-body')
    const outgroupTable = document.getElementById('outgroup-body')
    const table = [
      { dom: ingroupTable, key: '入方向' },
      { dom: outgroupTable, key: '出方向' }
    ]
    for (const { dom, key } of table) {
      for (const src_name of src) {
        for (const dst_name of dst) {
          const newRow = dom.insertRow()
          if (dst[0] == dst_name) {
            const srcCell = newRow.insertCell()
            srcCell.innerText = src_name
            srcCell.rowSpan = dst.length
          }
          const dstCell = newRow.insertCell()
          dstCell.innerText = dst_name
          for (const col_name of col) {
            const newCell = newRow.insertCell()
            newCell.innerText = response_json[key][`源-${src_name}`][`宿-${dst_name}`][col_name]
          }
        }
      }
    }
  }

 

function update() {
  $.ajax({
    type: 'get',
    url: '/index_main/',
    contentType: "application/json; charset=utf-8",
    success(response_json) {
      totalTraffic_update(response_json)
      portStatic_update(response_json)
      console.log(response_json)
    }
  })
  $.ajax({
    type: 'get',
    url: '/index_traffic/',
    contentType: "application/json; charset=utf-8",
    success(response_json) {
      trafficGroupTable_update(response_json)
      console.log(response_json)
    }
  })
}

update()
totalTrafficBps.options.animation = false
totalTrafficPps.options.animation = false
portStaticIn.options.animation = false
portStaticOut.options.animation = false
setInterval(update, 10*60*1000)
console.log(111)

});
