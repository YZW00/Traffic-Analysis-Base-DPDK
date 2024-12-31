<template>
    <ul>
        <template v-for="item in data" :key="item.key">
            <li ref="listNode">
                <ArrowRight v-if="item.children && isFolded(item)" @click="switchFold(item)" />
                <ArrowDown v-else-if="item.children" @click="switchFold(item)" />
                <Empty v-else />
                <span :class="{ selected:item.key == selected }"
                  @mousedown.left="clickItem(item)"
                  @dblclick="switchFold(item)">
                    {{ item.label }}
                </span>
            </li>
            <PacketDetail v-if="item.children" :data="item.children" v-show="!isFolded(item)"
            v-model:selected-key="selected" v-model:unfolded-key="unfolded"/>
        </template>
    </ul>
</template>

<script setup>
import { computed, nextTick, ref, watch } from 'vue'

import ArrowRight from '@/assets/icon/arrow-right.vue'
import ArrowDown from '@/assets/icon/arrow-down.vue'
import Empty from '@/assets/icon/empty.vue'

import PacketDetail from '@/components/PacketDetail.vue'

const emit = defineEmits(['update:selectedKey', 'update:unfoldedKey'])
const props = defineProps({
    data: Array,
    selectedKey: String,
    unfoldedKey: {
        type: Array,
        default: []
    }
})
const listNode = ref(null)
const selected = computed({
    get() {
        return props.selectedKey
    },
    set(value) {
        emit('update:selectedKey', value)
    }
})
watch(selected, (newValue) => {
    const index = props.data.findIndex(e => e.key == newValue)
    if (index > -1) {
        nextTick(() => {
            const element = listNode.value[index]
            if (element.offsetParent) {
                element.offsetParent.scroll({
                    left: element.offsetLeft,
                    top: element.offsetTop,
                    behavior: 'smooth'
                })
            }
        })
    }
})
const unfolded = computed({
    get() {
        return props.unfoldedKey
    },
    set(value) {
        emit('update:unfoldedKey', value)
    }
})

function isFolded(item) {
    return !unfolded.value.includes(item.key)
}

/* Event handler */
function switchFold(item) {
    if (item.children) {
        if (isFolded(item)) {
            unfolded.value = unfolded.value.concat([item.key])
        } else {
            unfolded.value = unfolded.value.filter(e => e != item.key)
        }
    }
}
function clickItem(item) {
    if (item.key == selected.value) {
        selected.value = null
    } else {
        selected.value = item.key
    }
}
</script>

<style scoped>
    ul {
        list-style: none; /* 去除默认样式 */
        padding-left: 0;  /* 去除左侧缩进 */
        overflow: hidden; /* 折叠时隐藏显示 */
        word-break: break-all; /* 禁止右侧空间不够时按单词截断 */
        user-select: none;/* 禁止选中文本 */
        display: block;
    }
    ul ul {
        margin-left: 1em; /* 子列表缩进 */
    }
    li {
        display: flex;       /* 垂直居中 */
        align-items: center; /* 垂直居中 */
        width: auto;
        text-align: left;
        line-height: normal;
    }
    span {
        width: 100%;         /* 占满容器 */
        height: 1.6em;       /* 1.6倍行高 */
        padding-left: 5px;   /* 美化文字左侧缝隙 */
        overflow: hidden;    /* 宽度不够时禁止换行 */
    }
    svg {
        height: 1em;   /* 图标尺寸 */
        width: 1em;    /* 图标尺寸 */
    }
    span:hover {
        background-color: #E5F3FF; /* 悬停弱提示色 */
    }
    .selected {
        background-color: #CDE5FF; /* 点击强调色 */
    }
    span:active,span:hover.selected {
        background-color: #CDE5FF; /* 点击强调色 */
        box-shadow: inset 0 0 0 1px #99D1FF; /* 强调边框色 */
    }
</style>
