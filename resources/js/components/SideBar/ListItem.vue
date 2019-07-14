<template>
    <li :class="[
        className,
        {
            disabled: disabled
        }
    ]">
        <a :href="url">
            <i class="fa fa-fw mr-2" :class="icon"></i> {{ text }}
        </a>
    </li>
</template>

<script>
    export default {
        props: [
            'activeRoute',
            'url',
            'icon',
            'text',
            'disabled',
        ],
        data() {
            return {
            };
        },
        computed: {
            className() {
                return this.url == this.$root.App.current_path ? 'active' : '';
            }
        }
    }
</script>
