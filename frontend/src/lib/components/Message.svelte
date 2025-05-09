<script lang="ts">
	import type { IMessage } from '@/types/Message';
	import { format, formatRelative, parseISO } from 'date-fns';

	let { message, userId }: { message: IMessage; userId: string } = $props();
	const isAuthor = message.user_id === userId;
	function formatTimeToHHMM(date: Date) {
		const hours = date.getHours().toString().padStart(2, '0');
		const minutes = date.getMinutes().toString().padStart(2, '0');
		return `${hours}:${minutes}`;
	}
</script>

<div
	class={[
		'mt-3 rounded-2xl py-2 px-3 max-w-10/12 flex',
		isAuthor ? 'self-end bg-rose-500 text-white rounded-br-md' : 'bg-slate-200 rounded-bl-md'
	]}
>
	<p>{message.text}</p>
	<span class={[
        'text-xs inline-block ml-2 self-end',
        isAuthor ? 'text-rose-200' : 'text-slate-500'
    ]}>{formatTimeToHHMM(new Date(message.created_at))}</span>
</div>
