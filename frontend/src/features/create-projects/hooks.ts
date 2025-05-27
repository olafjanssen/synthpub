import {
	//useQuery,
	useMutation,
	useQueryClient,
} from "@tanstack/react-query";
import { apiClient } from "@/api";
//import { CreateProject } from ".";

// const fetchProjects = async () => {
// 	const response = await apiClient.get("/projects/");
// 	return response.data;
// };

const createProject = async (newProject: {
	title: string;
	description: string;
	// eslint-disable-next-line @typescript-eslint/no-explicit-any
	topic_ids?: any[];
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
