import { getChatByMatchId, getUserById } from "@/api";
import type { PageLoad } from "./$types";
import { goto } from "$app/navigation";
import { error } from "@sveltejs/kit";

export const load: PageLoad = async ({ fetch, params, parent }) => {
  const { init_data } = await parent();
  const chat = getChatByMatchId(params.id, init_data, fetch)
  const match = getUserById(params.id, init_data, fetch).then((match) => {
        if (!match) {error(404, "Match not found");}
        return match;
  })
  return {
    chat,
    match,
  }
}