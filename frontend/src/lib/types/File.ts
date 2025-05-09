export enum FileTypes {
    IMAGE = "image",
    VIDEO = "video",
    AUDIO = "audio",
    DOCUMENT = "document",
    OTHER = "other"
}

export interface IFile {
    id: number,
    telegram_id: string | null,
    telegram_unique_id: string | null
    path: string | null,
    file_type: FileTypes,
    file_size: number | null,
    mime_type: string | null,
    duration: number | null,
    uploaded_at: Date,
    thumbnail?: IFile
}