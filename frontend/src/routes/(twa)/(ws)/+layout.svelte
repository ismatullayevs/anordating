<script lang="ts">
	import { setContext, getContext } from 'svelte';

	const { children } = $props();

	const init_data = (getContext('init_data') as () => { value: string | undefined })();
	let websocket: { value: WebSocket | null } = $state({ value: null });

	setContext('websocket', () => websocket);

	$effect(() => {
		if (init_data.value) {
			websocket.value = new WebSocket(
				`${import.meta.env.VITE_WEBSOCKET_URL}/ws?initData=${encodeURIComponent(init_data.value)}`
			);
		}
	});
</script>

{@render children()}
