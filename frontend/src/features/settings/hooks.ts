import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/api";
import { LLMSettings } from "@/utils/types";

const fetchLLMSettings = async () => {
	const response = await apiClient.get(`/settings/llm`);
	return response.data;
};

const saveLLMSettings = async (settings: LLMSettings) => {
	const response = await apiClient.post("/settings/llm", settings);
	return response.data;
};

export const useFetchProjectDetails = () => {
	return useQuery<LLMSettings>({
		queryKey: ["settings"],
		queryFn: () => fetchLLMSettings(),
		staleTime: 60,
		retry: 2,
	});
};

export const useSaveLLMSettings = () => {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: saveLLMSettings,

		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: ["settings"] });
		},
	});
};
