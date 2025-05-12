import { invalidateAll } from "$app/navigation";
import type { LayoutLoad } from "./$types";

export const load: LayoutLoad = async ({ parent }) => {
    const data = await parent();
    const websocket = new WebSocket(`${import.meta.env.VITE_WEBSOCKET_URL}/ws?initData=${encodeURIComponent(data.init_data)}`)
    websocket.onclose = () => {
        invalidateAll();
    }
    return {
        websocket
    }
}