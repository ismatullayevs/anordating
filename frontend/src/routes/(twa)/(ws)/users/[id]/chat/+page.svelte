<script lang="ts">
	import { goto } from '$app/navigation';
	import { createChat, getChatByMatchId, getUserById } from '@/api.js';
	import Chat from '@/components/Chat.svelte';
	import type { IUser } from '@/types/User';
	import { getContext } from 'svelte';
	import { page } from '$app/state';
	import type { IMessage } from '@/types/Message';
	import { error } from '@sveltejs/kit';

	const websocket = (getContext('websocket') as () => {value: WebSocket | null})();
	const init_data = (getContext('init_data') as () => {value: string | undefined})();
	const user = (getContext('user') as () => {value: IUser | null})();
	let match: IUser | null = $state(null);
	let messages: null | IMessage[] = $state(null);

	if (init_data.value) {
		getChatByMatchId(page.params.id, init_data.value).then((chat) => {
			if (chat) {
				let matchData;
				if (match) {
					matchData = encodeURIComponent(JSON.stringify(match));
				}
				goto(`/chats/${chat.id}?match=${matchData}`);
			} else {
				messages = [];
			}
		})
		getUserById(page.params.id, init_data.value).then((data) => {
			if (!data) {
				error(404, `User with id ${page.params.id} not found`);
			}
			match = data;
		}).catch((reason) => {
			console.log(JSON.stringify(reason));
		})
	}

	async function handleWSMessage(event: MessageEvent) {
		const messageData = JSON.parse(event.data);
		if (messageData.type === 'new_chat' && init_data.value && match) {
			goto(`/chats/${messageData.payload.id}`);
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
		if (!websocket.value || !init_data.value || !match) return;
		const chatData = await createChat(match.id, init_data.value);
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

<Chat user={user.value} {match} {messages} {onSendMessage} />
