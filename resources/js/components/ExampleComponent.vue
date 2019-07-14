<template>
    <div class="card card-default">
        <div class="card-header">Example Component</div>

        <div class="card-body">
            I'm an example component.
            <br><br>
            The count is: {{ count }}
            <br>
            <div class="btn-group">
                <button @click="count++" class="btn btn-success">Inc.</button>
                <button @click="count--" class="btn btn-danger">Dec.</button>
            </div>
        </div>
    </div>
</template>

<script>
    export default {
        data() {
            return {
                count: 0,
            };
        },
        mounted() {
            console.log('Component mounted.')
        }
    }
</script>
