export enum Genders {
    MALE = "male",
    FEMALE = "female",
}

export enum UILanguages {
    EN = 'en',
    RU = 'ru',
    UZ = 'uz',
}

export interface IUser {
    id: string,
    telegram_id: number,
    name: string,
    birth_date: Date,
    rating: number,
    is_active: boolean,
    bio: string | null,
    gender: Genders,
    latitude: number,
    longitude: number,
    place_id: string | null,
    is_location_precise: boolean,
    ui_language: UILanguages,
    created_at: Date,
    updated_at: Date,
}