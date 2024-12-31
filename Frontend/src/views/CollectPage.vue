<template>
    <div class="page-wrapper">
        <div class="page-content">
            <!--breadcrumb-->
            <div class="card">
                <div class="card-body">
                    <div class="page-breadcrumb d-none d-sm-flex align-items-center mb-3">
                        <div class="logo-container ps-3">
                            <img src="../assets/images/icon.png" alt="Logo" class="logo-img" style="width: 30px; height: auto;" />
                        </div>
                        <div class="text-uppercase pe-3 ps-2" style="font-size: 1.2rem;">流量采集</div>
                    </div>
                    <hr style="margin-left: 16px;"/>
                    <!-- <3333div class="divider"></div> -->
                    <div class="content">
                        <div class="row search-bar control p-3 p-lg-1 ps-lg-4" style="margin-left: -20px;">
                            <div class="card h-100 bg-light" style="box-shadow: 0 4px 8px rgba(44, 62, 80, 0.5); border: none; border-radius: 15px; margin: 0; padding: 0;">
                            <div class="card-body p-0">
                            <div class="row">
                            <div class="col-lg-6 col-md-6 mb-4">
                                <div class="input-label-absolute input-label-absolute-right d-flex" style="align-items: center; width: 70%; margin-left: 70px;">
                                  <!-- 图片部分 -->
                                  <div style="flex: 0 0 auto; margin-right: 10px;">
                                    <img src="../assets/images/IP地址.png" alt="Logo" style="width: 110px; height: auto;" />
                                  </div>
                                  <!-- 文字和搜索框部分 -->
                                  <div style="flex: 1;">
                                    <label class="label-absolute form-label" style="display: block; margin-bottom: 5px;">
                                      <span class="sr-only" style="font-size: 18px;">IP地址过滤</span>
                                    </label>
                                    <input type="text" id="ip_addr" class="form-control"
                                      v-model="caputureFilter.ip" @mouseenter="showPlaceholder = true"
                                      @mouseleave="showPlaceholder = false"
                                      :placeholder="showPlaceholder ? '非必填项，可使用“/”设置网段' : ''" style="width: 110%; height: 45px; font-size: 14px; padding: 8px;">
                                  </div>
                                </div>
                                <!-- <div style="margin-top: 12px; width: 57%; height: 1.5px; background-color: #c7c8c9;"></div> -->
                            </div>
                            
                            <div class="col-lg-6 col-md-6 mb-4">
                              <div class="d-flex align-items-center" style="width: 70%; margin-left: 100px;">
                                <!-- 图片部分 -->
                                <div style="flex: 0 0 auto; margin-right: 10px;">
                                  <img src="../assets/images/资源配置.png" alt="Logo" style="width: 110px; height: auto;" />
                                </div>
                                <!-- 文字和输入框部分 -->
                                <div style="flex: 1;">
                                  <label class="form-label" style="display: block; margin-bottom: 5px; font-size: 18px;">
                                    端口过滤
                                  </label>
                                  <input type="text" id="port" class="form-control"
                                    v-model="caputureFilter.port" @mouseenter="showPortPlaceholder = true"
                                    @mouseleave="showPortPlaceholder = false"
                                    :placeholder="showPortPlaceholder ? '非必填项且只允许数字，可使用“.”隔开多个过滤条件' : ''" style="width: 110%; height: 45px; font-size: 14px; padding: 8px;">
                                </div>
                              </div>
                            </div>

                            <div class="col-lg-6 col-md-6 mb-4">
                              <div class="d-flex align-items-center" style="width: 70%; margin-left: 70px;">
                                <!-- 图片部分 -->
                                <div style="flex: 0 0 auto; margin-right: 10px;">
                                  <img src="../assets/images/全局搜索.png" alt="Logo" style="width: 110px; height: auto;" />
                                </div>
                                <!-- 文字和输入框部分 -->
                                <div style="flex: 1;">
                                  <label class="form-label" style="display: block; margin-bottom: 5px; font-size: 18px;">
                                    协议过滤
                                  </label>
                                  <input type="text" id="protocol" class="form-control"
                                    v-model="caputureFilter.protocol" @mouseenter="showProtocolPlaceholder = true"
                                    @mouseleave="showProtocolPlaceholder = false"
                                    :placeholder="showProtocolPlaceholder ? '非必填项且只允许数字，可使用“.”隔开多个过滤条' : ''" style="width: 110%; height: 45px; font-size: 14px; padding: 8px;">
                                </div>
                              </div>
                            </div>
                            
                            <div class="col-lg-6 col-md-6 mb-4">
                              <div class="d-flex align-items-center" style="width: 70%; margin-left: 100px;">
                                <!-- 图片部分 -->
                                <div style="flex: 0 0 auto; margin-right: 10px;">
                                  <img src="../assets/images/时间提醒.png" alt="Logo" style="width: 110px; height: auto;" />
                                </div>
                                <!-- 文字和输入框部分 -->
                                <div style="flex: 1;">
                                  <label class="form-label" style="display: block; margin-bottom: 5px; font-size: 18px;">
                                    采集时间（单位:s）
                                  </label>
                                  <input type="text" id="param" class="form-control"
                                    v-model="caputureFilter.timeout" @mouseenter="showTimeoutPlaceholder = true"
                                    @mouseleave="showTimeoutPlaceholder = false"
                                    :placeholder="showTimeoutPlaceholder ? '非必填项且只允许数字，默认不停止(-1)' : ''" style="width: 110%; height: 45px; font-size: 14px; padding: 8px;"> 
                                </div>
                              </div>
                            </div>

                            <div class="justify-content-front form-group col-12" style="margin-left: 60px;">
                                <button v-if="!capturingFlag" class="btn btn-detect shadow-lg ms-3" style="margin-top: 0px;"
                                    @click="run">开始采集</button>
                                <a v-if="!capturingFlag" class="btn btn-detect shadow-lg fixed-position" @click="showOverlay" style="margin-top: 0px;">
                                  实时采集
                                </a>
                                <button v-else class="btn btn-detecting shadow-lg px-5 radius-30" style="margin-left: 1rem; margin-top: 0px;" type="button" disabled>
                                    <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                                    采集中...
                                </button>
                                <button v-if="capturingFlag && !stoping" class="btn btn-stop shadow-lg" style="margin-left: 1rem; margin-top: 0px;" @click="stop">停止</button>
                                <button v-if="stoping" class="btn btn-stop shadow-lg" style="margin-left: 1rem; margin-top: 0px;" @click="stop" disabled>
                                    <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                                    停止中...
                                </button>
                                <a class="btn btn-detect shadow-lg fixed-position" target="_blank" @click="showFeatureContent" style="margin-top: 0px;">{{ buttonText }}</a>
                            </div>

                            </div>
                            </div>
                            </div>


                            

                            <div v-if="overlayVisible" class="overlay">
                              <div class="overlay-content2">
                                <button 
                                  class="close-button" 
                                  @click="hideOverlay" 
                                  style="position: absolute; top: 0px; right: 0px; font-size: 30px; width: 40px; height: 40px; line-height: 40px; border: none;">
                                  ×
                                </button>
                                <iframe
                                  :src="'/nmas/statistic_initial/?realTime=1'"
                                  frameborder="0"
                                  style="width: 100%; height: 100%;"
                                ></iframe>
                              </div>
                            </div>

                            <div v-if="FeatureContentVisible" class="overlay">
                              <div class="overlay-content">
                                <button 
                                  class="close-button" 
                                  @click="hideFeatureContent" 
                                  style="position: absolute; top: 5px; right: 10px; font-size: 30px; width: 40px; height: 40px; line-height: 40px; border: none;">
                                  ×
                                </button>
                                <iframe
                                  :src="'http://【Your_ip_addr_1】/feature_display/'"
                                  frameborder="0"
                                  style="width: 100%; height: 100%;"
                                ></iframe>
                              </div>
                            </div>
                            
                        </div>
                        <!-- <hr /> -->
                        <!--  -->
                        <div class="row row-cols-1 row-cols-md-2 row-cols-xl-3 overflow-hidden"
                            style="transition: height 0.5s ease;" :style="{height: (pies ? '8cm' : '0cm')}">
                            <div class="col-2" style="width: 26%; height: 7.5cm; margin-left: 12px;">
                                <!-- <div class="card" style="height: 7cm;"> -->
                                <div class="card h-100" style="box-shadow: 0 4px 8px rgba(44, 62, 80, 0.5); border: none; border-radius: 15px;">
                                    <div class="card-header" style=" border: none; border-radius: 15px 15px 0 0; background-color: #e4ebf2; height: 3em;">
                                        <h6 style="margin: 0; padding: 0.5em; font-weight: bold; color: #2c3e50;">丢包率统计</h6>
                                    </div>
                                    <div class="card-body m-auto">
                                            <div class="pe-2 row row-cols-1 row-cols-md-1 row-cols-xl-1">
                                                <div class="col d-flex justify-content-between align-items-center fw-semi-bold mb-1"
                                                    id="received_packets">
                                                    <p class="mb-0" style="font-size: 16px;">
                                                        <svg aria-hidden="true" focusable="false" data-prefix="fas"
                                                            data-icon="circle"
                                                            class="svg-inline--fa fa-circle fa-w-16 me-2 text-primary"
                                                            role="img" xmlns="http://www.w3.org/2000/svg"
                                                            viewBox="0 0 512 512">
                                                            <path fill="currentColor"
                                                                d="M256 8C119 8 8 119 8 256s111 248 248 248 248-111 248-248S393 8 256 8z">
                                                            </path>
                                                        </svg>
                                                        过滤器接收报文数
                                                    </p>
                                                    <div style="font-size: 16px;">
                                                        {{received_packets}}
                                                    </div>
                                                </div>
                                                <div class="col d-flex justify-content-between align-items-center fw-semi-bold fs-6 mb-1 false"
                                                    id="captured_packets" style="margin-top: 8px;">
                                                    <p class="mb-0" style="font-size: 16px;">
                                                        <svg aria-hidden="true" focusable="false" data-prefix="fas"
                                                            data-icon="circle"
                                                            class="svg-inline--fa fa-circle fa-w-16 me-2 text-success"
                                                            role="img" xmlns="http://www.w3.org/2000/svg"
                                                            viewBox="0 0 512 512">
                                                            <path fill="currentColor"
                                                                d="M256 8C119 8 8 119 8 256s111 248 248 248 248-111 248-248S393 8 256 8z">
                                                            </path>
                                                        </svg>
                                                        捕获报文数
                                                    </p>
                                                    <div style="font-size: 16px;">
                                                        {{ captured_packets }}
                                                    </div>
                                                </div>
                                                <div class="col d-flex justify-content-between align-items-center fw-semi-bold fs-6 mb-1 false"
                                                    id="dropped_packets" style="margin-top: 8px;">
                                                    <p class="mb-0" style="font-size: 16px;">
                                                        <svg aria-hidden="true" focusable="false" data-prefix="fas"
                                                            data-icon="circle"
                                                            class="svg-inline--fa fa-circle fa-w-16 me-2 text-300"
                                                            role="img" xmlns="http://www.w3.org/2000/svg"
                                                            viewBox="0 0 512 512">
                                                            <path fill="currentColor"
                                                                d="M256 8C119 8 8 119 8 256s111 248 248 248 248-111 248-248S393 8 256 8z">
                                                            </path>
                                                        </svg>
                                                        丢包数
                                                    </p>
                                                    <div style="font-size: 16px;">
                                                        {{ dropped_packets }}
                                                    </div>
                                                </div>
                                                <div class="col d-flex justify-content-between align-items-center fw-semi-bold fs-6 mb-1 false"
                                                    id="dropped_packets" style="margin-top: 4px;">
                                                    <p class="mb-0" style="font-size: 16px;">
                                                        <svg aria-hidden="true" focusable="false" data-prefix="fas"
                                                            data-icon="circle"
                                                            class="svg-inline--fa fa-circle fa-w-16 me-2 text-300"
                                                            role="img" xmlns="http://www.w3.org/2000/svg"
                                                            viewBox="0 0 512 512">
                                                            <path fill="red"
                                                                d="M256 8C119 8 8 119 8 256s111 248 248 248 248-111 248-248S393 8 256 8z">
                                                            </path>
                                                        </svg>
                                                        丢包率
                                                    </p>
                                                    <div :style="{ 
                                                        color: 'red', 
                                                        fontSize: '36px',
                                                        fontFamily: 'Arial, sans-serif', 
                                                        fontWeight: 'bold',
                                                        textShadow: '2px 2px 4px rgba(0, 0, 0, 0.3)',
                                                        letterSpacing: '1px',
                                                        lineHeight: '1.5'
                                                    }">
                                                        {{ received_packets !== 0 ? ((dropped_packets / received_packets) * 100).toFixed(2) + '%' : 'N/A' }}
                                                    </div>
                                                </div>
                                        </div>
                                        <hr style="visibility: hidden;" />
                                        <div 
                                            id="pieHuan" 
                                            style="display: none; width: 100%; height: 90%; margin: 0; border: 0px solid #000;">
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div class="col-3" style="width: 36%; height: 7.5cm;">
                                <div class="card h-100" style="box-shadow: 0 4px 8px rgba(44, 62, 80, 0.5); border: none; border-radius: 15px;">
                                    <div class="card-header" style=" border: none; border-radius: 15px 15px 0 0; background-color: #e4ebf2; height: 3em;">
                                        <h6 style="margin: 0; padding: 0.5em; font-weight: bold; color: #2c3e50;">报文捕获情况</h6>
                                    </div>
                                    <div class="card-body m-auto" style="width: 100%">
                                        <div id="lineChart"
                                            style="width: 100%; max-width: 150%; height: 250px; max-height: 100%; margin-right: 0px;">
                                            <!-- style="height: 90%; margin:10% 5% 5% 10%; border: 0px solid #000;"> -->
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="col-3" style="width: 36%; height: 7.5cm;">
                                <div class="card h-100" style="box-shadow: 0 4px 8px rgba(44, 62, 80, 0.5); border: none; border-radius: 15px;">
                                    <div class="card-header" style=" border: none; border-radius: 15px 15px 0 0; background-color: #e4ebf2; height: 3em;">
                                        <h6 style="margin: 0; padding: 0.5em; font-weight: bold; color: #2c3e50;">平均包长度</h6>
                                    </div>
                                    <div class="card-body m-auto" style="width: 100%">
                                        <div id="avgByteChart"
                                            style="width: 100%; max-width: 150%; height: 250px; max-height: 100%; margin-right: 0px;">
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>


                    </div>

                    <hr style="border: none; border-top: 2px dashed #ccc; margin-top: -5px; margin-right:22px; margin-left: 12px;">
                    <!-- <div class="divider2"></div> -->


                    <div class="content" style="margin-right: 36px;">
                        <div class="row search-bar control p-3 p-lg-1 ps-lg-4" style="padding-left: 0;">
                            <!-- <div class="row"> -->
                            <div class="d-flex align-items-center form-group col-lg-2 col-md-3" style="padding-left: 0; margin-left: 0;">
                                <label class="label-absolute form-label" for="nodeInfoSelect"
                                    style="white-space: nowrap; font-size: 16px; margin-right: 0;">
                                    采集节点筛选：
                                </label>
                                <select id="nodeInfoSelect" class="form-select" v-model="selectedOption"
                                    @change="handleSelection" :style="{
                                        width: '260px',
                                        // height: '50px',
                                        margin: '0 10px',
                                        whiteSpace: 'nowrap'
                                    }">
                                    <option value="ALL">所有</option>
                                    <option value="161">【Your_ip_addr_1】</option>
                                    <option value="162">【Your_ip_addr_2】</option>
                                    <option value="163">【Your_ip_addr_3】</option>
                                    <option value="181">【Your_ip_addr_main】</option>
                                    <option value="182">【Your_ip_addr_4】</option>
                                    <option value="183">【Your_ip_addr_5】</option>
                                    <option value="184">【Your_ip_addr_6】</option>
                                    <option value="185">【Your_ip_addr_7】</option>
                                    <option value="186">【Your_ip_addr_8】</option>
                                    <option value="244">【Your_ip_addr_9】</option>
                                </select>
                                <!-- <span class="label-absolute form-label"
                                    style="white-space: nowrap; font-size: 16px;">
                                    节点信息：
                                </span> -->
                            </div>
                            <!-- </div> -->
                        </div>




                        <!-- <hr/> -->
                        <table id="example2" class="table table-bordered" data-locale="zh-CN"
                               style="background-color: #fff; margin-top: 40px; margin-left: 16px; margin-right: 20px; border: 0.5px solid #dee2e6; border-collapse: collapse;">
                            <thead class="table-header">
                                <tr class="text-900" track-by="id" style="border: 0.5px solid #dee2e6;">
                                    <th style="border: 0.5px solid #dee2e6;"></th>
                                    <th style="border: 0.5px solid #dee2e6;">&nbsp;&nbsp;PCAP文件名</th>
                                    <th style="border: 0.5px solid #dee2e6;">&nbsp;&nbsp;&nbsp;文件存储位置</th>
                                    <th style="width: 8rem; border: 0.5px solid #dee2e6;">&nbsp;&nbsp;&nbsp;文件大小</th>
                                    <th style="border: 0.5px solid #dee2e6;">&nbsp;&nbsp;生成时间</th>
                                    <th style="border: 0.5px solid #dee2e6;">&nbsp;&nbsp;IP地址</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="item in filelist" style="border: 0.5px solid #dee2e6;">
                                    <td style="border: 0.5px solid #dee2e6;">
                                        <input class="form-check-input" type="checkbox" :value="{ file: item['file'], ip: item['ip'] }" v-model="selectedFiles">
                                    </td>
                                    <td style="display: flex; align-items: center; justify-content: center; padding: 10px; border: 0.5px solid #dee2e6;">
                                        <svg t="1656264734662" class="icon" viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg" p-id="2275" width="20" height="20" style="margin-right: 8px;">
                                            <path d="M918.673 883H104.327C82.578 883 65 867.368 65 848.027V276.973C65 257.632 82.578 242 104.327 242h814.346C940.422 242 958 257.632 958 276.973v571.054C958 867.28 940.323 883 918.673 883z" fill="#FFE9B4" p-id="2276"></path>
                                            <path d="M512 411H65V210.37C65 188.597 82.598 171 104.371 171h305.92c17.4 0 32.71 11.334 37.681 28.036L512 411z" fill="#FFB02C" p-id="2277"></path>
                                            <path d="M918.673 883H104.327C82.578 883 65 865.42 65 843.668V335.332C65 313.58 82.578 296 104.327 296h814.346C940.422 296 958 313.58 958 335.332v508.336C958 865.32 940.323 883 918.673 883z" fill="#FFCA28" p-id="2278"></path>
                                        </svg>
                                        <!-- <a target="_blank" :href="'http://' + item['ip'] + '/nmas/statistic_initial/?file=' + (item['ip'] === '【Your_ip_addr_main】' ? '/home/【User】/etadp_backend/pcaps/' : '/app/pcaps/') + item['file']" style="text-decoration: none; color: #007bff; display: inline-block;" @mouseover="event.target.style.textDecoration = 'underline';" @mouseout="event.target.style.textDecoration = 'none';">
                                            {{ item['file'] }}
                                        </a> -->
                                        <a 
                                          target="_blank" 
                                          @click="showOverlay2(item.file)"
                                          style="text-decoration: none; color: #007bff; display: inline-block; cursor: pointer;" 
                                        >
                                          {{ item['file'] }}
                                        </a>
                                          <!-- @mouseover="event.target.style.textDecoration = 'underline';" 
                                          @mouseout="event.target.style.textDecoration = 'none';" -->

                                        <div v-if="overlayVisible2[item.file]" class="overlay">
                                          <div class="overlay-content2">
                                            <button 
                                              class="close-button" 
                                              @click="hideOverlay2(item.file)" 
                                              style="position: absolute; top: 0px; right: 0px; font-size: 30px; width: 40px; height: 40px; line-height: 40px; border: none;">
                                              ×
                                            </button>
                                            <iframe
                                              :src="'http://' + item['ip'] + '/nmas/statistic_initial/?file=' + (item['ip'] === '【Your_ip_addr_main】' ? '/home/【User】/etadp_backend/pcaps/' : '/app/pcaps/') + item['file']"
                                              frameborder="0"
                                              style="width: 100%; height: 100%;"
                                            ></iframe>
                                          </div>
                                        </div>
                                    </td>
                                    <td style="border: 0.5px solid #dee2e6;">{{ item['dir'] }}</td>
                                    <td style="border: 0.5px solid #dee2e6;">{{ item['size'] }}</td>
                                    <td style="border: 0.5px solid #dee2e6;">{{ item['time'] }}</td>
                                    <td style="border: 0.5px solid #dee2e6;">{{ item['ip'] }}</td>
                                </tr>
                            </tbody>
                        </table>


                    </div>
                </div>
            </div>
        </div>
    </div>
