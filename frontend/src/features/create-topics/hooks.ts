import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/api";

export interface CreateTopicPayload {
	name: string;
	description: string;
	feed_urls: string[];
	publish_urls: string[];
	thumbnail_url: string;
}

const createTopic = async (projectId: string, newTopic: CreateTopicPayload) => {
	const response = await apiClient.post(
		`/projects/${projectId}/topics`,
		newTopic
	);
	return response.data;
};

export const useCreateTopic = (projectId: string) => {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: (newTopic: CreateTopicPayload) =>
			createTopic(projectId, newTopic),
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: ["topics", projectId] });
		},
	});
};
