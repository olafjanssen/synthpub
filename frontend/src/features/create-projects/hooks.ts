import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/api";

const createProject = async (newProject: {
	title: string;
	description: string;
	topic_ids?: string[];
}) => {
	const response = await apiClient.post("/projects/", newProject);
	return response.data;
};

export const useCreateProject = () => {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: createProject,

		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: ["projects"] });
		},
	});
};
