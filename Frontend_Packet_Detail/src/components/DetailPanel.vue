<template>
    <Splitter style="height: calc(100vh - 40px - 3rem - 12px - 2rem)" layout="vertical">
        <SplitterPanel :size="60" class="flex flex-column min-h-0">
            <slot name="packet-list" />
        </SplitterPanel>
        <SplitterPanel :size="40" class="min-h-0">
            <Splitter layout="horizontal">
                <SplitterPanel :size="60" class="flex">
                    <ScrollPanel class="flex-grow-1">
                        <slot name="packet-detail" />
                    </ScrollPanel>
                </SplitterPanel>
                <SplitterPanel :size="40" class="flex">
                    <ScrollPanel class="flex-grow-1 overflow-hidden" style="width: 0">
                        <slot name="packet-hex" />
                    </ScrollPanel>
                </SplitterPanel>
            </Splitter>
        </SplitterPanel>
    </Splitter>
</template>

<script setup>
import Splitter from 'primevue/splitter'
import SplitterPanel from 'primevue/splitterpanel'
import ScrollPanel from 'primevue/scrollpanel'
</script>
