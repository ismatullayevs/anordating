import "../../app.css"
import type { LayoutLoad } from "./$types";
import { init, initData, initDataRaw } from '@telegram-apps/sdk-svelte';
import { getMe } from '@/api';
import { error } from "@sveltejs/kit";

export const ssr = false;

export const load: LayoutLoad = async ({ fetch }) => {
    init();
    initData.restore();
    const init_data = initDataRaw();
    if (!init_data) error(400, 'Failed to load init data');
    console.log("Fetching user")

    return {
        init_data,
        user: getMe(init_data, fetch)
    }
}