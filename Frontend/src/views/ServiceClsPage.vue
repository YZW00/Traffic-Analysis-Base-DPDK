<template>
    <div class="page-wrapper">
        <div class="page-content">
            <div class="card">
                <div class="card-body">
                    <div class="page-breadcrumb d-none d-sm-flex align-items-center mb-3">
                        <div class="logo-container ps-3">
                            <img src="../assets/images/icon.png" alt="Logo" class="logo-img" style="width: 30px; height: auto;" />
                        </div>
                        <div class="text-uppercase pe-3 ps-2" style="font-size: 1.2rem;">业务分类</div>
                    </div>
                    <hr style="margin-left: 16px;"/>
                    <ul class="nav nav-pills mb-3" role="tablist" style="margin-left: 20px;">
                        <li class="nav-item" role="presentation">
                            <a class="nav-link active" data-bs-toggle="pill" href="#serviceMapping" role="tab"
                                aria-selected="true">
                                <div class="d-flex align-items-center">
                                    <div class="tab-icon"><i class="fadeIn animated bx bx-map-pin"></i>
                                    </div>
                                    <div class="tab-title ">业务类别映射</div>
                                </div>
                            </a>
                        </li>
                        <li class="nav-item" role="presentation">
                            <a class="nav-link" data-bs-toggle="pill" href="#modelTrain" role="tab"
                                aria-selected="false">
                                <div class="d-flex align-items-center">
                                    <div class="tab-icon"><i class="fadeIn animated bx bx-meteor"></i>
                                    </div>
                                    <div class="tab-title">业务分类模型训练</div>
                                </div>
                            </a>
                        </li>
                        <li class="nav-item" role="presentation">
                            <a class="nav-link" data-bs-toggle="pill" href="#modelCls" role="tab" aria-selected="false">
                                <div class="d-flex align-items-center">
                                    <div class="tab-icon"><i class="fadeIn animated bx bx-network-chart"></i>
                                    </div>
                                    <div class="tab-title">业务分类</div>
                                </div>
                            </a>
                        </li>
                    </ul>
                    <div class="tab-content py-3" style="margin-left: 20px;">
                        <div class="tab-pane fade active show" id="serviceMapping" role="tabpanel">
                            <div
                              class="alert border-0 border-start border-5 alert-dismissible fade show py-2"
                              style="border-radius: 7px;"
                              v-for="(services, serviceType, index) in serviceRelated.serviceTypeMaps"
                              :key="serviceType"
                              @mouseenter="hoverServiceType(serviceType)"
                              @mouseleave="hoverServiceType(null)"
                              :class="{
                                'hover-bg': hoveredServiceType === serviceType,
                                [`border-${colors[index % colors.length]}`]: true
                              }"
                            >
                              <div class="d-flex align-items-center justify-content-between">
                                <div class="ms-2">
                                  <h4
                                    style="color: #0066cc; font-size: 1.5rem; font-weight: bold; margin: 0; padding-top: 15px;"
                                  >
                                    {{ serviceType.toUpperCase() }}
                                  </h4>
                                </div>
                                <!-- 删除按钮 -->
                                <svg
                                  v-if="hoveredServiceType === serviceType"
                                  @click="removeServiceType(serviceType)"
                                  xmlns="http://www.w3.org/2000/svg"
                                  viewBox="0 0 24 24"
                                  fill="#007bff"
                                  style="position: absolute; top: 50%; right: 10px; transform: translateY(-50%); cursor: pointer; width: 28px; height: 28px;"
                                >
                                  <path d="M12 10.586L5.757 4.343c-.39-.39-1.024-.39-1.414 0s-.39 1.024 0 1.414L10.586 12l-6.243 6.243c-.39.39-.39 1.024 0 1.414s1.024.39 1.414 0L12 13.414l6.243 6.243c.39.39 1.024.39 1.414 0s.39-1.024 0-1.414L13.414 12l6.243-6.243c.39-.39.39-1.024 0-1.414s-1.024-.39-1.414 0L12 10.586z" />
                                </svg>
                              </div>
                              <hr style="visibility: hidden;" />
                              <div class="chip" v-for="service in services" :key="service">
                                {{ service }}
                                <span class="closebtn" @click="removeServiceName(serviceType, service)">×</span>
                              </div>
                              <div class="chip">
                                <button
                                  type="button"
                                  class="btn btn-link btn-sm"
                                  style="text-decoration: none;"
                                  @click="showDialog2(serviceType)"
                                >
                                  <i class="bx bx-plus mr-1"></i>添加业务名称
                                </button>
                              </div>
                            </div>
                            <el-button type="info" round style="float:right; border-radius: 20px; background: linear-gradient(135deg, #C0C0C0, #C0B1AA); color: #fff;" class="btn btn-detect px-5 radius-30"
                                @click="serviceTypeMapCancleBtnOnclick">取消修改</el-button>
                            <el-button type="primary" round class="btn btn-detect shadow-lg px-5 radius-30" style="float:right;margin-right: 2%;"
                                @click="submitServiceTypeMapChange">提交修改</el-button>
                            <el-button type="primary" round class="btn btn-detect shadow-lg px-5 radius-30" style="float:right;margin-right: 2%;"
                                @click="showDialog1">添加业务类型</el-button>


                        </div>

                        <div class="tab-pane fade" id="modelTrain" role="tabpanel">
                            <div class="card upload-section">                             
                                <div class="card-body">
                                    <div class="mb-3">
                                        <label for="formFile" class="form-label">上传pcap/pcapng文件进行模型训练</label>
                                        <div class="input-group">
                                            <div class="col-md-4 select-padding"> <!-- 添加自定义类来设置右边内边距 -->
                                                <select v-model="trainRelated.uploadPcapType" class="form-select">
                                                    <option selected="" value="">选择要上传的 pcap/pcapng 文件所属业务类别</option>
                                                    <option v-for="(services, serviceType) in serviceRelated.serviceTypeMaps"
                                                            :key="serviceType" :value="serviceType">{{ serviceType }}</option>
                                                </select>
                                            </div>
                                            <div class="col-md-4 select-padding"> <!-- 添加自定义类来设置左边内边距 -->
                                                <input type="file" class="form-control" id="inputGroupFile04" ref="trainUploadInput"
                                                    aria-describedby="inputGroupFileAddon04" aria-label="Upload"
                                                    @change="selectedFile" style="color: #c0c4cc;">
                                            </div>
                                            <div class="col-md-4">
                                                <button v-if="!uploadingFlag" :class="btnClassUpload"
                                                        @click="uploadPcap" style="width: 170px; height: 40px;">上传</button>
                                                <button v-else class="btn btn-primary px-5,radius-30" type="button" disabled="">
                                                    <span class="spinner-border spinner-border-sm" role="status"
                                                        aria-hidden="true"></span>上传中...</button>
                                            </div>
                                        </div>
                                    </div>
                                </div>                               
                            </div>

                            <hr />
                            <div class="card">
                                <div class="card-body">
                                    <div class="mb-3"> <!-- 将原本的row g-3修改为mb-3，结构上与模板一致 -->
                                        <label for="formFile" class="form-label">选择服务器上的流量文件进行特征提取生成数据集(按照数据包所属类别进行提取)</label>
                                        <div class="input-group">
                                            <div class="col-md-4 select-padding" style="display: flex; align-items: center;">
                                                <span class="input-group-text" id="basic-addon3">选择数据类别：</span>
                                                <select id="featureTypeSelect" class="multiple-select" multiple="multiple">
                                                    <option v-for="(services, serviceType) in serviceRelated.serviceTypeMaps"
                                                            :key="serviceType" :value="serviceType">{{ serviceType }}</option>
                                                </select>
                                            </div>
                                            <div class="col-md-4 select-padding"> <!-- 添加自定义类来设置左边内边距，与模板结构对应 -->
                                                <div class="input-group">
                                                    <span class="input-group-text" id="basic-addon3">输入特征存储的文件名：</span>
                                                    <input v-model="trainRelated.featureGetSaveName" class="form-control" />
                                                </div>
                                            </div>
                                            <div class="col-md-4">
                                                <button v-if="!featureGetingFlag" :class="btnClassStartFeaturing"
                                                        @click="startFeatureGet" style="width: 170px; height: 40px;">开始提取</button>
                                                <button v-else class="btn btn-primary px-5,radius-30" type="button" disabled="">
                                                    <span class="spinner-border spinner-border-sm" role="status"
                                                        aria-hidden="true"></span>特征提取中...</button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <hr />
                            <div class="card">
                                <div class="card-body">
                                    <div class="mb-3">
                                        <label for="formFile" class="form-label">选择数据和模型进行训练(数据包括历史上传的所有数据)</label>
                                        <div class="input-group">
                                            <div class="col-md-4 select-padding" style="display: flex; align-items: center;">
                                                <span class="input-group-text" id="basic-addon3">选择数据：</span>
                                                <select v-model="trainRelated.chooseTrainModelDataFileName" class="form-select">
                                                    <option
                                                            v-for="trainModelDataFileName in trainRelated.trainModelDataFileNames"
                                                            :value="trainModelDataFileName">{{ trainModelDataFileName }}</option>
                                                </select>
                                            </div>
                                            <div class="col-md-4 select-padding" style="display: flex; align-items: center;">
                                                <span class="input-group-text" id="basic-addon3">选择模型：</span>
                                                <select v-model="trainRelated.choosetrainModelType" class="form-select">
                                                    <option selected="" value="lstm">lstm</option>
                                                    <option selected="" value="classic">classic</option>
                                                </select>
                                            </div>
                                            <div class="col-md-4">
                                                <button v-if="!trainningFlag" :class="btnClassStartTrain"
                                                        @click="startTrain" style="width: 170px; height: 40px;">开始训练</button>
                                                <button v-else class="btn btn-primary px-5,radius-30" type="button" disabled="">
                                                    <span class="spinner-border spinner-border-sm" role="status"
                                                        aria-hidden="true"></span>训练中...</button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <hr />

                            <div class="row row-cols-1 row-cols-md-2 row-cols-xl-4" v-if="this.showTrainResultFlag">
                                <div class="col">
                                    <div class="card radius-10 border-start border-0 border-3 border-info">
                                        <div class="card-body">
                                            <div class="d-flex align-items-center">
                                                <div>
                                                    <p class="mb-0 text-secondary">平均f1 score</p>
                                                    <h4 class="my-1 text-info">{{ this.clsRelated.f1Score }}</h4>
                                                </div>
                                                <!-- <div
                                                    class="widgets-icons-2 rounded-circle bg-gradient-scooter text-white ms-auto">
                                                    <i class="bx bxs-cart"></i>
                                                </div> -->
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div class="col">
                                    <div class="card radius-10 border-start border-0 border-3 border-danger">
                                        <div class="card-body">
                                            <div class="d-flex align-items-center">
                                                <div>
                                                    <p class="mb-0 text-secondary">平均准确率</p>
                                                    <h4 class="my-1 text-danger">{{ this.clsRelated.accuracy }}</h4>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div class="col">
                                    <div class="card radius-10 border-start border-0 border-3 border-success">
                                        <div class="card-body">
                                            <div class="d-flex align-items-center">
                                                <div>
                                                    <p class="mb-0 text-secondary">平均精确率</p>
                                                    <h4 class="my-1 text-success">{{ this.clsRelated.precision }}</h4>
                                                </div>

                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div class="col">
                                    <div class="card radius-10 border-start border-0 border-3 border-warning">
                                        <div class="card-body">
                                            <div class="d-flex align-items-center">
                                                <div>
                                                    <p class="mb-0 text-secondary">平均召回率</p>
                                                    <h4 class="my-1 text-warning">{{ this.clsRelated.recall }}</h4>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div class="row row-cols-1 row-cols-lg-3" v-if="this.showTrainLSTMResultFlag">
                                <div class="col d-flex">
                                    <div class="card radius-10 w-100">
                                        <div class="card-header bg-transparent">
                                            <div class="d-flex align-items-center">
                                                <div>
                                                    <h6 class="mb-0">train loss</h6>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="card-body">
                                            <div class="chart-container-0" id="chartLoss"
                                                style="width: 1000px; max-width: 100%; height:350px; overflow: hidden;max-height: 100%;">
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <div class="col d-flex">
                                    <div class="card radius-10 w-100">
                                        <div class="card-header bg-transparent">
                                            <div class="d-flex align-items-center">
                                                <div>
                                                    <h6 class="mb-0">train acc</h6>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="card-body">
                                            <div class="chart-container-0" id="chartTrainAcc"
                                                style="width: 1000px; max-width: 100%; height:350px; overflow: hidden;max-height: 100%;">
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <div class="col d-flex">
                                    <div class="card radius-10 w-100">
                                        <div class="card-header bg-transparent">
                                            <div class="d-flex align-items-center">
                                                <div>
                                                    <h6 class="mb-0">test acc</h6>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="card-body">
                                            <div class="chart-container-0" id="chartTestAcc"
                                                style="width: 1000px; max-width: 100%; height:350px; overflow: hidden;max-height: 100%;">
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- <div>
                                <canvas id="trainLossLine" width="430" height="325"
                                    style="display: block; height: 260px; width: 344px;"
                                    class="chartjs-render-monitor"></canvas>
                            </div> -->
                        </div>

                        <div class="tab-pane fade" id="modelCls" role="tabpanel">
                            <div class="card">
                                <div class="card-head">
                                    <h5><label for="formFile" class="form-label"
                                            style="padding:10px 20px 10px">流量数据分类</label></h5>
                                </div>
                                <div class="card-body">
                                    <div class="row g-3" style="padding-left:15px">
                                        <div class="col-md-4">
                                            <div class="input-group">
                                                <span class="input-group-text" id="basic-addon3">输入要分类的IP地址：</span>
                                                <!-- <span class="input-group-text" id="basic-addon3">1000</span> -->
                                                <input class="form-control" type="text" placeholder="非必填项，默认所有抓取到的IP地址"
                                                    v-model="clsRelated.ipFilter">
                                            </div>
                                        </div>

                                        <div class="col-md-4">
                                            <div class="input-group">
                                                <span class="input-group-text" id="basic-addon3">输入置信度域值：</span>
                                                <input placeholder="非必填项，默认0.4" type="text"
                                                    oninput="value=value.replace(/[^?\d.]/g,'')" class="form-control"
                                                    v-model="clsRelated.confidence">
                                                <!-- <input class="form-control mb-3" type="text" placeholder="1000" aria-label="Disabled input example" disabled="" readonly=""> -->
                                            </div>
                                        </div>

                                        <div class="col-md-4">
                                            <div class="input-group">
                                                <span class="input-group-text" id="basic-addon3">选择模型：</span>
                                                <select v-model="clsRelated.chooseClsModelType" class="form-select">
                                                    <option selected="" value="lstm">lstm</option>
                                                    <option selected="" value="classic">classic</option>
                                                    <option selected="" value="united">united</option>
                                                </select>
                                            </div>
                                        </div>
                                    </div>
                                    <br />
                                    <div class="row g-3" style="padding-left:15px">
                                        <div class="col-md-4">
                                            <div class="input-group">
                                                <span class="input-group-text" id="basic-addon3">输入要分类的起始时间：</span>
                                                <input type="datetime-local" class="form-control"
                                                    placeholder="非必填，默认流量抓取最早时间" v-model="clsRelated.startTime">
                                            </div>
                                        </div>

                                        <div class="col-md-4">
                                            <div class="input-group">
                                                <span class="input-group-text" id="basic-addon3">输入要分类的结束时间：</span>
                                                <input type="datetime-local" class="form-control"
                                                    placeholder="非必填，默认流量抓取最晚时间" v-model="clsRelated.endTime">
                                            </div>
                                        </div>

                                        <div class="col-md-2">
                                            <button v-if="!clsingFlag" :class="btnClassStartCls"
                                                @click="startCls">开始分类</button>
                                            <button v-else class="btn btn-primary px-5,radius-30" type="button"
                                                disabled="">
                                                <span class="spinner-border spinner-border-sm" role="status"
                                                    aria-hidden="true"></span>分类中...</button>
                                        </div>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col">
                                        <div class="card" style="border: 0px; box-shadow: 0 0;" v-if="showClsResultFlag">
                                            <div class="card-body m-auto">
                                                <div class="chart-container1" id="clsPie"
                                                    style="width: 400px; min-width: 100%; height:400px;">
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    <!--
                                    <div class="col">
                                        <div class="card" v-if="showClsResultFlag">
                                            <div class="card-body m-auto">
                                                <div class="chart-container1" id="clsPie" v-if="showClsResultFlag"
                                                    style="width: 400px; min-width: 100%; height:400px;">
                                                </div>
                                            </div>
                                        </div>
                                    </div> -->
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>


            <!-- <div class="card">
                <div class="card-body">
                    <h4 class="card-title">业务类别映射</h4>
                    <hr/>
                    <div class="alert border-0 border-start border-5 border-primary alert-dismissible fade show py-2" v-for="(services,serviceType) in serviceRelated.serviceTypeMaps" :key="serviceType">
                        <div class="d-flex align-items-center">
                            <div class="ms-3">
                                <div>
                                    <h4 class="mb-0 text-primary">{{serviceType}}
                                    <button type="button" class="btn btn-primary px-7" @click="showDialog2(serviceType)"><i class="bx bx-plus mr-1"></i>添加业务名称</button></h4>
                                </div>

                                <hr/>
                                <div class="chip" v-for="service in services">
                                    {{service}}<span class="closebtn" @click="removeServiceName(serviceType,service)">×</span>
                                </div>
                            </div>
                        </div>
                        <button type="button" class="btn-close" @click="removeServiceType(serviceType)"></button>
                    </div>
                    <button type="button" class="btn btn-primary px-5 radius-30" @click="showDialog1">添加业务类型</button>
                    <button type="button" class="btn btn-primary px-5 radius-30" @click="submitServiceTypeMapChange">提交修改</button>
                    <button type="button" :class="btnClass" @click="serviceTypeMapCancleBtnOnclick">取消修改</button>
                </div>
            </div> -->

            <!-- 模型训练部分 -->
            <!-- <div class="card">
                <div class="card-body">
                    <h4 class="card-title">业务分类模型训练</h4>
                    <hr/>
                    <div class="mb-3">
                        <label for="formFile" class="form-label">上传pcap文件进行模型训练</label>
                        <input class="form-control" type="file" id="formFile">
                    </div>
                    <div>

                    </div>
                </div>
            </div> -->
        </div>
        <!-- 添加业务类型的dialog，dialog1 -->
        <div class="modal" id="dialog1" tabindex="-1"
            :style="{ 'display': (showDialogFlag1 == true ? 'block' : 'none') }">
            <div class="modal-dialog modal-sm">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title"></h5>
                        <button type="button" class="btn-close" @click="closeDialog1"></button>
                    </div>
                    <div class="modal-body">
                        输入要添加的业务类型
                        <input class="form-control mb-3" type="text" placeholder="输入添加的业务类型"
                            v-model="inputNewServiceType">
                        <!-- <div class="input-group mb-3"> <span class="input-group-text" id="inputGroup-sizing-default">输入要添加的业务类型</span>
                            <input type="text" class="form-control" aria-label="Sizing example input" aria-describedby="inputGroup-sizing-default">
                        </div> -->
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" @click="closeDialog1">否</button>
                        <button type="button" class="btn btn-primary" @click="addServiceType">是</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- 添加业务类型的dialog，dialog2 -->
        <div class="modal" id="dialog2" tabindex="-1"
            :style="{ 'display': (showDialogFlag2 == true ? 'block' : 'none') }">
            <div class="modal-dialog modal-sm">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title"></h5>
                        <button type="button" class="btn-close" @click="closeDialog2"></button>
                    </div>
                    <div class="modal-body">
                        输入要给{{ chooseServivceType }}业务添加的业务名称
                        <input class="form-control mb-3" type="text" placeholder="输入添加的业务名称"
                            v-model="inputNewServiceName">
                        <!-- <div class="input-group mb-3"> <span class="input-group-text" id="inputGroup-sizing-default">输入要添加的业务类型</span>
                            <input type="text" class="form-control" aria-label="Sizing example input" aria-describedby="inputGroup-sizing-default">
                        </div> -->
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" @click="closeDialog2">否</button>
                        <button type="button" class="btn btn-primary" @click="addServiceName()">是</button>
                    </div>
                </div>
            </div>
        </div>
        <BgCover :show-cover="showDialogFlag1 || showDialogFlag2"></BgCover>
    </div>
