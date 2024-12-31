<template>
    <div class="page-wrapper">
	    <div class="page-content">
            <div class="card">
                <div class="card-body">
                    <div class="accordion accordion-flush">
                        <div class="accordion-item">
                            <h2 class="accordion-header" id="setting1">
                                <button class="accordion-button collapsed" type="button" id="setting-btn1" @click="toggleAccordion('setting-btn1','setting-content1')">
                                模型参数设置
                                </button>
                            </h2>
                            <div id="setting-content1" class="accordion-collapse collapse">
                                <div class="accordion-body">
                                    <form>
                                        <div class="input-group mb-3"> <span class="input-group-text" id="inputGroup-sizing-default">参数1</span>
                                            <input type="text" class="form-control" aria-label="Sizing example input" aria-describedby="inputGroup-sizing-default" :value="setting1.label1">
                                        </div>
                                        <div class="input-group mb-3"> <span class="input-group-text" id="inputGroup-sizing-default">参数2</span>
                                            <input type="text" class="form-control" aria-label="Sizing example input" aria-describedby="inputGroup-sizing-default" :value="setting1.label2">
                                        </div>
                                    </form>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
    export default{
        data(){
            return {
                setting1:{
                    label1:'aaa',
                    label2:'bbb'
                }
            }
        },

        methods:{
            toggleAccordion(btnId,contentId){
                // 如果隐藏
                if($("#"+btnId).hasClass('collapsed')){
                    $("#"+btnId).attr('class','accordion-button')
                    $("#"+contentId).show(300)
                    // $("#"+contentId).animate({'class':'accordion-collapse collapse show'},300)
                    // $("#"+contentId).attr('class','accordion-collapse collapse show')
                }else{
                    $("#"+btnId).attr('class','accordion-button collapsed')
                    $("#"+contentId).hide(300)
                    // $("#"+contentId).animate({'class':'accordion-collapse collapse'},300)
                    // $("#"+contentId).attr('class','accordion-collapse collapse')
                }
            }
        }
    }
</script>