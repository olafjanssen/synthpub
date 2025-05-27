export interface Project {
	title: string;
	description: string;
	thumbnail_url: string;
	topic_ids: string[];
	id: string;
	created_at: Date;
	updated_at: Date | null;
}

export interface Topic {
	name: string;
	description: string;
	publish_urls: string;
	thumbnail_url: string;
	id: string;
	processed_feeds: string[];
	created_at: Date;
	updated_at: Date | null;
}

export interface ContentData {
	title: string;
	description: string;
}
