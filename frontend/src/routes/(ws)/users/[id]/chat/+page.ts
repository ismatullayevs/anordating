import { getChatByMatchId, getUserById } from "@/api";
import { error, redirect, type LoadEvent } from "@sveltejs/kit";

export async function load({ parent, params }: LoadEvent) {
    const data = await parent();
    if (!(data && data.init_data && params.id && data.websocket)) {
        error(500, "Error");
    }
    const chat = await getChatByMatchId(params.id, data.init_data);
    if (chat) {
        redirect(302, `/chats/${chat.id}`);
    }
    const match = await getUserById(params.id, data.init_data)
    if (!match) {
        throw error(404, "User not found");
    }

    return {
        match,
    }
}