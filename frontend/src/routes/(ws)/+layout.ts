import { error, type LoadEvent } from "@sveltejs/kit";

export async function load({ parent }: LoadEvent) {
    const data = await parent();
    if (!(data && data.init_data)) {
        error(500, "No init data");
    }
    const websocket = new WebSocket(`${import.meta.env.VITE_WEBSOCKET_URL}/ws?initData=${encodeURIComponent(data.init_data)}`)
    return {
        websocket
    }
}