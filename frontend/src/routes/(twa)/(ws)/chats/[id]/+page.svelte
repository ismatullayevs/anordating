<script lang="ts">
	import Chat from '$lib/components/Chat.svelte';
	import type { IMessage } from '@/types/Message.js';

	import type { IUser } from '@/types/User';
	import { getContext } from 'svelte';
	import { page } from '$app/state';
	import { getChatMembers, getChatMessages, getUserById } from '@/api';
	import { error } from '@sveltejs/kit';

	const websocket = (getContext('websocket') as () => {value: WebSocket | null})();
	const init_data = (getContext('init_data') as () => {value: string | undefined})();
	const user = (getContext('user') as () => {value: IUser | null})();
	let match: IUser | null = $state(getMatchFromURI());
	let messages: IMessage[] | null = $state(null);

	function getMatchFromURI(): IUser | null {
		const urlParams = new URLSearchParams(window.location.search);
		const matchParam = urlParams.get('match');
		if (matchParam) {
			try {
				return JSON.parse(decodeURIComponent(matchParam));
			} catch (e) {
				console.error('Error parsing match parameter:', e);
			}
		}
		return null;
	}

	if (init_data.value) {
		getChatMembers(Number(page.params.id), init_data.value).then((members) => {
			const match_id = members.find((m) => m.user_id !== user.value?.id)?.user_id;
			if (!match_id) error(404, 'No match found');
			if (!match) {
				getUserById(match_id, init_data.value || '').then((data) => {
					match = data;
				});
			}
			getChatMessages(Number(page.params.id), init_data.value || '').then((data) => {
				messages = data;
			});
		});
	}

	function handleWSMessage(event: MessageEvent) {
		const messageData = JSON.parse(event.data);
		if (messageData.type === 'new_message' && messages) {
			const newMessage: IMessage = messageData.payload;
			if (newMessage.chat_id !== Number(page.params.id)) return;
			if (messages.map((m: IMessage) => m.id).includes(newMessage.id)) return;
			messages.push(newMessage);
		}
	}

	$effect(() => {
		if (!websocket.value) return;
		websocket.value.addEventListener('message', handleWSMessage);
		return () => {
			websocket.value?.removeEventListener('message', handleWSMessage);
		};
	});

	async function onSendMessage(message: string) {
		if (!websocket.value) return;
		websocket.value.send(
			JSON.stringify({
				type: 'new_message',
				payload: {
					chat_id: Number(page.params.id),
					text: message
				}
			})
		);
	}
</script>

<Chat user={user.value} match={match} {messages} {onSendMessage} />
