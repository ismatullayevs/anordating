import { getChatMembers, getUserById, getChatMessages } from "@/api";
import { error } from "@sveltejs/kit";
import type { PageLoad } from "./$types";

export const load: PageLoad = async ({ parent, params }) => {
    const data = await parent();
    const members = await getChatMembers(Number(params.id), data.init_data);
    const match_id = members.find((m) => m.user_id !== data.user.id)?.user_id;
    if (!match_id) error(404, "No match found");
    const match = await getUserById(match_id, data.init_data);
    const messages = await getChatMessages(Number(params.id), data.init_data)
    return {
        match,
        messages
    }
}