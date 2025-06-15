export interface Project {
	title: string;
	description: string;
	thumbnail_url: string;
	topic_ids: string[];
	id: string;
	created_at: Date;
	updated_at: Date | null;
}

export interface ProcessedFeed {
	url: string;
	accessed_at: string; // ISO timestamp
	content_hash: string;
	is_relevant: boolean;
	relevance_explanation: string;
	needs_further_processing: boolean;
	new_information: string;
	enforcing_information: string;
	contradicting_information: string;
	article_id: string;
}

export interface Topic {
	name: string;
	description: string;
	feed_urls: string[];
	publish_urls: string[];
	thumbnail_url: string;
	slug: string | null;
	prompt_id: string | null;
	id: string;
	article: string | null;
	processed_feeds: ProcessedFeed[];
	created_at: Date;
	updated_at: Date | null;
}

export interface ContentData {
	title: string;
	description: string;
}

export interface LLMSettings {
	settings: Settings;
}

interface Settings {
	article_generation: ArticleGeneration;
	article_refinement: ArticleRefinement;
}

interface ArticleGeneration {
	provider: string;
	model_name: string;
	max_tokens: number;
}

interface ArticleRefinement {
	provider: string;
	model_name: string;
	max_tokens: number;
}

export interface ArticleType {
	id: string;
	title: string | null;
	topic_id: string | null;
	content: string | null;
	version: number | null;
	created_at: string | null;
	updated_at: string | null;
	previous_version: string | null;
	next_version: string | null;
	source_feed: {
		url: string | null;
		accessed_at: string | null;
	};
	// eslint-disable-next-line @typescript-eslint/no-explicit-any
	representations: any[];
}
