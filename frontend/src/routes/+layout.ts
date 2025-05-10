import { getMe } from "@/api";
import { init, initData, initDataRaw } from "@telegram-apps/sdk-svelte";
import "../app.css"

export const ssr = false;

export async function load() {
    init();
    initData.restore();
    const init_data = initDataRaw();
    const user = init_data ? await getMe(init_data): null;
    return {
        init_data,
        user
    }
}