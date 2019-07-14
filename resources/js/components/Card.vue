<template>
    <div class="card card-default">
        <div class="card-header" v-html="cardHeader"></div>

        <div class="card-body">
            <slot></slot>
        </div>
    </div>
</template>

<script>
    export default {
        props: ['cardHeader'],
    }
</script>