</template>

<script>
import BgCover from '../components/BgCover.vue'
require("echarts/theme/roma")

export default {
    data() {
        return {
            hoveredServiceType: null, // 当前悬停的业务类别
            serviceRelated: {
                serviceTypeMaps: {},
                serviceTypeMapsBack: {},
                serviceTypeChangeFlag: false
            },
            showDialogFlag1: false,
            showDialogFlag2: false,
            uploadingFlag: false,
            trainningFlag: false,
            featureGetingFlag: false,
            clsingFlag: false,
            showTrainResultFlag: false,
            showTrainLSTMResultFlag: false,
            showClsResultFlag: false,
            inputNewServiceType: '',
            chooseServivceType: '',
            inputNewServiceName: '',
            lossChart: null,
            trainAccChart: null,
            testAccChart: null,
            historyData: {
                legendData: ['chat', 'p2p', 'video', 'text', 'game'],
                data: [
                    { value: 20, name: 'chat' },
                    { value: 20, name: 'p2p' },
                    { value: 20, name: 'video' },
                    { value: 20, name: 'text' },
                    { value: 20, name: 'game' }
                ]
            },
            chooseFeatureGetType: [],
            trainRelated: {
                uploadFileData: null,
                uploadPcapType: '',

                featureGetSaveName: '',
                choosetrainModelType: '',
                chooseTrainModelDataFileName: '',
                trainModelDataFileNames: [],
            },
            clsRelated: {
                confidence: '',
                chooseClsModelType: '',
                startTime:'',
                endTime:'',
                ipFilter:'',
                f1Score: '',
                accuracy: '',
                precision: '',
                recall: ''
            },
            colors: ['primary', 'success', 'danger', 'warning', 'info', 'secondary'], // 自定义循环颜色
            // historyPieChart: null,
            clsPieChart: null
        }
    },

    computed: {
        btnClassCancle: function () {
            return [
                'btn', 'btn-secondary', 'px-5', 'radius-30',
                {
                    'disabled': !this.serviceRelated.serviceTypeChangeFlag
                }
            ]
        },

        btnClassUpload: function () {
            return [
                'btn', 'btn-primary', 'px-5', 'radius-30',
                {
                    'disabled': this.trainRelated.uploadPcapType == ''
                }
            ]
        },

        btnClassStartFeaturing: function () {
            return [
                'btn', 'btn-primary', 'px-5', 'radius-30',
                {
                    'disabled': this.chooseFeatureGetType == [] || this.trainRelated.featureGetSaveName == ''
                }
            ]
        },

        btnClassStartTrain: function () {
            return [
                'btn', 'btn-primary',
                {
                    'disabled': this.trainRelated.choosetrainModelType == '' || this.trainRelated.chooseTrainModelDataFileName == ''
                }
            ]
        },

        btnClassStartCls: function () {
            return [
                'btn', 'btn-primary',
                {
                    'disabled': this.clsRelated.chooseClsModelType == ''
                }
            ]
        }
    },

    mounted() {
        this.getData()

        $('#featureTypeSelect').select2({
            theme: 'bootstrap4',
            width: $(this).data('width') ? $(this).data('width') : $(this).hasClass('w-100') ? '100%' : 'style',
            placeholder: $(this).data('placeholder'),
            allowClear: true,
        }).on("change", (e) => {
            console.log(e)
            console.log($(e.target).val())
            this.chooseFeatureGetType = $(e.target).val()
        })

        // var option = {
        //     maintainAspectRatio: false,
        //     title: {
        //         text: '历史业务分类结果',
        //     },
        //     //鼠标划过时饼状图上显示的数据
        //     tooltip: {
        //         trigger: 'item',
        //         triggerOn: "mousemove",
        //         axisPointer: {
        //             // 坐标轴指示器，坐标轴触发有效
        //             type: 'shadow', // 默认为直线，可选为：'line' | 'shadow'
        //         },
        //         showContent: true,                       //是否显示提示框浮层
        //         formatter: '{a}<br/>{b}:{c} ({d}%)'
        //     },
        //     //图例
        //     legend: {
        //         bottom: 10,//控制图例出现的距离  默认左上角
        //         left: 'center',//控制图例的位置
        //         // itemWidth: 16,//图例颜色块的宽度和高度
        //         // itemHeight: 12,
        //         textStyle: {//图例中文字的样式
        //             color: '#000',
        //             fontSize: 16
        //         },
        //         data: this.historyData.legendData//图例上显示的饼图各模块上的名字
        //     },
        //     series: [{
        //         type: 'pie',             //echarts图的类型   pie代表饼图
        //         radius: ['50%', '70%'],           //饼图中饼状部分的大小所占整个父元素的百分比
        //         center: ['50%', '50%'],
        //         data: this.historyData.data,
        //         itemStyle: {
        //             normal: {
        //                 label: {
        //                     show: true, //饼图上是否出现标注文字 标注各模块代表什么  默认是true
        //                 },
        //                 labelLine: {
        //                     show: true, //官网demo里外部标注上的小细线的显示隐藏    默认显示
        //                 }
        //             }
        //         }
        //     }]
        // }
        // // this.$nextTick(()=>{
        // //     this.historyPieChart = this.$echarts.init(document.getElementById('historyPie'))
        // //     this.historyPieChart.setOption(option)
        // //         })
        // this.historyPieChart = this.$echarts.init(document.getElementById('historyPie'), "roma")
        // this.historyPieChart.setOption(option)
        // window.addEventListener("resize", () => {
        //     // 第六步，执行echarts自带的resize方法，即可做到让echarts图表自适应
        //     this.historyPieChart.resize();
        //     // 如果有多个echarts，就在这里执行多个echarts实例的resize方法,不过一般要做组件化开发，即一个.vue文件只会放置一个echarts实例
        //     /*
        //     this.myChart2.resize();
        //     this.myChart3.resize();
        //     ......
        //     */
        // });
    },

    methods: {
        hoverServiceType(serviceType) {
          this.hoveredServiceType = serviceType; // 设置悬停状态
        },
        removeServiceType(serviceType) {
          this.$delete(this.serviceRelated.serviceTypeMaps, serviceType); // 删除业务类别
          this.serviceRelated.serviceTypeChangeFlag = true; // 标记修改状态
        },
        getData() {
            var serverError = false
            this.$axios.get("/nmas/classify/splitConfig").then(response => {
                if (response.data.status == 'success') {
                    this.serviceRelated.serviceTypeMaps = response.data.result
                    this.serviceRelated.serviceTypeMapsBack = JSON.parse(JSON.stringify(this.serviceRelated.serviceTypeMaps))
                    this.$axios.post("/nmas/classify/showDir", { "childDir": "Features" }).then(response => {
                        if (response.data.status == 'success') {
                            this.trainRelated.trainModelDataFileNames = response.data.result
                        }
                    }, response => {
                        alert('服务器发生错误')
                        console.log(response)
                    })
                    // this.serviceRelated.serviceTypeMapsBack= Object.assign({},this.serviceRelated.serviceTypeMaps);
                }
            }, response => {
                alert('服务器发生错误')
                console.log(response)
                serverError = true
            })


        },

        submitServiceTypeMapChange() {
            console.log(this.serviceRelated.serviceTypeMaps)
            this.$axios.post('/nmas/classify/splitConfig', { 'data': this.serviceRelated.serviceTypeMaps }).then(response => {
                console.log(response)
                if (response.data.status == 'success') {
                    alert('业务类型映射修改成功')
                    this.serviceRelated.serviceTypeMapsBack = JSON.parse(JSON.stringify(this.serviceRelated.serviceTypeMaps))
                    this.serviceRelated.serviceTypeChangeFlag = false
                } else {
                    alert('业务映射修改失败,请重试')
                }
            }, response => {
                alert('业务映射修改失败,请重试')
                console.log(response)
            })
        },

        serviceTypeMapCancleBtnOnclick() {
            this.serviceRelated.serviceTypeMaps = JSON.parse(JSON.stringify(this.serviceRelated.serviceTypeMapsBack))
            // this.serviceRelated.serviceTypeMaps = Object.assign({},this.serviceRelated.serviceTypeMapsBack);
            this.serviceRelated.serviceTypeChangeFlag = false
        },

        showDialog1() {
            this.showDialogFlag1 = true
        },

        closeDialog1() {
            this.inputNewServiceType = ''
            this.showDialogFlag1 = false
        },

        addServiceType() {
            if (this.inputNewServiceType.split(' ').join('').length == 0)
                alert("请输入业务类别")
            else {
                console.log(this.serviceRelated.serviceTypeMaps[this.inputNewServiceType])
                if (this.serviceRelated.serviceTypeMaps[this.inputNewServiceType] != undefined) {
                    alert("输入的业务类别已存在")
                } else {
                    this.showDialogFlag1 = false
                    this.serviceRelated.serviceTypeMaps[this.inputNewServiceType] = []
                    this.serviceRelated.serviceTypeChangeFlag = true
                }
            }
            this.inputNewServiceType = ''
        },

        showDialog2(serviceType) {
            this.chooseServivceType = serviceType
            this.showDialogFlag2 = true
        },

        closeDialog2() {
            this.inputNewServiceName = ''
            this.showDialogFlag2 = false
        },

        addServiceName() {
            if (this.inputNewServiceName.split(' ').join('').length == 0)
                alert("请输入业务名称")
            else {
                if (this.serviceRelated.serviceTypeMaps[this.chooseServivceType].indexOf(this.inputNewServiceName) != -1) {
                    alert("输入的业务名称已存在")
                } else {
                    this.showDialogFlag2 = false
                    this.serviceRelated.serviceTypeMaps[this.chooseServivceType].push(this.inputNewServiceName)
                    this.serviceRelated.serviceTypeChangeFlag = true
                    this.chooseServivceType = ''

                }
            }
            this.inputNewServiceName = ''
        },

        removeServiceName(serviceType, service) {
            var index = this.serviceRelated.serviceTypeMaps[serviceType].findIndex(function (item) {
                return item == service;
            })
            this.serviceRelated.serviceTypeMaps[serviceType].splice(index, 1);
            this.serviceRelated.serviceTypeChangeFlag = true
        },

        removeServiceType(serviceType) {
            this.$delete(this.serviceRelated.serviceTypeMaps, serviceType)
            this.serviceRelated.serviceTypeChangeFlag = true
        },

        selectedFile() {
            let file = this.$refs.trainUploadInput.files[0]
            let index = file.name.lastIndexOf(".");
            let suffix = file.name.substring(index + 1).toLowerCase();
            if (suffix == 'pcap' || suffix == 'pcapng') {
                return
            } else {

            }
        },

        uploadPcap() {
            let file = this.$refs.trainUploadInput.files[0]
            if (file == undefined) {
                alert('请选择要上传的文件！')
            } else {
                let index = file.name.lastIndexOf(".");
                let suffix = file.name.substring(index + 1).toLowerCase();

                if (suffix == 'pcap' || suffix == 'pcapng') {
                    this.uploadingFlag = true
                    let uploadData = new FormData()
                    uploadData.append('label', this.trainRelated.uploadPcapType)
                    uploadData.append('files', file)
                    console.log(uploadData.get('label'))
                    console.log(uploadData.get('file'))
                    this.$axios.post('/nmas/classify/uploadFiles', uploadData, {
                        headers: { "Content-Type": "multipart/form-data" }
                    }).then(res => {
                        if (res.data.status == 'success') {
                            alert('上传成功')
                        } else {
                            alert('上传失败，请重试！')
                        }
                        console.log(res)
                    }, res => {
                        alert('上传失败，请重试！')
                    })
                } else {
                    alert('文件格式错误，不支持的文件扩展名，请重新上传！')
                }
            }
            this.uploadingFlag = false

        },

        startFeatureGet() {
            this.featureGetingFlag = true
            console.log(this.chooseFeatureGetType)
            this.$axios.post('/nmas/classify/datasetBuild', {
                'classes': this.chooseFeatureGetType,
                'dataset_name': this.trainRelated.featureGetSaveName
            }).then(res => {
                if (res.data.status == 'success') {
                    this.$axios.post("/nmas/classify/showDir", { "childDir": "Features" }).then(response => {
                        if (response.data.status == 'success') {

                            this.trainRelated.trainModelDataFileNames = response.data.result
                            alert('特征提取完成')
                        }
                    }, response => {
                        console.log(response)
                        alert('特征提取失败，请重试！')
                    })
                } else {
                    console.log(res)
                    alert('特征提取失败，请重试！')
                }

            }, res => {
                console.log(res)
                alert('特征提取失败，请重试！')
            })
            this.featureGetingFlag = false
        },

        startTrain() {
            this.trainningFlag = true

            // setTimeout(() => {
            //     this.trainningFlag = false
            //     var xLableList = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '60', '61', '62', '63', '64', '65', '66', '67', '68', '69', '70', '71', '72', '73', '74', '75', '76', '77', '78', '79', '80', '81', '82', '83', '84', '85', '86', '87', '88', '89', '90', '91', '92', '93', '94', '95', '96', '97', '98', '99', '100', '101', '102', '103', '104', '105', '106', '107', '108', '109', '110', '111', '112', '113', '114', '115', '116', '117', '118', '119', '120', '121', '122', '123', '124', '125', '126', '127', '128', '129', '130', '131', '132', '133', '134', '135', '136', '137', '138', '139', '140', '141', '142', '143', '144', '145', '146', '147', '148', '149', '150', '151', '152', '153', '154', '155', '156', '157', '158', '159', '160', '161', '162', '163', '164', '165', '166', '167', '168', '169', '170', '171', '172', '173', '174', '175', '176', '177', '178', '179', '180', '181', '182', '183', '184', '185', '186', '187', '188', '189', '190', '191', '192', '193', '194', '195', '196', '197', '198', '199', '200']
            //         var lossList = [1.4512, 1.2206, 1.1962, 1.1761, 1.1622, 1.1533, 1.1446, 1.136, 1.1297, 1.1233, 1.1201, 1.1168, 1.1141, 1.1113, 1.1093, 1.1088, 1.1074, 1.1061, 1.1065, 1.1042, 1.1028, 1.1014, 1.1001, 1.0992, 1.0985, 1.0982, 1.098, 1.0984, 1.097, 1.0974, 1.0969, 1.0965, 1.096, 1.0961, 1.095, 1.0957, 1.0958, 1.0966, 1.0953, 1.095, 1.0951, 1.0945, 1.0948, 1.0951, 1.0958, 1.0946, 1.0945, 1.0939, 1.0944, 1.0931, 1.093, 1.0913, 1.0872, 1.0868, 1.087, 1.0871, 1.0869, 1.0871, 1.0876, 1.0872, 1.0869, 1.0866, 1.0856, 1.0853, 1.0851, 1.0853, 1.0849, 1.0849, 1.085, 1.0857, 1.0844, 1.0842, 1.084, 1.0838, 1.0835, 1.0836, 1.0832, 1.0837, 1.0831, 1.0824, 1.0825, 1.0823, 1.0823, 1.082, 1.0822, 1.082, 1.0822, 1.082, 1.0818, 1.082, 1.0821, 1.0823, 1.0816, 1.0821, 1.0815, 1.0813, 1.0817, 1.0816, 1.0817, 1.0816, 1.0813, 1.0816, 1.0815, 1.0814, 1.0817, 1.0815, 1.0812, 1.0817, 1.0814, 1.0815, 1.0813, 1.0815, 1.0814, 1.0808, 1.0812, 1.0811, 1.0813, 1.0809, 1.081, 1.081, 1.081, 1.0814, 1.0807, 1.081, 1.0809, 1.0811, 1.0811, 1.0814, 1.0809, 1.081, 1.0813, 1.0809, 1.081, 1.0809, 1.0814, 1.0807, 1.0813, 1.0809, 1.0809, 1.081, 1.081, 1.0807, 1.0812, 1.0809, 1.0811, 1.0809, 1.081, 1.0811, 1.0809, 1.081, 1.0809, 1.0808, 1.0809, 1.0811, 1.081, 1.0806, 1.081, 1.0809, 1.0814, 1.0808, 1.0809, 1.0811, 1.0811, 1.0812, 1.0809, 1.0809, 1.0808, 1.0809, 1.0812, 1.0807, 1.0807, 1.0807, 1.0808, 1.0809, 1.0808, 1.0806, 1.0808, 1.0808, 1.081, 1.0809, 1.0807, 1.0807, 1.0809, 1.0808, 1.0808, 1.0809, 1.081, 1.0806, 1.0806, 1.0807, 1.0811, 1.0808, 1.0808, 1.0808, 1.0808, 1.0807, 1.0807, 1.0808, 1.0806, 1.0811]
            //         var trainAccList = [0.5897, 0.8072, 0.8289, 0.8491, 0.8627, 0.8714, 0.8808, 0.8896, 0.8952, 0.901, 0.9046, 0.9069, 0.9101, 0.9126, 0.9142, 0.9157, 0.9169, 0.9173, 0.9174, 0.9194, 0.921, 0.9226, 0.9224, 0.924, 0.9245, 0.9249, 0.9249, 0.9246, 0.9256, 0.9254, 0.926, 0.9267, 0.9269, 0.9271, 0.9274, 0.9272, 0.9269, 0.9265, 0.9274, 0.9277, 0.9279, 0.9278, 0.9282, 0.9278, 0.9272, 0.9284, 0.928, 0.9287, 0.9285, 0.9296, 0.9293, 0.9315, 0.9358, 0.9364, 0.9363, 0.9358, 0.9361, 0.936, 0.9359, 0.9363, 0.9364, 0.9366, 0.9374, 0.9377, 0.9379, 0.9381, 0.9382, 0.9381, 0.9383, 0.938, 0.9382, 0.939, 0.9393, 0.9393, 0.9392, 0.9394, 0.939, 0.9394, 0.9397, 0.9404, 0.9404, 0.9406, 0.9406, 0.9407, 0.9407, 0.9408, 0.9409, 0.941, 0.941, 0.9411, 0.941, 0.9411, 0.9411, 0.9412, 0.9413, 0.9411, 0.9413, 0.9412, 0.9413, 0.9414, 0.9413, 0.9413, 0.9414, 0.9414, 0.9411, 0.9413, 0.9414, 0.9414, 0.9415, 0.9415, 0.9415, 0.9414, 0.9415, 0.9416, 0.9411, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9417, 0.9417, 0.9417, 0.9417, 0.9417, 0.9417, 0.9417, 0.9417, 0.9417, 0.9417, 0.9418, 0.9418, 0.9418, 0.9418, 0.9418, 0.9418, 0.9418, 0.9418, 0.9418, 0.9418, 0.9418, 0.9418, 0.9418, 0.9418, 0.9418, 0.9418, 0.9418, 0.9418, 0.9418, 0.9418, 0.9418, 0.9418, 0.9418, 0.9418, 0.9418, 0.9418, 0.9418, 0.9418, 0.9418, 0.9418, 0.9418]
            //         var testAccList = [0.785, 0.8121, 0.8277, 0.8335, 0.8485, 0.8517, 0.8558, 0.8579, 0.8558, 0.8571, 0.8573, 0.8581, 0.8598, 0.8592, 0.8581, 0.8619, 0.859, 0.8581, 0.8579, 0.8621, 0.861, 0.864, 0.8631, 0.8642, 0.864, 0.8656, 0.8654, 0.8612, 0.8658, 0.864, 0.8638, 0.8627, 0.8615, 0.8625, 0.8635, 0.8646, 0.8615, 0.8631, 0.8642, 0.8633, 0.8615, 0.8608, 0.8602, 0.8617, 0.8612, 0.8633, 0.8619, 0.8629, 0.8638, 0.8617, 0.8629, 0.8688, 0.8712, 0.87, 0.8692, 0.8723, 0.8715, 0.8698, 0.87, 0.8679, 0.8698, 0.8665, 0.8706, 0.8702, 0.8688, 0.8683, 0.8702, 0.8708, 0.8685, 0.8677, 0.8675, 0.8731, 0.8719, 0.8721, 0.8706, 0.8694, 0.8673, 0.8704, 0.8694, 0.8696, 0.87, 0.8692, 0.8694, 0.8694, 0.8692, 0.8692, 0.869, 0.8688, 0.8685, 0.8688, 0.8688, 0.8692, 0.869, 0.8688, 0.8688, 0.8688, 0.8685, 0.8688, 0.869, 0.8692, 0.869, 0.8692, 0.8685, 0.8692, 0.8692, 0.8696, 0.8694, 0.869, 0.869, 0.8692, 0.8692, 0.8694, 0.8694, 0.8696, 0.8694, 0.8685, 0.8692, 0.8692, 0.8694, 0.8694, 0.8696, 0.8694, 0.869, 0.8694, 0.8692, 0.869, 0.8692, 0.8692, 0.8692, 0.8692, 0.869, 0.8694, 0.8694, 0.8692, 0.8692, 0.8694, 0.8694, 0.8694, 0.8692, 0.8698, 0.8698, 0.8698, 0.8698, 0.8698, 0.8698, 0.8698, 0.8698, 0.8698, 0.8698, 0.87, 0.8698, 0.8696, 0.8698, 0.8696, 0.8696, 0.8694, 0.8694, 0.8696, 0.8692, 0.869, 0.8692, 0.8688, 0.869, 0.8685, 0.8688, 0.8685, 0.8683, 0.8688, 0.8685, 0.8685, 0.8685, 0.8685, 0.8685, 0.8683, 0.8683, 0.8683, 0.8683, 0.8683, 0.8685, 0.8683, 0.8685, 0.8685, 0.869, 0.8685, 0.8685, 0.8694, 0.869, 0.8688, 0.8692, 0.869, 0.8694, 0.869, 0.8694, 0.8692, 0.8692, 0.8694, 0.8692, 0.8694, 0.8694, 0.8694]
            //         // this.clsRelated.f1Score = response.data.result.f1
            //         // this.clsRelated.accuracy = response.data.result.accuracy
            //         // this.clsRelated.precision = response.data.result.precision
            //         // this.clsRelated.recall = response.data.result.recall
            //         var lossOption = {
            //             tooltip: {
            //                 trigger: 'axis'
            //             },
            //             xAxis: {
            //                 type: "category",
            //                 name: "epoch",
            //                 boundaryGap: false,
            //                 data: xLableList,
            //             },
            //             yAxis: {
            //                 type: "value",
            //                 name: "loss",
            //             },
            //             series: [{
            //                 name: "模型训练loss",
            //                 type: "line",
            //                 stack: "loss",
            //                 data: lossList,
            //             }],
            //         }
            //         var trainAccOption = {
            //             tooltip: {
            //                 trigger: 'axis'
            //             },
            //             xAxis: {
            //                 type: "category",
            //                 name: "epoch",
            //                 boundaryGap: false,
            //                 data: xLableList,
            //             },
            //             yAxis: {
            //                 type: "value",
            //                 name: "train acc",
            //             },
            //             series: [{
            //                 name: "模型训练集准确率",
            //                 type: "line",
            //                 stack: "train acc",
            //                 data: trainAccList,
            //             }],
            //         }
            //         var testAccOption = {
            //             tooltip: {
            //                 trigger: 'axis'
            //             },
            //             xAxis: {
            //                 type: "category",
            //                 name: "epoch",
            //                 boundaryGap: false,
            //                 data: xLableList,
            //             },
            //             yAxis: {
            //                 type: "value",
            //                 name: "test acc",
            //             },
            //             series: [{
            //                 name: "模型测试集准确率",
            //                 type: "line",
            //                 stack: "test acc",
            //                 data: testAccList,
            //             }],
            //         }
            //         this.showTrainResultFlag = true
            //         this.$nextTick(()=>{
            //             this.LossChart = this.$echarts.init(document.getElementById('chartLoss')),"roma"
            //             this.LossChart.setOption(lossOption)
            //             this.trainAccChart = this.$echarts.init(document.getElementById('chartTrainAcc')),"roma"
            //             this.trainAccChart.setOption(trainAccOption)
            //             this.testAccChart = this.$echarts.init(document.getElementById('chartTestAcc')),"roma"
            //             this.testAccChart.setOption(testAccOption)
            //         })
            // }, 1000);

            this.$axios.post('/nmas/classify/modelTrainCsv', { "method": this.trainRelated.choosetrainModelType, "dataset_dir": this.trainRelated.chooseTrainModelDataFileName }).then(response => {
                console.log(response)
                this.trainningFlag = false
                if (response.data.status == 'success') {
                    alert('模型训练完成')
                    console.log(response.data)
                    if (this.trainRelated.choosetrainModelType == 'lstm') {
                        var xLableList = response.data.result.epochList
                        var lossList = response.data.result.lossList
                        var trainAccList = response.data.result.trainAccList
                        var testAccList = response.data.result.testAccList
                        console.log(xLableList)
                        // var trainAccList = [0.5897, 0.8072, 0.8289, 0.8491, 0.8627, 0.8714, 0.8808, 0.8896, 0.8952, 0.901, 0.9046, 0.9069, 0.9101, 0.9126, 0.9142, 0.9157, 0.9169, 0.9173, 0.9174, 0.9194, 0.921, 0.9226, 0.9224, 0.924, 0.9245, 0.9249, 0.9249, 0.9246, 0.9256, 0.9254, 0.926, 0.9267, 0.9269, 0.9271, 0.9274, 0.9272, 0.9269, 0.9265, 0.9274, 0.9277, 0.9279, 0.9278, 0.9282, 0.9278, 0.9272, 0.9284, 0.928, 0.9287, 0.9285, 0.9296, 0.9293, 0.9315, 0.9358, 0.9364, 0.9363, 0.9358, 0.9361, 0.936, 0.9359, 0.9363, 0.9364, 0.9366, 0.9374, 0.9377, 0.9379, 0.9381, 0.9382, 0.9381, 0.9383, 0.938, 0.9382, 0.939, 0.9393, 0.9393, 0.9392, 0.9394, 0.939, 0.9394, 0.9397, 0.9404, 0.9404, 0.9406, 0.9406, 0.9407, 0.9407, 0.9408, 0.9409, 0.941, 0.941, 0.9411, 0.941, 0.9411, 0.9411, 0.9412, 0.9413, 0.9411, 0.9413, 0.9412, 0.9413, 0.9414, 0.9413, 0.9413, 0.9414, 0.9414, 0.9411, 0.9413, 0.9414, 0.9414, 0.9415, 0.9415, 0.9415, 0.9414, 0.9415, 0.9416, 0.9411, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9416, 0.9417, 0.9417, 0.9417, 0.9417, 0.9417, 0.9417, 0.9417, 0.9417, 0.9417, 0.9417, 0.9418, 0.9418, 0.9418, 0.9418, 0.9418, 0.9418, 0.9418, 0.9418, 0.9418, 0.9418, 0.9418, 0.9418, 0.9418, 0.9418, 0.9418, 0.9418, 0.9418, 0.9418, 0.9418, 0.9418, 0.9418, 0.9418, 0.9418, 0.9418, 0.9418, 0.9418, 0.9418, 0.9418, 0.9418, 0.9418, 0.9418]
                        // var testAccList = [0.785, 0.8121, 0.8277, 0.8335, 0.8485, 0.8517, 0.8558, 0.8579, 0.8558, 0.8571, 0.8573, 0.8581, 0.8598, 0.8592, 0.8581, 0.8619, 0.859, 0.8581, 0.8579, 0.8621, 0.861, 0.864, 0.8631, 0.8642, 0.864, 0.8656, 0.8654, 0.8612, 0.8658, 0.864, 0.8638, 0.8627, 0.8615, 0.8625, 0.8635, 0.8646, 0.8615, 0.8631, 0.8642, 0.8633, 0.8615, 0.8608, 0.8602, 0.8617, 0.8612, 0.8633, 0.8619, 0.8629, 0.8638, 0.8617, 0.8629, 0.8688, 0.8712, 0.87, 0.8692, 0.8723, 0.8715, 0.8698, 0.87, 0.8679, 0.8698, 0.8665, 0.8706, 0.8702, 0.8688, 0.8683, 0.8702, 0.8708, 0.8685, 0.8677, 0.8675, 0.8731, 0.8719, 0.8721, 0.8706, 0.8694, 0.8673, 0.8704, 0.8694, 0.8696, 0.87, 0.8692, 0.8694, 0.8694, 0.8692, 0.8692, 0.869, 0.8688, 0.8685, 0.8688, 0.8688, 0.8692, 0.869, 0.8688, 0.8688, 0.8688, 0.8685, 0.8688, 0.869, 0.8692, 0.869, 0.8692, 0.8685, 0.8692, 0.8692, 0.8696, 0.8694, 0.869, 0.869, 0.8692, 0.8692, 0.8694, 0.8694, 0.8696, 0.8694, 0.8685, 0.8692, 0.8692, 0.8694, 0.8694, 0.8696, 0.8694, 0.869, 0.8694, 0.8692, 0.869, 0.8692, 0.8692, 0.8692, 0.8692, 0.869, 0.8694, 0.8694, 0.8692, 0.8692, 0.8694, 0.8694, 0.8694, 0.8692, 0.8698, 0.8698, 0.8698, 0.8698, 0.8698, 0.8698, 0.8698, 0.8698, 0.8698, 0.8698, 0.87, 0.8698, 0.8696, 0.8698, 0.8696, 0.8696, 0.8694, 0.8694, 0.8696, 0.8692, 0.869, 0.8692, 0.8688, 0.869, 0.8685, 0.8688, 0.8685, 0.8683, 0.8688, 0.8685, 0.8685, 0.8685, 0.8685, 0.8685, 0.8683, 0.8683, 0.8683, 0.8683, 0.8683, 0.8685, 0.8683, 0.8685, 0.8685, 0.869, 0.8685, 0.8685, 0.8694, 0.869, 0.8688, 0.8692, 0.869, 0.8694, 0.869, 0.8694, 0.8692, 0.8692, 0.8694, 0.8692, 0.8694, 0.8694, 0.8694]
                        this.clsRelated.f1Score = response.data.result.f1
                        this.clsRelated.accuracy = response.data.result.accuracy
                        this.clsRelated.precision = response.data.result.precision
                        this.clsRelated.recall = response.data.result.recall
                        var lossOption = {
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
                            }],
                        }
                        var trainAccOption = {
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
                                name: "train acc",
                            },
                            series: [{
                                name: "模型训练集准确率",
                                type: "line",
                                stack: "train acc",
                                data: trainAccList,
                            }],
                        }
                        var testAccOption = {
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
                                name: "test acc",
                            },
                            series: [{
                                name: "模型测试集准确率",
                                type: "line",
                                stack: "test acc",
                                data: testAccList,
                            }],
                        }
                        this.showTrainResultFlag = true
                        this.showTrainLSTMResultFlag = true
                        this.$nextTick(() => {
                            this.LossChart = this.$echarts.init(document.getElementById('chartLoss'), "roma")
                            this.LossChart.setOption(lossOption)
                            this.trainAccChart = this.$echarts.init(document.getElementById('chartTrainAcc'), "roma")
                            this.trainAccChart.setOption(trainAccOption)
                            this.testAccChart = this.$echarts.init(document.getElementById('chartTestAcc'), "roma")
                            this.testAccChart.setOption(testAccOption)

                            window.onresize = () => {
                                if (this.LossChart != null) {
                                    this.LossChart.resize()
                                }
                                if (this.trainAccChart != null) {
                                    this.trainAccChart.resize()
                                }
                                if (this.testAccChart != null) {
                                    this.testAccChart.resize()
                                }
                            }
                        })
                    }else{
                        var bestModel = response.data.result.AdaBoost
                        if(bestModel.f1 < response.data.result.DecisionTree.f1){
                            bestModel = response.data.result.DecisionTree
                        }
                        if(bestModel.f1 < response.data.result.RandomForest.f1){
                            bestModel = response.data.result.RandomForest
                        }
                        this.clsRelated.f1Score = bestModel.f1
                        this.clsRelated.accuracy = bestModel.accuracy
                        this.clsRelated.precision = bestModel.precision
                        this.clsRelated.recall = bestModel.recall
                        this.showTrainResultFlag = true
                        this.showTrainLSTMResultFlag = false
                    }

                } else {
                    alert('模型训练失败，请重试')
                }
            }, response => {
                this.trainningFlag = false
                alert('模型训练失败，请重试')
                console.log(response)
            })
        },

        startCls() {
            if(this.clsRelated.startTime != ''){
                this.clsRelated.startTime = this.clsRelated.startTime.replace(/T/,' ') + ":00"
            }
            if(this.clsRelated.endTime != ''){
                this.clsRelated.endTime = this.clsRelated.endTime.replace(/T/,' ') + ":00"
            }
            const ipReg = /^(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])$/;
            if(!(this.clsRelated.ipFilter == '' || ipReg.test(this.clsRelated.ipFilter))){
                alert('请输入正确的IP地址')
                return
            }

            let confidence = 0.4

            if(this.clsRelated.confidence != ''){
                if(!(this.clsRelated.confidence <= 1 && this.clsRelated.confidence >= 0)){
                    alert('请输入正确的置信度,置信度应在0-1之间')
                    return
                }
                confidence = this.clsRelated.confidence
            }


            console.log(this.clsRelated)
            this.clsingFlag = true

            // setTimeout(() => {
            //     let labelCount = {
            //         "streaming": 190,
            //         "Unknow": 71,
            //         "webhttps": 56,
            //         "fileupload": 16,
            //         "p2p": 15
            //     }
            //     let labelAvgProd = {
            //         "streaming": 0.9895178390176673,
            //         "Unknow": 0.9317230044955939,
            //         "webhttps": 0.9200082985418183,
            //         "fileupload": 0.6371835507452487,
            //         "p2p": 0.968221378326416
            //     }
            //     var legendData = new Array()
            //     var pieData = new Array()
            //     for(let key in labelCount){
            //         legendData.push(key)
            //         pieData.push({
            //             'value':labelCount[key],
            //             'name':key,
            //             'avg_prod':labelAvgProd[key]
            //         })
            //     }
            //     let option = {
            //             title: {
            //             text: '最新业务分类结果',
            //         },
            //         //鼠标划过时饼状图上显示的数据
            //         tooltip: {
            //             trigger: 'item',
            //             triggerOn: "mousemove",
            //             axisPointer: {
            //                 // 坐标轴指示器，坐标轴触发有效
            //                 type: 'shadow', // 默认为直线，可选为：'line' | 'shadow'
            //             },
            //             showContent: true,                       //是否显示提示框浮层
            //             formatter: '{a}<br/>{b}:{c} ({d}%)'
            //         },
            //         //图例
            //         legend: {
            //             bottom: 10,//控制图例出现的距离  默认左上角
            //             left: 'center',//控制图例的位置
            //             // itemWidth: 16,//图例颜色块的宽度和高度
            //             // itemHeight: 12,
            //             textStyle: {//图例中文字的样式
            //                 color: '#000',
            //                 fontSize: 16
            //             },
            //             data: legendData//图例上显示的饼图各模块上的名字
            //         },
            //         series: [{
            //             type: 'pie',             //echarts图的类型   pie代表饼图
            //             radius: ['50%', '70%'],           //饼图中饼状部分的大小所占整个父元素的百分比
            //             center: ['50%', '50%'],
            //             data: pieData,

            //             itemStyle: {
            //                 normal: {
            //                     label: {
            //                         show: true, //饼图上是否出现标注文字 标注各模块代表什么  默认是true
            //                     },
            //                     labelLine: {
            //                         show: true, //官网demo里外部标注上的小细线的显示隐藏    默认显示
            //                     }
            //                 }
            //             }
            //         }]
            //         }
            //     this.showClsResultFlag = true
            //     this.$nextTick(()=>{
            //         this.drawPie('clsPie',option)
            //     })

            //     this.clsingFlag = false
            // }, 1000);

                //     legendData: ['chat', 'p2p', 'video', 'text', 'game'],
                // data: [
                //     { value: 20, name: 'chat' },
                //     { value: 20, name: 'p2p' },
                //     { value: 20, name: 'video' },
                //     { value: 20, name: 'text' },
                //     { value: 20, name: 'game' }
                // ]

            this.$axios.post("/nmas/classify/modelPredSQL",{
                'method':this.clsRelated.chooseClsModelType,
                'threshold':confidence,
                'ip':this.clsRelated.ipFilter,
                'time_start':this.clsRelated.startTime,
                'time_end':this.clsRelated.endTime
            }).then(resp=>{
                if(resp.data.status == 'success'){
                    let labelCount = resp.data.result.label_count
                    let labelAvgProd = resp.data.result.label_avg_prod
                    var legendData = new Array()
                    var pieData = new Array()
                    for(let key in labelCount){
                        legendData.push(key)
                        pieData.push({
                            'value':labelCount[key],
                            'name':key,
                            'avg_prod':labelAvgProd[key]
                        })
                    }

                    for(let item in labelCount){
                        console.log(item)
                    }
                    let option = {
                        title: {
                        text: '业务分类结果',
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
                        data: legendData//图例上显示的饼图各模块上的名字
                    },
                    series: [{
                        type: 'pie',             //echarts图的类型   pie代表饼图
                        radius: ['50%', '70%'],           //饼图中饼状部分的大小所占整个父元素的百分比
                        center: ['50%', '50%'],
                        data:pieData,
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
                    this.showClsResultFlag = true
                    this.$nextTick(()=>{
                        this.drawPie('clsPie',option)
                    })
                    this.clsingFlag = false
                }else{
                    alert(resp.data.err)
                    this.showClsResultFlag = false
                    this.clsingFlag = false
                }
            },response =>{
                alert("流量分类失败，请重试！")
                this.clsingFlag = false
            })
        },

        drawPie(id, option) {
            // console.log(data)
            let chart = this.$echarts.init(document.getElementById(id), "roma");
            // console.log('after init')
            chart.setOption(option)
            window.addEventListener("resize", () => {
                // 第六步，执行echarts自带的resize方法，即可做到让echarts图表自适应
                chart.resize();
                // 如果有多个echarts，就在这里执行多个echarts实例的resize方法,不过一般要做组件化开发，即一个.vue文件只会放置一个echarts实例
                /*
                this.myChart2.resize();
                this.myChart3.resize();
                ......
                */
            });
            // chart.on('mouseover',function(params){
            //     const [name,value] = params.data
            //     chart.setOption({
            //         title:{
            //             text:name,
            //             subtext:value,
            //             left:'center',
            //             top:'center'
            //         }
            //     })
            // })
        },

        drawLine(id, option) {
            let chart = this.$echarts.init(document.getElementById(id), "roma");
            chart.setOption(option)
        }

    },
    components: { BgCover },
}
</script>

