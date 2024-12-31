<template>
    <div class="flex sgcc-row sgcc-head">
        <span class="cell" style="width: 5%; padding-left: 3px;">No.</span>
        <span class="cell" style="width: 7.5%">Time</span>
        <span class="cell" style="width: 10%">Source</span>
        <span class="cell" style="width: 10%">Destination</span>
        <span class="cell" style="width: 5%">Protocol</span>
        <span class="cell" style="width: 5%">Length</span>
        <span class="cell" style="width: 57.5%">Info</span>
    </div>
    <RecycleScroller
        ref="scroller"
        :items="data"
        :item-size="16"
        keyField="num"
        class="flex-grow-1 overflow-x-hidden overflow-y-auto"
        v-slot="{ item }"
    >
      <div
        class="flex sgcc-row"
        :style="{
            '--bg-color': '#' + item.bg || '#ffffff',
            color: '#' + item.fg || '#ffffff',
            '--hover-color': '#' + mixColor(item.bg || 'ffffff', '90D0FF', 0.2)
        }"
        @click="rowClick(item)"
      >
        <span class="cell" style="width: 5%; padding-left: 3px;">{{ item.c[0] }}</span>
        <span class="cell" style="width: 7.5%">{{ item.c[1] }}</span>
        <span class="cell" style="width: 10%">{{ item.c[2] }}</span>
        <span class="cell" style="width: 10%">{{ item.c[3] }}</span>
        <span class="cell" style="width: 5%">{{ item.c[4] }}</span>
        <span class="cell" style="width: 5%">{{ item.c[5] }}</span>
        <span class="cell" style="width: 57.5%">{{ item.c[6] }}</span>
      </div>
  </RecycleScroller>
</template>

<script setup>
import { defineProps, ref, defineExpose } from 'vue'
import { RecycleScroller } from 'vue-virtual-scroller'

const emits = defineEmits(['rowClick'])
const props = defineProps({
    data: {
        required: true
    }
})

function mixColor(colorStrA, colorStrB, alpha) {
    const oldColor = parseInt(colorStrA, 16)
    const addColor = parseInt(colorStrB, 16)
    const [Ra, Ga, Ba] = [(addColor>>16), (addColor>>8)&0xFF, (addColor&0xFF)];
    let [R, G, B] = [(oldColor>>16), (oldColor>>8)&0xFF, (oldColor&0xFF)];
    [R, G, B] = [(1-alpha)*R+alpha*Ra, (1-alpha)*G+alpha*Ga, (1-alpha)*B+alpha*Ba];
    [R, G, B] = [Math.floor(R), Math.floor(G), Math.floor(B)];
    return ((R << 16) | (G << 8) | B).toString(16)
}

function rowClick(item) {
    emits('rowClick', { data : item })
}

const scroller = ref(null)
function scorllToItem(idx) {
    scroller.value.scrollToItem(idx)
}

defineExpose({
    scorllToItem
})

</script>

<style scoped>
.cell {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.sgcc-row {
    cursor: pointer;
    gap: 0.5%;
    background-color: var(--bg-color);
}

.sgcc-row:hover {
    background-color: var(--hover-color);
}

.sgcc-head>span {
    border-right: 1px solid #E5E5E5;
    font-weight: strong;
}
</style>
