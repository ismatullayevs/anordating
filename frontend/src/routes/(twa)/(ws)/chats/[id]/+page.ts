import { getChatMembers, getChatMessages, getUserById } from '@/api';
import type { PageLoad } from './$types';
import type { IUser } from '@/types/User';
import { error } from '@sveltejs/kit';

function getMatchFromURI(url: URL): IUser | null {
	const matchParam = url.searchParams.get('match')
	if (matchParam) {
		try {
			return JSON.parse(decodeURIComponent(matchParam));
		} catch (e) {
			return null;
		}
	}
	return null;
}

export const load: PageLoad = async ({ fetch, params, parent, url }) => {
	const { init_data, user } = await parent();
	let userData = await user;
	const match = (async () => {
        const match = getMatchFromURI(url);
        if (match) {
            return match;
        }
		return getChatMembers(Number(params.id), init_data).then(async (members) => {
			const match_id = members.find((m) => m.user_id !== userData.id)?.user_id;
			if (!match_id) error(404, 'No match found');
			return await getUserById(match_id, init_data, fetch).then((user) => {
				if (!user) error(404, 'No match found');
				return user;
			});
		});
	})();

	return {
        match,
        messages: getChatMessages(Number(params.id), init_data, fetch)
    };
};
