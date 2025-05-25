import { invalidateAll } from "$app/navigation";
import type { LayoutLoad } from "./$types";

export const load: LayoutLoad = async ({ parent }) => {
    const { init_data } = await parent();
    console.log("Connecting to websocket")
    const websocket = new WebSocket(
        `${import.meta.env.VITE_WEBSOCKET_URL}/ws?initData=${encodeURIComponent(init_data)}`
    );

    websocket.onclose = (e) => {
        invalidateAll();
    }

    return {
        websocket
    }
}