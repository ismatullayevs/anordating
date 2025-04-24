<script>
	import Date from "@/components/Date.svelte";
	import Message from "@/components/Message.svelte";
	import SendMessage from "@/components/SendMessage.svelte";
    let { data } = $props();
    const userId = "23l2kj2jjd8s"

</script>
<div class="border-b-slate-200 fixed border-b-1 py-2 w-full">
    <div class="px-3 max-w-3xl mx-auto">
        <p class="text-xl font-semibold">Anora</p>
    </div>
</div>

<div class="p-3 pt-14 flex flex-col items-start max-w-3xl mx-auto">
    <Date text='April 17' />
    {#each data.messages as message}
        <Message message={message} userId={userId} />
    {/each}
</div>

<SendMessage />