import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/api";
import { ArticleType, Topic } from "@/utils/types";

const fetchArticle = async (articleId: string) => {
	const response = await apiClient.get(`/articles/${articleId}`);
	return response.data as ArticleType;
};

const fetchTopic = async (topicId: string) => {
	const response = await apiClient.get(`/topics/${topicId}`);
	return response.data as Topic;
};

interface ArticleWithFeeds {
	article: ArticleType;
	sources: Topic["processed_feeds"];
}

export const useFetchArticleDetails = (articleId: string) => {
	return useQuery<ArticleWithFeeds>({
		queryKey: ["article", articleId],
		queryFn: async () => {
			const article = await fetchArticle(articleId);

			let sources: Topic["processed_feeds"] = [];

			if (article.topic_id) {
				try {
					const topic = await fetchTopic(article.topic_id);
					sources = topic.processed_feeds;
				} catch (err) {
					console.error("Error fetching topic:", err);
				}
			}

			return { article, sources };
		},
		enabled: !!articleId,
		staleTime: 60,
		retry: 2,
	});
};
