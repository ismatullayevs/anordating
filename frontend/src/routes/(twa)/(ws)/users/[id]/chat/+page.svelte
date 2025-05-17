<script lang="ts">
	import { goto } from "$app/navigation";
	import { createChat, getChatMembers } from "@/api.js";
	import Chat from "@/components/Chat.svelte";
	let { data } = $props();

  if (data.chat) {
    goto(`/chats/${data.chat.id}`);
  }

	async function handleWSMessage(event: MessageEvent) {
		const messageData = JSON.parse(event.data);
		if (messageData.type === 'new_chat') {
			const members = await getChatMembers(messageData.payload.id, data.init_data);
			if (members.map(m => m.user_id).includes(data.match.id)) {
				goto(`/chats/${messageData.payload.id}`);
			}
		}
	}

	$effect(() => {
		data.websocket.addEventListener("message", handleWSMessage);
		return () => {
			data.websocket.removeEventListener("message", handleWSMessage);
		}
	})

	async function onSendMessage(message: string) {
        const chatData = await createChat(data.match.id, data.init_data);
		if (!chatData) return;
		data.websocket.send(JSON.stringify({
			type: 'new_message',
			payload: {
				chat_id: chatData.id,
				text: message
			}
		}));
		goto(`/chats/${chatData.id}`);
	}
</script>

<Chat user={data.user} match={data.match} messages={[]} {onSendMessage} />
