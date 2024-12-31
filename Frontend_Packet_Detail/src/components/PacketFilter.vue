<template>
    
<div class="grid m-1">
    <InputText class="col border-noround" type="text" v-model="interValue" />
    <Button class="col-fixed border-noround" label="过滤" :disabled="realTime && !config?.allowRealTimeFilter" style="background-color: rgb(62, 135, 217);" @click="buttonClick"/>
    <Button class="col-fixed border-noround ml-1 w-8rem" v-if="realTime" label="停止" style="background-color: rgb(62, 135, 217);" @click="stopCapture"/>
</div>
</template>

<script setup>
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'
import { computed } from 'vue';

const props = defineProps({
    value: String,
    realTime: Boolean,
    config: Object
})
const emit = defineEmits(['update:value', 'setFilter', 'stopCapture'])

const interValue = computed({
    get() {
        return props.value
    },
    set(newValue) {
        emit('update:value', newValue)
    }
})

function buttonClick() {
    emit('setFilter', interValue.value)
}

function stopCapture() {
    emit('stopCapture')
}
</script>
