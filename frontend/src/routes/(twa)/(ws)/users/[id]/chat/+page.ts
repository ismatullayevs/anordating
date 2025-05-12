import { getChatByMatchId, getUserById } from "@/api";
import { error, redirect } from "@sveltejs/kit";
import type { PageLoad } from "./$types";

export const load: PageLoad = async ({ parent, params }) => {
    const data = await parent();
    let chat = null;
    try {
        chat = await getChatByMatchId(params.id, data.init_data);
    } catch { /* empty */ }
    if (chat) {
        redirect(302, `/chats/${chat.id}`);
    }
    try {
        const match = await getUserById(params.id, data.init_data)
        return {
            match: match,
        }
    } catch {
        throw error(404, "Match not found");
    }
}