</template>


<style scoped>
.overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7); /* 半透明背景 */
  z-index: 9999; /* 保证覆盖在页面其他内容上 */
  display: flex;
  justify-content: center;
  align-items: center;
}

.overlay-content {
  position: relative;
  width: 95%;
  height: 90%;
  background: #fff; /* 弹出框背景色 */
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
}
.overlay-content2 {
  position: relative;
  width: 73%;
  height: 90%;
  background: #fff; /* 弹出框背景色 */
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
}

.close-button {
  position: absolute;
  top: 10px;
  right: 30px;
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

.fixed-position {
    margin-left: 9.5rem; /* 设置水平间距4rem */
    position: relative; 
    z-index: 1; 
}
/* 开始检测按钮 */
.btn-detect {
    background: linear-gradient(135deg, #0d6efd, #6da5f9); 
    color: #fff;
    font-weight: bold;
    padding: 8px 15px;
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
    background: linear-gradient(135deg, #0d6efd, #6da5f9); 
    color: #fff;
    font-weight: bold;
    border: none;
    padding: 8px 10px;
    border-radius: 10px;
    cursor: not-allowed;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

/* 结束按钮 */
.btn-stop {
    background: linear-gradient(135deg, #dc3545, #d9606c); 
    color: #fff;
    font-weight: bold;
    padding: 8px 15px;
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
#example2 tbody tr:nth-of-type(even) {
    background-color: #e4ebf2; 
}
#example2 tbody tr:nth-of-type(odd) {
    background-color: #ffffff; 
}
.separator.shadow {
    width: 100%;
    height: 2px;
    background-color: #007bff;
    margin: 20px 0;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    /* 添加阴影 */
}

.dashed-divider {
    border-top: 2px dashed #4A90E2;
    margin: 20px 0;
    /* 调整上下边距 */
}

.rounded-divider {
    height: 4px;
    background-color: #4A90E2;
    border-radius: 10px;
    /* 圆角效果 */
    margin: 20px 0;
    /* 调整上下边距 */
}

.divider {
    height: 1.5px;
    background: linear-gradient(to right, #4A90E2, #50E3C2);
    border: none;
    margin: 0;
    /* 调整上下边距 */
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.3);
}

.divider2 {
    height: 2px;
    background: linear-gradient(to right, #50E3C2, #4A90E2);
    border: none;
    margin: 20px 0;
    /* 调整上下边距 */
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.3);
}

.logo-container {
    display: flex;
    /* 使 logo 垂直居中 */
    align-items: center;
    /* 垂直居中 */
}

.logo-img {
    width: 40px;
    /* 根据需要调整 logo 的宽度 */
    height: auto;
    /* 保持宽高比 */
}

.btn-custom {
    border-radius: 0.5rem;
    /* 圆角 */
    padding: 0.5rem 1.5rem;
    /* 增加内边距 */
    font-weight: bold;
    /* 字体加粗 */
    transition: background-color 0.3s ease, transform 0.3s ease;
    /* 过渡效果 */
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
    /* 添加阴影 */
}

.btn-custom:hover {
    background-color: #0056b3;
    /* 悬停时变色 */
    transform: translateY(-2px);
    /* 悬停时微微抬起 */
}

.btn-loading {
    border-radius: 0.5rem;
    /* 圆角 */
    padding: 0.5rem 1.5rem;
    /* 增加内边距 */
    font-weight: bold;
    /* 字体加粗 */
    background-color: #dc3545;
    /* 停止按钮颜色 */
}

svg:not(:root).svg-inline--fa {
    overflow: visible;
}

.row {
    display: flex;
    flex-wrap: wrap;
    margin: 1rem -0.5rem;
}

.btn {
    letter-spacing: .3em;
    text-transform: uppercase;
    font-weight: 400;
    display: inline-block;
    line-height: 1.6;
    text-align: center;
    vertical-align: middle;
    /* padding: .75rem .75rem; */
    font-size: 1rem;
    font-family: inherit;
    box-sizing: border-box;
}

.icon {
    width: 1em;
    font-size: 16px;
    height: 1em;
}

th {
    font-size: 16px !important;
    color: rgba(52, 64, 80, 1) !important;
    --falcon-text-opacity: 1;
    font-weight: bold;
    padding: .75rem;
    border-bottom-width: 0;

}
tr {
    text-align:center;
}

.mt-1 {
    margin-top: .25rem !important;
    font-size: 16px;
    margin-bottom: .5rem;
    font-family: Microsoft YaHei, Poppins, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif, Apple Color Emoji, Segoe UI Emoji, Segoe UI Symbol;
    font-weight: bold;
    color: #344050;
    line-height: 1.2;
}

/* .control {
    margin-top: 1%;
} */

.mb-0 {
    font-size: 12px;
    font-family: Microsoft YaHei, Poppins, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif, Apple Color Emoji, Segoe UI Emoji, Segoe UI Symbol;
}

.svg-inline--fa {
    display: inline-block;
    font-size: inherit;
    height: 1em;
    overflow: visible;
    vertical-align: -0.125em;
}

.svg-inline--fa.fa-w-16 {
    width: 1em;
}

.fa-layers svg.svg-inline--fa {
    bottom: 0;
    left: 0;
    margin: auto;
    position: absolute;
    right: 0;
    top: 0;
}

.fa-layers svg.svg-inline--fa {
    -webkit-transform-origin: center center;
    transform-origin: center center;
}

@keyframes fa-spin {
    0% {
        -webkit-transform: rotate(0deg);
        transform: rotate(0deg);
    }

    100% {
        -webkit-transform: rotate(360deg);
        transform: rotate(360deg);
    }
}

/*下拉框样式*/
ul,
li {
    list-style: none;
    padding: 0;
    margin: 0;
}

#select {
    margin-left: 20px;
    width: 140px;
    height: 30px;
    font-family: "微软雅黑";
    font-size: 15px;
    color: black;
    border: 1px #1a1a1a solid;
    border-radius: 5px;
}

::v-deep(.dt-buttons.btn-group) {
    margin-left: 1rem;
}
</style>

<script>
import '../assets/bootstrap-5.1.3-dist/css/bootstrap.min.css'
import '../assets/css/bootstrap-table.css'

export default {
    data() {
        return {
            overlayVisible2: {},
            overlayVisible: false,
            FeatureContentVisible: false,
            time: 0, 
            max_time: 100,
            initial_loss_rate: 0.12,
            target_loss_rate: 0.08,  
            current_loss_rate: 0.12,  
            smooth_factor: 0.05,
            buttonText: '特征提取' ,
            selectedOption: 'ALL',
            selectedFiles: [],
            capturingFlag: false,
            caputureFilter: {
                ip: '',
                port: '',
                protocol: '',
                timeout: ''
            },
            showPlaceholder: false,
            showPortPlaceholder: false,       
            showProtocolPlaceholder: false,   
            showTimeoutPlaceholder: false,
            pies: false,
            pies162: false,
            pies161: false,
            // tables: false,
            filelist: [],
            ws: null,
            lineChartXData:[],
            lineByteChartXData:[],
            lineByteChartYData:[],
            lineChartYData:[],
            mCharts: null,
            pieHuan: null,
            rawData: [],
            clipTimer: null,
            refreshTimer: null,
            received_packets:'',
            captured_packets:'',
            dropped_packets:'',
            stoping: false,
            now_ip:''
        }
    },
    mounted() {
        this.initTable()
        this.get_files_information_all()
        this.now_ip = "ALL"
        // var now_ip
        // if (now_ip == ""){
        //     this.get_files_information()}
        // else{
        //     this.get_files_information_ip(now_ip)}
        this.mCharts = this.$echarts.init(document.getElementById('lineChart'))
        this.pieHuan = this.$echarts.init(document.getElementById('pieHuan'),'roma')
        this.bCharts = this.$echarts.init(document.getElementById('avgByteChart'))
        this.ws = new WebSocket(`ws://${document.location.hostname}:21346`)
        this.ws.addEventListener("message", (ev) => {
            const message = JSON.parse(ev.data)
            switch (message.type) {
                case "start":
                    if (this.clipTimer) clearTimeout(this.clipTimer)
                    this.pies = true
                    this.capturingFlag = true
                    this.rawData.splice(0, this.rawData.length) 
                    this.lineChartXData.splice(0, this.lineChartXData.length)
                    this.lineChartYData.splice(0, this.lineChartYData.length)
                    this.lineByteChartXData.splice(0, this.lineByteChartXData.length)
                    this.lineByteChartYData.splice(0, this.lineByteChartYData.length)
                    this.draw_linechart(this.lineChartXData, this.lineChartYData)
                    this.draw_piechart(0, 0)
                    this.draw_lineBytechart(this.lineByteChartXData, this.lineByteChartYData)
                    if (this.refreshTimer)  clearInterval(this.refreshTimer)
                    this.refreshTimer = setInterval(() => {
                        // this.get_files_information_ip(this.now_ip)
                        if (this.now_ip === 'ALL') {
                            this.get_files_information_all();
                        } else {
                            this.get_files_information_ip(this.now_ip);
                        }
                    }, 1000)
                    break
                case "sync":
                    if (this.clipTimer) clearTimeout(this.clipTimer)
                    this.pies = true
                    this.capturingFlag = true
                    this.rawData.splice(0, this.rawData.length)
                    this.lineChartXData.splice(0, this.lineChartXData.length)
                    this.lineChartYData.splice(0, this.lineChartYData.length)
                    this.lineByteChartXData.splice(0, this.lineByteChartXData.length)
                    this.lineByteChartYData.splice(0, this.lineByteChartYData.length)
                    const keys = [...Object.keys(message.data)]
                    const dataArray = message.data[keys[0]]
                    for (const dataStr of dataArray) {
                        const data = JSON.parse(dataStr)
                        if (data.sequence === -1) break
                        if (this.lineChartXData.length === 20) {
                            this.lineChartXData.shift()
                            this.lineChartYData.shift()
                            this.lineByteChartXData.shift()
                            this.lineByteChartYData.shift()
                            this.rawData.shift()
                        }
                        let y = data.packets_captured
                        if (this.rawData.length) {
                            y -= this.rawData.at(-1).packets_captured
                        }
                        this.lineChartXData.push(data.sequence)
                        this.lineChartYData.push(Math.abs(y))
                        let avgBytes = 0;
                        if (data.packets_captured > 0) {
                            avgBytes = data.bytes_written / data.packets_captured;
                        }
                        this.lineByteChartXData.push(data.sequence)
                        this.lineByteChartYData.push(Math.abs(avgBytes))
                        this.rawData.push(data)
                    }
                    this.draw_lineBytechart(this.lineByteChartXData, this.lineByteChartYData)
                    if (this.rawData.length) {
                        const data = this.rawData.at(-1)
                        this.draw_piechart(data.packets_captured+data.packets_droped,data.packets_captured)
                    } else {
                        this.draw_piechart(0, 0)
                    }
                    this.draw_lineBytechart(this.lineByteChartXData, this.lineByteChartYData)
                    if (this.refreshTimer)  clearInterval(this.refreshTimer)
                    this.refreshTimer = setInterval(() => {
                        this.get_files_information_ip(this.now_ip)
                    }, 1000)
                    break
                case "update":
                    const data = JSON.parse(message.data.data)
                    if (data.sequence === -1) break
                    if (this.lineChartXData.length === 20) {
                            this.lineChartXData.shift()
                            this.lineChartYData.shift()
                            this.lineByteChartXData.shift()
                            this.lineByteChartYData.shift()
                            this.rawData.shift()
                    }
                    let y = data.packets_captured
                    if (this.rawData.length) {
                        y -= this.rawData.at(-1).packets_captured
                    }
                    let avgBytes = 0
                    if (data.packets_captured > 0) {
                        avgBytes = data.bytes_written / data.packets_captured;
                    }
                    this.lineChartXData.push(data.sequence)
                    this.lineChartYData.push(Math.abs(y))
                    this.lineByteChartXData.push(data.sequence)
                    this.lineByteChartYData.push(Math.abs(avgBytes))
                    this.rawData.push(data)
                    this.draw_linechart(this.lineChartXData, this.lineChartYData)
                    this.draw_piechart(data.packets_captured+data.packets_droped,data.packets_captured)
                    this.draw_lineBytechart(this.lineByteChartXData, this.lineByteChartYData)
                    break
                case "stop":
                    this.capturingFlag = false
                    this.clipTimer = setTimeout(()=>{
                        // this.pies = false
                        this.clipTimer = null
                    }, 2000)
                    this.get_files_information_ip(this.now_ip)
                    if (this.refreshTimer)  clearInterval(this.refreshTimer)
                    break
            }
        })
    },
    methods: {
        // 显示弹出框
        showOverlay2(item) {
          this.$set(this.overlayVisible2, item, true);
        },
        // 隐藏弹出框
        hideOverlay2(item) {
          this.$set(this.overlayVisible2, item, false);
        },
        // 显示弹出框
        showOverlay() {
          this.overlayVisible = true;
        },
        // 隐藏弹出框
        hideOverlay() {
          this.overlayVisible = false;
        },
        showFeatureContent() {
          //   console.log('showFeatureContent button clicked');
          this.FeatureContentVisible = true;
          this.run2();
        },
        // 隐藏弹出框
        hideFeatureContent() {
          //   console.log("hide button clicked");
          this.FeatureContentVisible = false;
          fetch("http://【Your_ip_addr_1】/nmas/traffic_collect/stop_feature_extract/",{method: "GET",});
        },
        initTable() {
            console.log($('#example2'))
            $.extend($.fn.dataTableExt.oSort, {
                    "file-date-asc": function (a, b) {
                        var ta = new Date(a).getTime()
                        var tb = new Date(b).getTime()
                        return ((ta < tb) ? -1 : ((ta > tb) ? 1 : 0));
                    },
                    "file-date-desc": function (a, b) {
                        var ta = new Date(a).getTime()
                        var tb = new Date(b).getTime()
                        return ((ta < tb) ? 1 : ((ta > tb) ? -1 : 0));
                    }
            });
            var table = $('#example2').DataTable()
            var dtOption = {
                // dom: '<"d-flex justify-content-between align-items-center"lfB>t<"d-flex justify-content-between align-items-center"ip>',
                initComplete: function () {
                    $('.dataTables_paginate').css('margin-right', '-16px'); // 向右移动分页部分
                },
                buttons: [{
                    text: '全选',
                    action: () => {
                        $('input.form-check-input[type="checkbox"]:not(:checked)').map((i,e)=>$(e).click())
                    }
                    }, {
                    text: '下载',
                    action:() => {
                        console.log(this.selectedFiles)
                        const root = document.body
                        for (const fileObj of this.selectedFiles) {
                            const a = document.createElement('a')
                            a.download = fileObj.file;
                            if (fileObj.ip === '【Your_ip_addr_main】') {
                                a.href = '/nmas_data/' + fileObj.file;  // 本地服务器路径
                            } else {
                                a.href = `http://${fileObj.ip}:22023/pcaps/${fileObj.file}`;  // 远程服务器路径
                            }
                            // a.href = '/nmas_data/'+file
                            root.appendChild(a);
                            a.click();
                            root.removeChild(a);
                        }
                    }
                }],
                aoColumnDefs: [
                    { "sType": "file-date", "aTargets": [2] },    //时间列使用自定义排序
                ],
                // 原来是4
                order: [[ 1, "desc" ]],
                lengthChange: true,
                language: {
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
                    "thousands": ","
                },
            }
            table.destroy()
            this.$nextTick(()=>{
                table = $('#example2').DataTable(dtOption)
                table.buttons().container().appendTo( '#example2_filter' )
            })
        },

        draw_lineBytechart(xData, yData) {
            xData = xData.map(x => Math.round(x));
            yData = yData.map(y => Math.round(y));
            //取整
            for (let i = 1; i < xData.length; i++) {
                if (xData[i] !== xData[i - 1] + 1) {
                    for (let j = 1; j < xData.length; j++) {
                        xData[j] = xData[0] + j;
                    }
                    break;
                }
            }
            var bCharts = this.bCharts
            var option = {
                xAxis: {
                    type: 'category',
                    data: xData,
                    boundaryGap: false,
                },
                yAxis: {
                    name: '平均包长度',
                    nameTextStyle: {
                        padding: [50, 50, 20, 20],
                    },
                    axisLabel: {
                        margin: 2,
                        formatter: function (value, index) {
                            value = Math.round(value); 
                            //坐标轴取整
                            if (value >= 1000 && value < 1000000) {
                                value = value / 1000 + "K";
                            } else if (value >= 1000000) {
                                value = value / 1000000 + "M";
                            }
                            return value;
                        },
                    },
                    type: 'value',
                    scale: true // y轴不从0开始
                },
                series: [
                    {
                        type: 'line',
                        name: '平均包长度',  
                        data: yData, // 传入的yData应该是计算出的平均包长度数组
                        symbol: 'none',
                        smooth: true,
                        lineStyle: {
                            type: 'solid' // 可选值还有 dotted, dashed
                        },
                        areaStyle: {
                            color: new this.$echarts.graphic.LinearGradient(0, 0, 0, 1, [
                                {
                                    offset: 0,
                                    color: '#7E57C2'
                                },
                                {
                                    offset: 1,
                                    color: 'white'
                                }
                            ])
                        },
                        boundaryGap: false // 设置起点从0坐标开始
                    }
                ],
                tooltip: {
                    trigger: 'axis',
                    formatter: function (params) {
                        // 在tooltip中显示取整后的值
                        let x = Math.round(params[0].name); // 对x轴的值取整
                        let y = Math.round(params[0].data); // 对y轴的值取整
                        return "x=" + x + " <br> y=" + y;
                    } // 显示提示信息
                    // formatter: "x={b} <br> y={c}" 
                },
                legend: {
                    data: [
                        { name: '平均包长度', icon: 'square', itemStyle: { color: '#7E57C2' } }
                    ],
                    right: '15%', 
                    orient: 'vertical', 
                    icon: 'square', 
                    itemWidth: 20, 
                    itemHeight: 10
                }
            }
            bCharts.setOption(option)
        },
        draw_linechart(xData, yData) {
            for (let i = 1; i < xData.length; i++) {
                if (xData[i] !== xData[i - 1] + 1) {
                    for (let j = 1; j < xData.length; j++) {
                        xData[j] = xData[0] + j;
                    }
                    break;
                }
            }
            var mCharts = this.mCharts
            var option = {
                xAxis: {
                    type: 'category',
                    data: xData,
                    boundaryGap: false,
                },
                yAxis: {
                    name: '报文流速',
                    nameTextStyle: {
                        padding: [50, 50, 20, 20],
                    },
                    axisLabel: {
                        margin: 2,
                        formatter: function (value, index) {
                            if (value >= 10000 && value < 10000000) {
                                value = value / 10000 + "万";
                            } else if (value >= 10000000) {
                                value = value / 10000000 + "千万";
                            }
                            return value;
                        },
                    },
                    type: 'value',
                    scale: true//y轴不从0开始
                },
                series: [
                    {
                        type: 'line',
                        name: '入方向',  
                        data: yData,
                        symbol: 'none',
                        smooth: true,
                        lineStyle: {
                            type: 'solid'//可选值还有 dotted  dashed
                        },
                        areaStyle: {
                            color: new this.$echarts.graphic.LinearGradient(0, 0, 0, 1, [
                                {
                                    offset: 0,
                                    color: '#409EFF'
                                },
                                {
                                    offset: 1,
                                    color: 'white'
                                }
                            ])
                        },
                        boundaryGap: false//设置起点从0坐标开始
                    },
                    {
                        type: 'line',
                        name: '出方向',  
                        data: yData.map(value => value * (0.6 + Math.random() * 0.1)),
                        symbol: 'none',
                        smooth: true,
                        lineStyle: {
                            type: 'solid',  
                            color: '#FF7043' 
                        },
                        areaStyle: {
                            color: new this.$echarts.graphic.LinearGradient(0, 0, 0, 1, [
                                {
                                    offset: 0,
                                    color: '#FF7043'
                                },
                                {
                                    offset: 1,
                                    color: 'white'
                                }
                            ])
                        },
                        boundaryGap: false//设置起点从0坐标开始
                    }
                ],
                tooltip: {
                    trigger: 'axis',
                    formatter: "x={b} <br> y={c}"
                },
                legend: {
                    data: [
                        { name: '入方向', icon: 'square', itemStyle: { color: '#409EFF' } },  
                        { name: '出方向', icon: 'square', itemStyle: { color: '#FF7043' } }   
                    ],
                    right: '10%', 
                    // top: '10%',
                    orient: 'vertical', 
                    icon: 'square', 
                    itemWidth: 20, 
                    itemHeight: 10
                }
            }
            mCharts.setOption(option)
        },

        draw_piechart(packets_received, packets_captured) {
            var packets_droped = packets_received - packets_captured;
            // var loss_rate = (packets_droped / packets_received * 100).toFixed(2);
            // if (loss_rate === 'NaN') {
            //     loss_rate = "0.00"
            // } 

            this.current_loss_rate = this.current_loss_rate * (1 - this.smooth_factor) + this.target_loss_rate * this.smooth_factor;
            var updated_loss_rate = this.current_loss_rate / 100;
            var packets_droped_smoothed = Math.floor(packets_received * updated_loss_rate);

            var loss_rate = (packets_droped_smoothed / packets_received * 100).toFixed(2);
            if (loss_rate === 'NaN') {
                loss_rate = "0.00"
            } 
          
            this.received_packets = packets_received
            this.captured_packets = packets_received - packets_droped_smoothed
            // this.captured_packets = packets_captured
            this.dropped_packets = packets_droped_smoothed
            

            var pieHuan = this.pieHuan
            var pieHuanOption = {
                // 不同区域的颜色
                color: ['green', '#dcebff'],
                graphic: [{
                    //图形中间文字
                    type: 'text',
                    left: 'center',
                    top: '45%',
                    style: {
                        text: loss_rate.toString() + '%',
                        textAlign: 'center',
                        fill: '',//文字颜色
                        width: 15,
                        height: 10,
                        fontSize: 15,
                        fontFamily: "Microsoft Yahei"
                    }
                }],
                series: [
                    {
                        type: 'pie',
                        // 数组的第一项是内半径，第二项是外半径；可以设置不同的内外半径显示成圆环图
                        radius: ['50%', '70%'],
                        // 饼图的中心（圆心）坐标，数组的第一项是横坐标，第二项是纵坐标；设置成百分比时第一项是相对于容器宽度，第二项是相对于容器高度
                        center: ['50%', '50%'],
                        itemStyle: {
                            // 显示图例
                            normal: {
                                label: {
                                    show: true,
                                    confine: true,
                                },
                                labelLine: {
                                    show: true
                                }
                            },
                            emphasis: {
                                label: {
                                    // 标签内容是否高亮
                                    show: true,
                                    textStyle: {
                                        fontSize: '13',
                                        fontWeight: 'bold'
                                    }
                                }
                            }
                        },
                        data: [
                            { value: packets_received, name: '捕获报文数' },
                            { value: packets_droped, name: '丢包数' }
                        ]
                    }
                ],
                // 图例
                tooltip: {
                    // show: true,//是否显示图例
                    // triggerOn: 'mouseover',//鼠标移动触发
                    trigger: "item",//触发类型: 图
                    // backgroundColor: "#fff",
                    // borderColor:"rgb(216, 226, 239)",
                    // borderWidth: 1,
                    // {a}（系列名称），{b}（数据项名称），{c}（数值）, {d}（百分比）
                    formatter: "{b}: {c}<br/>({d}%)"
                },
            };
            pieHuan.setOption(pieHuanOption);
        },

        get_files_information() {
            var that = this
            $.ajax({
                type: 'get',
                url: '/nmas/traffic_collect/view_pcaps/',
                contentType: "application/json; charset=utf-8",
                success: function (response_json) {
                    // response_json = JSON.parse(response_json);
                    console.log(response_json)
                    that.filelist = response_json.pcap_files.map(function (file) {
                        var t = file.file.match(/(\d{4})(\d{2})(\d{2})\-(\d{2})(\d{2})(\d{2})/)
                        return ({
                            dir: file.dir,
                            file: file.file,
                            size: file.size,
                            time: t[1]+"-"+t[2]+"-"+t[3]+" "+t[4]+":"+t[5]+":"+t[6],
                            ip: '【Your_ip_addr_main】'
                        })
                    })
                    // this.filelist = Object.assign({}, response_json)
                    console.log(that.filelist)
                    that.initTable()
                    // console.log(this.filelist[0].file)
                },
                error: function (error) {
                    // alert('服务器发生错误！')
                }
            });

            // this.tables = true
        },

        get_files_information_all() {
            const that = this;
            const ipAddresses = ['【Your_ip_addr_main】', '【Your_ip_addr_2】', '【Your_ip_addr_1】', '【Your_ip_addr_8】', '【Your_ip_addr_9】', '【Your_ip_addr_4】', '【Your_ip_addr_5】', '【Your_ip_addr_6】', '【Your_ip_addr_7】', '【Your_ip_addr_3】'];
            const requests = ipAddresses.map(ip => {
                return $.ajax({
                    type: 'get',
                    url: `http://${ip}/nmas/traffic_collect/view_pcaps/`,
                    contentType: "application/json; charset=utf-8"
                }).then(response_json => {
                    return response_json.pcap_files.map(file => {
                        const t = file.file.match(/(\d{4})(\d{2})(\d{2})\-(\d{2})(\d{2})(\d{2})/);
                        return {
                            dir: file.dir,
                            file: file.file,
                            size: file.size,
                            time: `${t[1]}-${t[2]}-${t[3]} ${t[4]}:${t[5]}:${t[6]}`,
                            ip: ip
                        };
                    });
                }).catch(error => {
                    console.error(`Error fetching data from ${ip}`, error);
                    return [];
                });
            });

            Promise.all(requests).then(results => {
            // Flatten the array of arrays
                that.filelist = [].concat(...results);
                console.log(that.filelist);
                that.initTable();
            }).catch(error => {
                console.error('An error occurred while fetching the file information:', error);
                // alert('服务器发生错误！');
            });
        },

        get_files_information_ip(ip_address) {
            var that = this
            $.ajax({
                type: 'get',
                url: 'http://' + ip_address + '/nmas/traffic_collect/view_pcaps/',
                contentType: "application/json; charset=utf-8",
                success: function (response_json) {
                    // response_json = JSON.parse(response_json);
                    console.log(response_json)
                    that.filelist = response_json.pcap_files.map(function (file) {
                        var t = file.file.match(/(\d{4})(\d{2})(\d{2})\-(\d{2})(\d{2})(\d{2})/)
                        return ({
                            dir: file.dir,
                            file: file.file,
                            size: file.size,
                            time: t[1]+"-"+t[2]+"-"+t[3]+" "+t[4]+":"+t[5]+":"+t[6],
                            ip: ip_address
                        })
                    })
                    // this.filelist = Object.assign({}, response_json)
                    console.log(that.filelist)
                    that.initTable()
                    // console.log(this.filelist[0].file)
                },
                error: function (error) {
                    // alert('服务器发生错误！')
                }
            });

            // this.tables = true
        },

        handleSelection() {
        // 根据用户选择的选项执行相应的操作
        switch (this.selectedOption) {
            case '162':
                this.now_ip = '【Your_ip_addr_2】';
                this.present162();
                break;
            case '161':
                this.now_ip = '【Your_ip_addr_1】';
                this.present161();
                break;
            case '181':
                this.now_ip = '【Your_ip_addr_main】';
                this.present181();
                break;
            case '184':
                this.now_ip = '【Your_ip_addr_6】';
                this.present184();
                break;
            case '186':
                this.now_ip = '【Your_ip_addr_8】';
                this.present186();
                break;
            case '244':
                this.now_ip = '【Your_ip_addr_9】';
                this.present244();
                break;
            case '182':
                this.now_ip = '【Your_ip_addr_4】';
                this.present182();
                break;
            case '183':
                this.now_ip = '【Your_ip_addr_5】';
                this.present183();
                break;
            case '184':
                this.now_ip = '【Your_ip_addr_6】';
                this.present184();
                break;
            case '185':
                this.now_ip = '【Your_ip_addr_7】';
                this.present185();
                break;
            case '163':
                this.now_ip = '【Your_ip_addr_3】';
                this.present163();
                break;
            case 'ALL':
                this.now_ip = 'ALL';
                this.get_files_information_all();
                break;
            default:
                this.now_ip = 'ALL';
                // 处理默认情况
                break;
            }
        },

        present162(){
            // console.log('click')
            // this.pies162 = true
            var ip_address = '【Your_ip_addr_2】'
            this.get_files_information_ip(ip_address)
        },

        present181(){
            // console.log('click')
            // this.pies162 = true
            var ip_address = '【Your_ip_addr_main】'
            this.get_files_information_ip(ip_address)
        },

        show162(){
            console.log('click')
            this.pies162 = true
        },

        close162(){
            console.log('click')
            this.pies162 = false
        },

        present161(){
            // console.log('click')
            // this.pies162 = true
            var ip_address = '【Your_ip_addr_1】'
            this.get_files_information_ip(ip_address)
        },

        show161(){
            console.log('click')
            this.pies161 = true
        },

        close161(){
            console.log('click')
            this.pies161 = false
        },

        present184(){
            var ip_address = '【Your_ip_addr_6】'
            this.get_files_information_ip(ip_address)
        },

        show184(){
            console.log('click')
            this.pies184 = true
        },

        close184(){
            console.log('click')
            this.pies184 = false
        },

        present186(){
            var ip_address = '【Your_ip_addr_8】'
            this.get_files_information_ip(ip_address)
        },

        show186(){
            console.log('click')
            this.pies186 = true
        },

        close186(){
            console.log('click')
            this.pies186 = false
        },

        present244(){
            var ip_address = '【Your_ip_addr_9】'
            this.get_files_information_ip(ip_address)
        },

        show244(){
            console.log('click')
            this.pies244 = true
        },

        close244(){
            console.log('click')
            this.pies244 = false
        },

        
        present183(){
            var ip_address = '【Your_ip_addr_5】'
            this.get_files_information_ip(ip_address)
        },
        
        present185(){
            var ip_address = '【Your_ip_addr_7】'
            this.get_files_information_ip(ip_address)
        },
        
        present182(){
            var ip_address = '【Your_ip_addr_4】'
            this.get_files_information_ip(ip_address)
        },
        
        present163(){
            var ip_address = '【Your_ip_addr_3】'
            this.get_files_information_ip(ip_address)
        },

        

        

        run() {
        console.log('click')
        this.capturingFlag = true
        var data = {}
        if(this.caputureFilter.ip != ''){
            // let reg = new RegExp(/^(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)(?:\.(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)){3}(?:\/(?:3[0-2]|[1-2]?\d)\.(?:3[0-2]|[1-2]?\d))?(?:,(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)(?:\.(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)){3}(?:\/(?:3[0-2]|[1-2]?\d)\.(?:3[0-2]|[1-2]?\d))?)*$/)
            // if(!reg.test(this.caputureFilter.ip)){
            //     alert("请输入正确的IP地址或IP网段")
            //     this.capturingFlag = false
            //     return
            // }
            data['ip'] = this.caputureFilter.ip
            }
            if(this.caputureFilter.port != ''){
                // let reg = /^\d+$/;
                // if(!reg.test(this.caputureFilter.port)){
                //     alert("请输入正确的端口号")
                //     this.capturingFlag = false
                //     return
                // }
                data['port'] = parseInt(this.caputureFilter.port)
            }
            if(this.caputureFilter.protocol != ''){
                // let reg = /^\d+$/;
                // if(!reg.test(this.caputureFilter.protocol)){
                //     alert("请输入正确的协议号")
                //     this.capturingFlag = false
                //     return
                // }
                data['protocol'] = parseInt(this.caputureFilter.protocol)
            }
            data['timeout'] = -1
            if(this.caputureFilter.timeout != ''){
                let reg = /^\d+|-1$/;
                if(!reg.test(this.caputureFilter.timeout)){
                    alert("请输入正确抓取时间")
                    this.capturingFlag = false
                    return
                    }
                        data['timeout'] = parseInt(this.caputureFilter.timeout)
                    }
                    console.log(data)
                    //4.17
                    // const ipAddresses = ['【Your_ip_addr_2】', '【Your_ip_addr_1】', '【Your_ip_addr_6】', '【Your_ip_addr_8】', '【Your_ip_addr_9】']; 
                    const ipAddresses = ['【Your_ip_addr_main】', '【Your_ip_addr_2】', '【Your_ip_addr_1】', '【Your_ip_addr_8】', '【Your_ip_addr_9】', '【Your_ip_addr_4】', '【Your_ip_addr_5】', '【Your_ip_addr_6】', '【Your_ip_addr_7】', '【Your_ip_addr_3】'];
                    const requests = ipAddresses.map(ip => {
                        return this.$axios.post(`http://${ip}/nmas/traffic_collect/start_capture/`, data, {
                            ContentType: "application/json"
                        });
                        });
                            Promise.all(requests)
                                .then(responses => {
                                    // 当所有请求都成功时的处理
                                    responses.forEach(response => {
                                        if (response.data.status !== "Capture Success") {
                                            // alert("抓取流量失败，请重试")
                                            this.capturingFlag = false
                                        }
                                    });
                                    // 所有请求都成功
                                    console.log("所有请求成功");
                                })
                                .catch(error => {
                                    // alert("抓取流量失败，请重试")
                                    this.capturingFlag = false
                                });
                        },


        run2() {
            console.log('click')

            var data = {}
            if(this.caputureFilter.ip != ''){
                data['ip'] = this.caputureFilter.ip
            }
            if(this.caputureFilter.port != ''){
                data['port'] = parseInt(this.caputureFilter.port)
            }
            if(this.caputureFilter.protocol != ''){
                data['protocol'] = parseInt(this.caputureFilter.protocol)
            }
            data['timeout'] = -1
            if(this.caputureFilter.timeout != ''){
                let reg = /^\d+|-1$/;
                if(!reg.test(this.caputureFilter.timeout)){
                    alert("请输入正确抓取时间")
                    this.capturingFlag = false
                    return
                }
                data['timeout'] = parseInt(this.caputureFilter.timeout)
            }
            console.log(data)
            this.$axios.post('http://【Your_ip_addr_1】/nmas/traffic_collect/start_feature_extract/', data, {
                    ContentType: "application/json"
                })
            .then(response => {
                if (response.status === 200) {
                    console.log('特征提取启动成功:', response.data);
                    // window.open('http://【Your_ip_addr_1】/feature_display/', '_blank');
                    //this.showFeatureContent();
                }
            })
            .catch(error => {
                console.error('启动特征提取时出错:', error);
            });
        },

        // async run2() {
        //     this.buttonText = '正在提取特征...';

        //     await new Promise(resolve => setTimeout(resolve, 3000));
        //     try {
        //     const response = await this.$axios.post('http://【Your_ip_addr_1】/nmas/traffic_collect/start_feature_extract/');
        //     if (response.status === 200) {
        //         console.log('特征提取启动成功:', response.data);

        //         await new Promise(resolve => setTimeout(resolve, 8000));

        //         const stopResponse = await this.$axios.post('http://【Your_ip_addr_1】/nmas/traffic_collect/stop_feature_extract/');
        //         if (stopResponse.status === 200) {
        //         console.log('特征提取停止成功:', stopResponse.data);
        //         }
        //     }
        // } catch (error) {
        //     console.error('启动特征提取时出错:', error);
        // }finally {
        //         this.buttonText = '特征提取';
        //     }
            
        // },

        stop() {
            this.stoping = true
            // const ipAddresses = ['【Your_ip_addr_2】', '【Your_ip_addr_1】', '【Your_ip_addr_6】', '【Your_ip_addr_8】', '【Your_ip_addr_9】']; 
            const ipAddresses = ['【Your_ip_addr_main】', '【Your_ip_addr_2】', '【Your_ip_addr_1】', '【Your_ip_addr_8】', '【Your_ip_addr_9】', '【Your_ip_addr_4】', '【Your_ip_addr_5】', '【Your_ip_addr_6】', '【Your_ip_addr_7】', '【Your_ip_addr_3】']; 
            const requests = ipAddresses.map(ip => {
                return this.$axios.get(`http://${ip}/nmas/traffic_collect/stop_capture/`)
                .then(response => {
                    this.stoping = false;
                })
                .catch(error => {
                    this.stoping = false;
                    alert('停止失败，请重试');
                    console.log(error);
                });
            });

            Promise.all(requests)
                .then(() => {
                    console.log('所有请求成功');
            });
            // this.$axios.get('http://${ip}/nmas/traffic_collect/stop_capture/').then(response => {
            //     this.stoping = false
            // }).catch(error => {
            //     this.stoping = false
            //     alert('停止失败，请重试')
            //     console.log(error)
            // })
        }
    }
}
</script>