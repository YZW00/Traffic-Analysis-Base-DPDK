<template>
    <Dialog :visible="visible"
      modal :closable="false" :draggable="false" :showHeader="false"
      :pt="{
            content: { class: 'p-0 border-round' }
        }">
        <div class="flex flex-column align-items-end select-none">
            <div class="flex p-3 gap-4 align-items-center mt-2 mb-0 mx-6">
                <img src="@/assets/icon/shark.svg" alt="icon" class="w-12rem h-12rem cool-rotate">
                <div class="flex flex-column align-items-end font-normal">
                    <h2 class="font-bold text-4xl sgcc-color mb-3">在线报文解析</h2>
                    <h4 class="text-sm sgcc-secondary mb-4">Online packet dissector</h4>
                </div>
            </div>
            <ProgressBar :value="value" :showValue="false"
              style="height: 6px" class="w-full"
              :mode="value >= 0 ? 'determinate' : 'indeterminate' "
              :pt="{
                root: { class: 'border-noround' }
              }"/>
            <p class="p-1 font-light text-sm sgcc-gray">{{ text }}</p>
        </div>
    </Dialog>
</template>

<script setup>
import Dialog from 'primevue/dialog'
import ProgressBar from 'primevue/progressbar'

defineProps({
    visible: Boolean,
    value: Number,
    text: String
})
</script>

<style scoped>
.sgcc-color {
    background-image: linear-gradient(to right, #0B9471, #00594F);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
}
.sgcc-gray {
    color: #8D9092;
}
.sgcc-secondary {
    color: #4EB7A6;
}

::v-deep(div .p-progressbar-value) {
    background-color: #0B9471;
}

.cool-rotate {
    /* animation: cool 1s linear infinite; */
}

@keyframes cool {
    0% {  transform: rotate(0deg); }
    50% {  transform: rotate(180deg); }
    100% {  transform: rotate(360deg); }
}
</style>
