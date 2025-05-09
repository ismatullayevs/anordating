<script lang="ts">
	import { init, initData, initDataRaw } from '@telegram-apps/sdk-svelte';
	import type { IUser } from '@/types/User';
	import '../app.css';
	import { getChatByMatchId, getMe } from '@/api';
	import { setContext } from 'svelte';
	import { redirect } from '@sveltejs/kit';
	import type { IChat } from '@/types/Chat';
	import { page } from '$app/state';
	import { goto } from '$app/navigation';

	const { children } = $props();
	let init_data: {value: string | undefined | null} = $state({value: null});
	let user: {value: IUser | null} = $state({value: null});
	let websocket: {value: WebSocket | null} = {value: null};
	
	setContext('user', () => user);
	setContext('init_data', () => init_data);
	setContext('websocket', () => websocket);

	$effect(() => {
		init();
		initData.restore();
		init_data.value = initDataRaw();

		if (init_data.value) {
			getMe(init_data.value).then((data) => {
				user.value = data;
			});
			websocket.value = new WebSocket(`${import.meta.env.VITE_WEBSOCKET_URL}/ws?initData=${encodeURIComponent(init_data.value)}`);
			websocket.value.addEventListener('message', (event) => {
				const data = JSON.parse(event.data);
				if (data.type === 'new_chat') {
					const chat: IChat = data.payload;
					if (page.route.id === '/users/[id]/chat') {
						goto(`/chats/${chat.id}`);
					}
				}
			})
			websocket.value.onclose = () => {
				websocket.value = null;
			}
		}
	});
</script>
{#if !user.value}
	<p>Please, create an account in <a href="https://t.me/anordatingbot">@anordatingbot</a></p>
{:else}
	{@render children()}
{/if}
