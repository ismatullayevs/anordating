<script lang="ts">  
    import DateBadge from "@/components/DateBadge.svelte";
	import Message from "@/components/Message.svelte";
    import type { IMessage } from "@/types/Message";

    import { createChat, getChatByMatchId, getChatMembers, getChatMessages, getUserById } from '@/api';
	import { page } from '$app/state';
	import { getContext, untrack } from 'svelte';
	import type { IUser } from '@/types/User';
	import { goto } from "$app/navigation";

	let init_data = (getContext('init_data') as () => { value: string | undefined | null })();
    let match: IUser | null = $state(null)
	let user = (getContext("user") as () => {value: IUser | null})();
	let websocket = (getContext("websocket") as () => {value: WebSocket | null})();
    let messages: IMessage[] = $state([])
    let newMessage = $state({value: ''});

	$effect(() => {
        if (init_data.value) {
            if ( page.route.id === "/(ws)/users/[id]/chat") {
                getChatByMatchId(page.params.id, init_data.value)
                    .then((data) => {
                        if (data) goto(`/chats/${data.id}`);
                    })
                    .catch((err) => {
                        console.error(err);
                    });
                getUserById(page.params.id, init_data.value)
                    .then((data) => {
                        untrack(() => match = data);
                    })
            } else {
                getChatMembers(Number(page.params.id), init_data.value)
                    .then((data) => {
                        for (const member of data) {
                            if (member.user_id !== user.value?.id && init_data.value) {
                                getUserById(member.user_id, init_data.value)
                                    .then((data) => {
                                        untrack(() => match = data);
                                    })
                                    .catch((err) => {
                                        console.error(err);
                                    });
                            }
                        }
                    })
                    .catch((err) => {
                        console.error(err);
                    });
                }}
            }
	);

    $effect(() => {
        if (init_data.value && page.route.id === "/(ws)/chats/[id]") {
            getChatMessages(Number(page.params.id), init_data.value)
                .then((data) => {
                    untrack(() => messages = data);
                })
                .catch((err) => {
                    console.error(err);
                });
        }
    })
    
	function handleWSMessage(event: MessageEvent) {
		const data = JSON.parse(event.data);
		if (data.type === 'new_message') {
			const newMessage: IMessage = data.payload;
            messages.push(newMessage);
		}
	}

	$effect(() => {
		if (websocket.value && websocket.value.readyState === WebSocket.OPEN) {
			websocket.value.addEventListener('message', handleWSMessage);
		}
		return () => {
			if (websocket.value) {
				websocket.value.removeEventListener('message', handleWSMessage);
			}
		};
	})

    let autoscroll = false;
    $effect.pre(() => {
        JSON.stringify(messages)
        const body = document.body;
        const scrollHeight = Math.max(
            body.scrollHeight,
            document.documentElement.scrollHeight,
            body.offsetHeight,
            document.documentElement.offsetHeight,
            body.clientHeight,
            document.documentElement.clientHeight
        );

        const scrollTop = window.pageYOffset || (document.documentElement || document.body.parentNode || document.body).scrollTop;
        const clientHeight = window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight;

        autoscroll = scrollHeight - scrollTop - clientHeight <= 100;
    })

    $effect(() => {
        JSON.stringify(messages)
        if (autoscroll) {
            setTimeout(() => {
                window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'});
            }, 100);
        }
    })

    function isNewDay(current: IMessage, previous: IMessage) {
        if (!previous) return true;

        const currentDate = new Date(current.created_at);
        const previousDate = new Date(previous.created_at);

        return (
            currentDate.getFullYear() !== previousDate.getFullYear() ||
            currentDate.getMonth() !== previousDate.getMonth() ||
            currentDate.getDate() !== previousDate.getDate()
        );
  }

  function handleSubmit(e: SubmitEvent) {
    e.preventDefault();
    if (newMessage.value.trim() === '') return;
    if (!init_data.value || !match || !websocket.value) return;
    if (page.route.id === "/(ws)/users/[id]/chat") {
        createChat(match.id, init_data.value).then((data) => {
            if (!data) return;
            websocket.value?.send(JSON.stringify({
                type: 'new_message',
                payload: {
                    chat_id: data.id,
                    text: newMessage.value
                }
            }));
            newMessage.value = '';
            goto(`/chats/${data.id}`);
        }).catch((err) => {
            console.error(err);
        })
    } else {
        websocket.value.send(JSON.stringify({
            type: 'new_message',
            payload: {
                chat_id: Number(page.params.id),
                text: newMessage.value
            }
        }));
        newMessage.value = '';
    }
  }
</script>

{#if match && user.value}
    <div class="border-b-slate-200 bg-white fixed border-b-1 py-2 w-full">
        <div class="px-3 max-w-3xl mx-auto">
            <p class="text-lg font-semibold">{ match.name }</p>
        </div>
    </div>

    <div class="p-3 pt-12 pb-16 flex flex-col items-start max-w-3xl mx-auto">
        {#each messages as message, i}
            {#if isNewDay(message, messages[i - 1])}
                <DateBadge date={new Date(message.created_at)} />
            {/if}
            <Message message={message} userId={user.value.id} />
        {/each}
    </div>
    
    <form onsubmit={handleSubmit} class="bg-white fixed bottom-0 left-0 right-0 px-3 py-1 max-w-3xl mx-auto flex justify-between items-center gap-2 border-1 border-slate-200">
        <input bind:value={newMessage.value} type="text" placeholder="Type your message..." class="w-full border-none outline-none ring-0">
        <button type="submit" aria-label="Send" class="">
            <i class="fa-regular fa-paper-plane text-gray-500 text-xl translate-y-1"></i>
        </button>
    </form>
{/if}