<style scoped>
/* 开始检测按钮 */
.btn-detect {
    background: linear-gradient(135deg, #0d6efd, #6da5f9); /* 绿色渐变 */
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
    background: linear-gradient(135deg, #0d6efd, #6da5f9); /* 橙色渐变 */
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
    background: linear-gradient(135deg, #dc3545, #d9606c); /* 红色渐变 */
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
.hover-bg {
  background-color: #e4ebf2; /* 鼠标悬停时的背景颜色 */
}

.alert .btn-danger {
  font-size: 0.8rem;
  padding: 0.2rem 0.4rem;
}
.page-wrapper {
  min-height: 100vh; 
  margin: 0;
  padding: 0;
}
.page-content {
  margin: 0;
  padding: 0;
}
.select-padding {
    padding-right: 20px;
}
.upload-section select.form-select {
  color: #c0c4cc; /* 将文字颜色设置为较暗的灰色，你可以调整这个颜色值来满足需求 */
}

.chip:hover {
  background-color: #007bff; /* 悬停时背景色变为蓝色 */
  color: #fff; /* 文字颜色变为白色 */
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2); /* 增强阴影效果 */
  transform: translateY(-2px); /* 悬停时微微抬起 */
}

.chip i {
  transform: translateY(-2px);
}

.nav-link {
  margin-right: 10px;
  border-radius: 20px;
  transition: all 0.3s ease; /* 添加过渡动画 */
}

.nav-link:hover {
  background-color: #73b2f6; /* 鼠标悬停时背景变为蓝色 */
  color: white; /* 字体颜色变为白色 */
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.15); /* 增加悬停时阴影效果 */
  transform: translateY(-2px);
}

.nav-link.active {
  background-color: #007bff; /* 激活时背景变为蓝色 */
  color: white;
}

</style>