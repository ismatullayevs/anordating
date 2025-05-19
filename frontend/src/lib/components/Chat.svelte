<script lang="ts">  
    import DateBadge from "@/components/DateBadge.svelte";
    import Message from "@/components/Message.svelte";
    import type { IMessage } from "@/types/Message";
	import type { IUser } from "@/types/User";

    interface IProps {
        user: IUser | null;
        match: IUser | null;
        messages: IMessage[];
        onSendMessage: (message: string) => void;
    }
    
    const { user, match, messages, onSendMessage }: IProps = $props();
    
    let newMessage = $state('');
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

    function onSubmit(e: SubmitEvent) {
        e.preventDefault();
        if (newMessage.trim() === '') return;
        if (!match || !user) return;
        onSendMessage(newMessage);
        newMessage = '';
    }

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

</script>

<div class="border-b-slate-200 bg-white fixed border-b-1 py-2 w-full">
    <div class="px-3 max-w-3xl mx-auto">
        {#if match}
            <p class="text-lg font-semibold">{ match.name }</p>
        {:else}
            <div class="w-24 h-8 bg-gray-300 rounded-lg shimmer"></div>
        {/if}
    </div>
</div>

<div class="p-3 pt-12 pb-16 flex flex-col items-start max-w-3xl mx-auto">
{#if !user || !messages}
    <div class="w-full max-w-2/3 h-10 mt-3 bg-gray-300 rounded-lg shimmer"></div>
    <div class="w-full max-w-2/3 h-10 mt-3 self-end bg-gray-300 rounded-lg shimmer"></div>
    <div class="w-full max-w-2/3 h-10 mt-3 bg-gray-300 rounded-lg shimmer"></div>
{:else}
    {#each messages as message, i}
        {#if isNewDay(message, messages[i - 1])}
            <DateBadge date={new Date(message.created_at)} />
        {/if}
        <Message message={message} userId={user.id} />
    {/each}
{/if}
</div>

<form onsubmit={onSubmit} class="bg-white fixed bottom-0 left-0 right-0 px-3 py-1 max-w-3xl mx-auto flex justify-between items-center gap-2 border-1 border-slate-200">
    <input bind:value={newMessage} type="text" placeholder="Type your message..." class="w-full border-none outline-none ring-0">
    <button type="submit" aria-label="Send" class="">
        <i class="fa-regular fa-paper-plane text-gray-500 text-xl translate-y-1"></i>
    </button>
</form>