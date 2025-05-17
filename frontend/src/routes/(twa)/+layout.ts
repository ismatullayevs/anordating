import { getMe } from "@/api";
import { init, initData, initDataRaw } from "@telegram-apps/sdk-svelte";
import "../../app.css";
import type { LayoutLoad } from "./$types";
import { error } from "@sveltejs/kit";

export const ssr = false;

export const load: LayoutLoad = async () => {
  init();
  initData.restore();
  const init_data = initDataRaw();
  if (!init_data) {
    error(500, "Open the app in telegram");
  }
  console.log("Fetching user")
  const user = await getMe(init_data);
  return {
    init_data,
    user
  }
}
