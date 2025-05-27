<script lang="ts">
    const { data, children } = $props();
</script>

{#await data.user}
    <div class="loading">
        <p>Loading...</p>
    </div>
{:then user}
    {@render children()}
{:catch error}
    <div class="error">
        <p>Error: {error.message}</p>
    </div>
{/await}