<script lang="ts">
	import { goto } from '$app/navigation';
	import { createChat, getChatByMatchId, getChatMembers, getUserById } from '@/api.js';
	import Chat from '@/components/Chat.svelte';
	import type { IUser } from '@/types/User';
	import { getContext } from 'svelte';
	import { page } from '$app/state';

	const websocket = (getContext('websocket') as () => {value: WebSocket | null})();
	const init_data = (getContext('init_data') as () => {value: string | undefined})();
	const user = (getContext('user') as () => {value: IUser | null})();
	const match: {value: IUser | null} = $state({ value: null });

	if (init_data.value) {
		getChatByMatchId(page.params.id, init_data.value).then((chat) => {
			if (chat) {
				goto(`/chats/${chat.id}`);
			}
		});
		getUserById(page.params.id, init_data.value).then((data) => {
			match.value = data;
		})
	}


	async function handleWSMessage(event: MessageEvent) {
		const messageData = JSON.parse(event.data);
		if (messageData.type === 'new_chat' && init_data.value && match.value) {
			const members = await getChatMembers(messageData.payload.id, init_data.value);
			if (members.map((m) => m.user_id).includes(match.value.id)) {
				goto(`/chats/${messageData.payload.id}`);
			}
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
		if (!websocket.value || !init_data.value || !match.value) return;
		const chatData = await createChat(match.value.id, init_data.value);
		if (!chatData) return;
		websocket.value.send(
			JSON.stringify({
				type: 'new_message',
				payload: {
					chat_id: chatData.id,
					text: message
				}
			})
		);
		goto(`/chats/${chatData.id}`);
	}
</script>

<Chat user={user.value} match={match.value} messages={[]} {onSendMessage} />
