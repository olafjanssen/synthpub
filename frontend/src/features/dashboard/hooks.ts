import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/api";
import { Project } from "./";

const fetchProjects = async () => {
	const response = await apiClient.get("/projects/");
	return response.data;
};

export const useFetchProjects = () => {
	return useQuery<Project[]>({
		queryKey: ["projects"],
		queryFn: fetchProjects,
		staleTime: 60,
		retry: 2,
	});
};
