<template>
    <div class="page-wrapper">
        <div class="page-content">
            <div class="row row-cols-1 row-cols-md-2 row-cols-xl-4">
                <div class="col">
                    <div class="card radius-10 border-start border-0 border-3 border-info">
                    <div class="card-body">
                        <div class="d-flex align-items-center">
                            <div>
                                <p class="mb-0 text-secondary">Total Orders</p>
                                <h4 class="my-1 text-info">4805</h4>
                                <p class="mb-0 font-13">+2.5% from last week</p>
                            </div>
                            <div class="widgets-icons-2 rounded-circle bg-gradient-scooter text-white ms-auto"><i class='bx bxs-cart'></i>
                            </div>
                        </div>
                    </div>
                    </div>
                </div>
                <div class="col">
                <div class="card radius-10 border-start border-0 border-3 border-danger">
                    <div class="card-body">
                        <div class="d-flex align-items-center">
                            <div>
                                <p class="mb-0 text-secondary">Total Revenue</p>
                                <h4 class="my-1 text-danger">$84,245</h4>
                                <p class="mb-0 font-13">+5.4% from last week</p>
                            </div>
                            <div class="widgets-icons-2 rounded-circle bg-gradient-bloody text-white ms-auto"><i class='bx bxs-wallet'></i>
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
                                <p class="mb-0 text-secondary">Bounce Rate</p>
                                <h4 class="my-1 text-success">34.6%</h4>
                                <p class="mb-0 font-13">-4.5% from last week</p>
                            </div>
                            <div class="widgets-icons-2 rounded-circle bg-gradient-ohhappiness text-white ms-auto"><i class='bx bxs-bar-chart-alt-2' ></i>
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
                                <p class="mb-0 text-secondary">Total Customers</p>
                                <h4 class="my-1 text-warning">8.4K</h4>
                                <p class="mb-0 font-13">+8.4% from last week</p>
                            </div>
                            <div class="widgets-icons-2 rounded-circle bg-gradient-blooker text-white ms-auto"><i class='bx bxs-group'></i>
                            </div>
                        </div>
                    </div>
                </div>
                </div> 
            </div><!--end row-->

            <div class="row">
                <div class="col-12 col-lg-8">
                    <div class="card radius-10">
                        <div class="card-body">
                            <div class="d-flex align-items-center">
                                <div>
                                    <h6 class="mb-0">被管网流量(最近七天)</h6>
                                </div>
                            </div>
                            <!-- <div class="d-flex align-items-center ms-auto font-13 gap-2 my-3">
                                <span class="border px-1 rounded cursor-pointer"><i class="bx bxs-circle me-1" style="color: #7cb5ec"></i>入方向</span>
                                <span class="border px-1 rounded cursor-pointer"><i class="bx bxs-circle me-1" style="color: #f7a35c"></i>出方向</span>
                            </div> -->
                            <ul class="list-group list-group-flush">
                                <li class="list-group-item">
                                    <div class="chart-container-2">
                                        <canvas id="totaltraffic-bps"></canvas>
                                    </div>
                                </li>
                                <li class="list-group-item">
                                    <div class="chart-container-2">
                                        <canvas id="totaltraffic-pps"></canvas>
                                    </div>
                                </li>
                            </ul>
                        </div>
                    </div>
                </div>
                <div class="col-12 col-lg-4">
                    <div class="card radius-10">
                        <div class="card-body">
                            <div class="d-flex align-items-center">
                                <div>
                                    <h6 class="mb-0">端口占用情况</h6>
                                </div>
                            </div>
                            <ul class="list-group list-group-flush">
                                <li class="list-group-item ">
                                    <div class="chart-container-2 mt-4 position-relative">
                                        <span class="badge bg-secondary font-13 position-absolute top-0 start-0">入端口</span>
                                        <canvas id="port-static-in" class="position-absolute top-0 start-0"></canvas>
                                    </div>
                                </li>
                                <li class="list-group-item">
                                    <div class="chart-container-2 mt-4 position-relative">
                                        <span class="badge bg-secondary font-13 position-absolute top-0 start-0">出端口</span>
                                        <canvas id="port-static-out" class="position-absolute top-0 start-0"></canvas>
                                    </div>
                                </li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div><!--end row-->

                <div class="card radius-10">
                    <div class="card-body">
                        <div class="d-flex align-items-center">
                            <div>
                                <h6 class="mb-0">分类流量行为</h6>
                            </div>
                            <ul class="nav nav-tabs ms-auto" role="tablist">
                                <li class="nav-item mx-1" role="presentation">
                                <button class="nav-link active" id="ingroup-tab" data-bs-toggle="tab" data-bs-target="#ingroup" type="button" aria-current="page">入方向</button>
                                </li>
                                <li class="nav-item" role="presentation">
                                <button class="nav-link" id="outgroup-tab" data-bs-toggle="tab" data-bs-target="#outgroup" type="button">出方向</button>
                                </li>
                            </ul>
                        </div>		  
                        <div class="tab-content" id="nav-tabContent">
                            <div class="tab-pane show active" id="ingroup" role="tabpanel" aria-labelledby="ingroup-tab">
                                <table class="table table-hover align-middle mb-0">
                                    <!-- REMOVE: "../static/images/products/0*.png" -->
                                    <thead class="text-center">
                                        <tr><th>流记录源地址</th><th>流记录宿地址</th><th>流数</th><th>报文数</th><th>字节数</th></tr>
                                    </thead>
                                    <tbody id="ingroup-body">
                                    </tbody>
                                </table>
                            </div>
                            <div class="tab-pane" id="outgroup" role="tabpanel" aria-labelledby="outgroup-tab">
                                <table class="table table-hover align-middle mb-0">
                                    <thead class="text-center">
                                        <tr><th>流记录源地址</th><th>流记录宿地址</th><th>流数</th><th>报文数</th><th>字节数</th></tr>
                                    </thead>
                                    <tbody id="outgroup-body">
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>


                <div class="row">
                    <div class="col-12 col-lg-7 col-xl-8 d-flex">
                        <div class="card radius-10 w-100">
                        <div class="card-header bg-transparent">
                            <div class="d-flex align-items-center">
                                <div>
                                    <h6 class="mb-0">Recent Orders</h6>
                                </div>
                                <div class="dropdown ms-auto">
                                    <a class="dropdown-toggle dropdown-toggle-nocaret" href="#" data-bs-toggle="dropdown"><i class='bx bx-dots-horizontal-rounded font-22 text-option'></i>
                                    </a>
                                    <ul class="dropdown-menu">
                                        <li><a class="dropdown-item" href="javascript:;">Action</a>
                                        </li>
                                        <li><a class="dropdown-item" href="javascript:;">Another action</a>
                                        </li>
                                        <li>
                                            <hr class="dropdown-divider">
                                        </li>
                                        <li><a class="dropdown-item" href="javascript:;">Something else here</a>
                                        </li>
                                    </ul>
                                </div>
                            </div>
                            </div>
                            <div class="card-body">
                            <div class="row">
                                <div class="col-lg-7 col-xl-8 border-end">
                                    <div id="geographic-map-2"></div>
                                </div>
                                <div class="col-lg-5 col-xl-4">
                                
                                <div class="mb-4">
                                <p class="mb-2"><i class="flag-icon flag-icon-us me-1"></i> USA <span class="float-end">70%</span></p>
                                <div class="progress" style="height: 7px;">
                                        <div class="progress-bar bg-primary progress-bar-striped" role="progressbar" style="width: 70%"></div>
                                    </div>
                                </div>
            
                                <div class="mb-4">
                                    <p class="mb-2"><i class="flag-icon flag-icon-ca me-1"></i> Canada <span class="float-end">65%</span></p>
                                    <div class="progress" style="height: 7px;">
                                        <div class="progress-bar bg-danger progress-bar-striped" role="progressbar" style="width: 65%"></div>
                                    </div>
                                </div>
            
                                <div class="mb-4">
                                    <p class="mb-2"><i class="flag-icon flag-icon-gb me-1"></i> England <span class="float-end">60%</span></p>
                                    <div class="progress" style="height: 7px;">
                                        <div class="progress-bar bg-success progress-bar-striped" role="progressbar" style="width: 60%"></div>
                                    </div>
                                </div>
            
                                <div class="mb-4">
                                    <p class="mb-2"><i class="flag-icon flag-icon-au me-1"></i> Australia <span class="float-end">55%</span></p>
                                    <div class="progress" style="height: 7px;">
                                        <div class="progress-bar bg-warning progress-bar-striped" role="progressbar" style="width: 55%"></div>
                                    </div>
                                </div>
            
                                <div class="mb-4">
                                    <p class="mb-2"><i class="flag-icon flag-icon-in me-1"></i> India <span class="float-end">50%</span></p>
                                    <div class="progress" style="height: 7px;">
                                        <div class="progress-bar bg-info progress-bar-striped" role="progressbar" style="width: 50%"></div>
                                    </div>
                                </div>

                                <div class="mb-0">
                                    <p class="mb-2"><i class="flag-icon flag-icon-cn me-1"></i> China <span class="float-end">45%</span></p>
                                    <div class="progress" style="height: 7px;">
                                        <div class="progress-bar bg-dark progress-bar-striped" role="progressbar" style="width: 45%"></div>
                                        </div>
                                </div>

                                </div>
                            </div>
                            </div>
                        </div>
                    </div>
            
                    <div class="col-12 col-lg-5 col-xl-4 d-flex">
                        <div class="card w-100 radius-10">
                            <div class="card-body">
                            <div class="card radius-10 border shadow-none">
                            <div class="card-body">
                                <div class="d-flex align-items-center">
                                    <div>
                                        <p class="mb-0 text-secondary">Total Likes</p>
                                        <h4 class="my-1">45.6M</h4>
                                        <p class="mb-0 font-13">+6.2% from last week</p>
                                    </div>
                                    <div class="widgets-icons-2 bg-gradient-cosmic text-white ms-auto"><i class='bx bxs-heart-circle'></i>
                                    </div>
                                </div>
                            </div>
                            </div>
                            <div class="card radius-10 border shadow-none">
                            <div class="card-body">
                                <div class="d-flex align-items-center">
                                    <div>
                                        <p class="mb-0 text-secondary">Comments</p>
                                        <h4 class="my-1">25.6K</h4>
                                        <p class="mb-0 font-13">+3.7% from last week</p>
                                    </div>
                                    <div class="widgets-icons-2 bg-gradient-ibiza text-white ms-auto"><i class='bx bxs-comment-detail'></i>
                                    </div>
                                </div>
                            </div>
                            </div>
                            <div class="card radius-10 mb-0 border shadow-none">
                            <div class="card-body">
                                <div class="d-flex align-items-center">
                                    <div>
                                        <p class="mb-0 text-secondary">Total Shares</p>
                                        <h4 class="my-1">85.4M</h4>
                                        <p class="mb-0 font-13">+4.6% from last week</p>
                                    </div>
                                    <div class="widgets-icons-2 bg-gradient-moonlit text-white ms-auto"><i class='bx bxs-share-alt'></i>
                                    </div>
                                </div>
                            </div>
                            </div>
                            </div>

                        </div>
            
                    </div>
                    </div><!--end row-->
        </div>
    </div>
</template>

<script>

</script>

<style>
</style>