export interface IChatMember {
    id: number,
    chat_id: number,
    user_id: string,
    created_at: Date,
    updated_at: Date,
}

export interface IChat {
    id: number,
    members: IChatMember[],
}