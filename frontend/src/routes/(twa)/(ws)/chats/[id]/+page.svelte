<script lang="ts">
	import { page } from '$app/state';
	import Chat from '$lib/components/Chat.svelte';
	import type { IMessage } from '@/types/Message.js';
	const { data } = $props();
	let messages = $state(data.messages);

	function handleWSMessage(event: MessageEvent) {
		const messageData = JSON.parse(event.data);
		if (messageData.type === 'new_message') {
			const newMessage: IMessage = messageData.payload;
			if (newMessage.chat_id !== Number(page.params.id)) return;
			if (messages.map((m: IMessage) => m.id).includes(newMessage.id)) return;
			messages.push(newMessage);
		}
	}

	$effect(() => {
		data.websocket.addEventListener('message', handleWSMessage);
		return () => {
			data.websocket.removeEventListener('message', handleWSMessage);
		};
	});

	async function onSendMessage(message: string) {
		data.websocket.send(
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

<Chat user={data.user} match={data.match} {messages} {onSendMessage} />
