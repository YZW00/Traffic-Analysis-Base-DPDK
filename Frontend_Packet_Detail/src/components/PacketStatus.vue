<template>
    <div class="flex justify-content-between align-items-center text-base h-2rem">
        <div class="flex gap-3 ml-2">
            <p v-if="realTime">
                实时模式
            </p>
            <template v-else>
                <p v-if="isLoading">正在载入...</p>
                <p v-else-if="isCompleted">文件加载完成</p>
                <p v-else>初始化中, 请稍后...</p>
            </template>
            <ProgressBar :value="percent" :showValue="false"
            class="w-10rem h-1rem" v-if="isLoading"
            :pt="{
                root: { class: 'border-noround bg-white border-solid border-1 surface-border' }
            }"/>
        </div>
        <Divider layout="vertical"/>
        <div class="flex gap-3 mr-2" v-if="isLoading || isCompleted">
            <p>分组: {{ total }}</p>
            <p>已加载: {{ loaded }} ({{percent}}%)</p>
        </div>
        <div v-else></div>
    </div>
</template>

<script setup>
import ProgressBar from 'primevue/progressbar'
import Divider from 'primevue/divider'

import { computed } from 'vue';

const props = defineProps({
    total: Number,
    loaded: Number,
    forceFinish: Boolean,
    realTime: Boolean
})

const percent = computed(() => Math.floor(props.loaded*100/props.total))
const isLoading = computed(() => (props.loaded < props.total && props.loaded > -1) && !props.forceFinish && !props.realTime)
const isCompleted = computed(() => ((props.loaded >= props.total && props.loaded > -1) || props.forceFinish) && !props.realTime)
</script>
