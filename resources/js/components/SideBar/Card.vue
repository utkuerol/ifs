<template>
    <div class="card nav-card">
        <div class="card-header" @click="mutableIsOpen = !mutableIsOpen" style="cursor: pointer;">
            {{ header }}
            <i class="fa fa-fw pull-right" :class="iconClass" style="margin: 4px;"></i>
        </div>

        <slide-up-down ref="slider" :active="mutableIsOpen" :duration="500">
            <div class="nav-tabs">
                <slot></slot>
            </div>
        </slide-up-down>
    </div>
</template>

<script>
    export default {
        props: [
            'header',
            'isOpen',
        ],
        data() {
            return {
                mutableIsOpen: null,
            };
        },
        methods: {
            childrenOpen() {
                for (var i = this.$refs['slider'].$children.length - 1; i >= 0; i--) {
                    if (this.$refs['slider'].$children[i].activeRoute == this.$root.App.current_route) {
                        return true;
                    }
                }

                return false;
            }
        },
        computed: {
            iconClass() {
                return this.mutableIsOpen ? 'fa-caret-up' : 'fa-caret-down';
            }
        },
        mounted() {
            if (this.isOpen) {
                this.mutableIsOpen = this.isOpen;
            } else {
                this.mutableIsOpen = this.childrenOpen();
            }
        }
    }
</script>
