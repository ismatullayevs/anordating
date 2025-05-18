<script lang="ts">
    import { setContext } from 'svelte';
    import "../../app.css";
    import { init, initData, initDataRaw } from '@telegram-apps/sdk-svelte';
	import { getMe } from '@/api';
	import type { IUser } from '@/types/User';

    const { children } = $props();

    init();
    initData.restore();
    let init_data = $state({value: initDataRaw()});
    let user: { value: IUser | null} = $state({ value: null});

    $effect(() => {
        if (init_data.value) getMe(init_data.value).then(data => user.value = data);
    })

    setContext('init_data', () => init_data);
    setContext('user', () => user);
</script>


{@render children()}