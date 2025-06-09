import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/api";
import { Project, Topic } from "@/utils/types";

const fetchProjects = async (id: string) => {
	const response = await apiClient.get(`/projects/${id}`);
	return response.data;
};

export const useFetchProjectDetails = (id: string) => {
	return useQuery<Project>({
		queryKey: ["project", id],
		queryFn: () => fetchProjects(id),
		staleTime: 60,
		retry: 2,
	});
};

//TODO: Fetch topics by project id

const fetchTopics = async () => {
	const response = await apiClient.get(`/topics/`);
	return response.data;
};

export const useFetchTopics = () => {
	return useQuery<Topic[]>({
		queryKey: ["topics"],
		queryFn: fetchTopics,
		staleTime: 60,
		retry: 2,
	});
};
