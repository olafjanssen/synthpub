import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/api";
import { ArticleType } from "@/utils/types";

const fetchArticle = async (articleId: string) => {
	const response = await apiClient.get(`/articles/${articleId}`);
	return response.data as ArticleType;
};

export const useFetchArticleDetails = (articleId: string) => {
	return useQuery<ArticleType>({
		queryKey: ["article", articleId],
		queryFn: () => fetchArticle(articleId),
		enabled: !!articleId,
		staleTime: 60,
		retry: 2,
	});
};
