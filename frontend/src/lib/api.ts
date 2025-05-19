import type { IChat, IChatMember } from "./types/Chat";
import type { IMessage } from "./types/Message";
import type { IUser } from "./types/User";

export const getMe = async (init_data: string): Promise<IUser> => {
    const getter = async () => {
        const res = await fetch(`${import.meta.env.VITE_API_URL}/users/me`, {
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `twa ${init_data}`,
            },
        });
        if (!res.ok) {
            throw new Error(`Error: ${res.status} ${res.statusText}`);
        }
        const data = await res.json();
        return data;
        }
    return await new Promise<IUser>((resolve, reject) => {
        setTimeout(() => {
            getter().then(resolve).catch(reject);
        }
        , 1000000);
    });
}

export const getChatByMatchId = async (match_id: string, init_data: string): Promise<IChat> => {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/users/${match_id}/chat`, {
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `twa ${init_data}`,
        },
    });
    if (!res.ok) {
        throw new Error(`Error: ${res.status} ${res.statusText}`);
    }
    const data = await res.json();
    return data;
}

export const getChat = async (id: number, init_data: string): Promise<IChat> => {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/chats/${id}`, {
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `twa ${init_data}`,
        },
    });
    if (!res.ok) {
        throw new Error(`Error: ${res.status} ${res.statusText}`);
    }
    const data = await res.json();
    return data;
}


export const getChatMessages = async (id: number, init_data: string): Promise<IMessage[]> => {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/chats/${id}/messages`, {
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `twa ${init_data}`,
        },
    });
    if (!res.ok) {
        throw new Error(`Error: ${res.status} ${res.statusText}`);
    }
    const data = await res.json();
    return data;
}


export const getChatMembers = async (id: number, init_data: string): Promise<IChatMember[]> => {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/chats/${id}/members`, {
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `twa ${init_data}`,
        },
    });
    if (!res.ok) {
        throw new Error(`Error: ${res.status} ${res.statusText}`);
    }
    const data = await res.json();
    return data;
}

export const createChat = async (match_id: string, init_data: string): Promise<IChat> => {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/chats`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `twa ${init_data}`,
        },
        body: JSON.stringify({
            match_id: match_id,
        }),
    });
    if (!res.ok) {
        throw new Error(`Error: ${res.status} ${res.statusText}`);
    }
    const data = await res.json();
    return data;
}

export const getUserById = async (id: string, init_data: string): Promise<IUser> => {
    const getter = async () => {
        const res = await fetch(`${import.meta.env.VITE_API_URL}/users/${id}`, {
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `twa ${init_data}`,
            },
        });
        if (!res.ok) {
            throw new Error(`Error: ${res.status} ${res.statusText}`);
        }
        const data = await res.json();
        return data;
    }
    return await new Promise<IUser>((resolve, reject) => {
        setTimeout(() => {
            getter().then(resolve).catch(reject);
        }
        , 1000000);
    });
}