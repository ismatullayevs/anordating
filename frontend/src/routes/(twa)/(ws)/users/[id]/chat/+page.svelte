<script lang="ts">
	import { goto } from '$app/navigation';
	import { createChat } from '@/api.js';
	import Chat from '@/components/Chat.svelte';
	import type { PageProps } from './$types';
	import type { IMessage } from '@/types/Message';

	const { data }: PageProps = $props();
	let messages: IMessage[] = $state([]);

	Promise.all([data.chat, data.match]).then(([chat, match]) => {
		if (chat) {
			goto(`/chats/${chat.id}?match=${encodeURIComponent(JSON.stringify(match))}`);
		}
		messages = [];
	})

	async function handleWSMessage(event: MessageEvent) {
		const messageData = JSON.parse(event.data);
		if (messageData.type === 'new_chat') {
			goto(`/chats/${messageData.payload.id}`);
		}
	}

	$effect(() => {
		data.websocket.addEventListener('message', handleWSMessage);
		return () => {
			data.websocket.removeEventListener('message', handleWSMessage);
		};
	});

	async function onSendMessage(message: string) {
		const match = await data.match;
		const chatData = await createChat(match.id, data.init_data);
		data.websocket.send(
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

<Chat user={data.user} match={data.match} messages={messages} {onSendMessage} />
