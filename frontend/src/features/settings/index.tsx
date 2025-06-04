import React, { FormEvent, useEffect, useState } from "react";
import { useFetchProjectDetails, useSaveLLMSettings } from "./hooks";
import { LLMSettings } from "@/utils/types";

interface SettingsModalProps {
	onClose: () => void;
}

const SettingsModal: React.FC<SettingsModalProps> = ({ onClose }) => {
	const { data: llm } = useFetchProjectDetails();
	const { mutate } = useSaveLLMSettings();

	const [activeSection, setActiveSection] = useState<"env" | "llm">("env");

	const [databaseLocation, setDatabaseLocation] = useState("");
	const [openaiApiKey, setOpenaiApiKey] = useState("");
	const [youtubeApiKey, setYoutubeApiKey] = useState("");
	const [githubToken, setGithubToken] = useState("");

	const [articleProvider, setArticleProvider] = useState(
		llm?.settings?.article_generation?.provider ?? ""
	);
	const [articleModel, setArticleModel] = useState(
		llm?.settings?.article_generation?.model_name ?? ""
	);
	const [articleMaxTokens, setArticleMaxTokens] = useState(
		llm?.settings?.article_generation?.max_tokens ?? 0
	);

	const [refinementProvider, setRefinementProvider] = useState(
		llm?.settings?.article_refinement?.provider ?? ""
	);
	const [refinementModel, setRefinementModel] = useState(
		llm?.settings?.article_refinement?.model_name ?? ""
	);
	const [refinementMaxTokens, setRefinementMaxTokens] = useState(
		llm?.settings?.article_refinement?.max_tokens ?? 0
	);

	useEffect(() => {
		setArticleProvider(llm?.settings?.article_generation?.provider ?? "");
		setArticleModel(llm?.settings?.article_generation?.model_name ?? "");
		setArticleMaxTokens(llm?.settings?.article_generation?.max_tokens ?? 0);

		setRefinementProvider(llm?.settings?.article_refinement?.provider ?? "");
		setRefinementModel(llm?.settings?.article_refinement?.model_name ?? "");
		setRefinementMaxTokens(llm?.settings?.article_refinement?.max_tokens ?? 0);
	}, [llm]);

	const handleSaveEnvVariables = () => {
		// TODO: Implement saving environment variables
		alert("Environment variables saved!");
	};

	const handleSaveLLMSettings = (e: FormEvent) => {
		// TODO: Implement saving LLM settings
		e.preventDefault();

		const newLLMSettings: LLMSettings = {
			settings: {
				article_generation: {
					provider: articleProvider,
					model_name: articleModel,
					max_tokens: articleMaxTokens,
				},
				article_refinement: {
					provider: refinementProvider,
					model_name: refinementModel,
					max_tokens: refinementMaxTokens,
				},
			},
		};

		console.log(newLLMSettings);

		mutate(newLLMSettings, {
			onSuccess: () => {
				onClose();
			},

			// eslint-disable-next-line @typescript-eslint/no-explicit-any
			onError: (e: any) => {
				alert(e);
			},
		});
	};

	return (
		<div
			onClick={onClose}
			className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
		>
			<div
				onClick={(e) => e.stopPropagation()}
				className="relative w-full max-w-2xl p-6 rounded-md shadow-2xl bg-[#4A6A5F] text-white min-h-[600px] overflow-y-auto"
			>
				<button
					onClick={onClose}
					className="absolute top-3 right-3 text-2xl font-bold"
				>
					&times;
				</button>

				<h2 className="text-3xl font-semibold mb-4">Settings</h2>

				<div className="flex mb-4 border-b border-[#b3d9bb]">
					<button
						className={`mr-6 pb-2 ${
							activeSection === "env"
								? "font-bold border-b-4 border-[rgb(240,109,108)]"
								: "opacity-80 hover:opacity-100"
						}`}
						onClick={() => setActiveSection("env")}
					>
						Environment
					</button>
					<button
						className={`pb-2 ${
							activeSection === "llm"
								? "font-bold border-b-4 border-[rgb(240,109,108)]"
								: "opacity-80 hover:opacity-100"
						}`}
						onClick={() => setActiveSection("llm")}
					>
						LLM
					</button>
				</div>

				{activeSection === "env" && (
					<div className="h-[200px] w-[600px]">
						<div className="mb-6 mt-6">
							<label
								className="block mb-1 font-medium"
								htmlFor="databaseLocation"
							>
								Database Location
							</label>
							<div className="flex">
								<input
									id="databaseLocation"
									type="text"
									value={databaseLocation}
									onChange={(e) => setDatabaseLocation(e.target.value)}
									placeholder="Path to database"
									className="flex-1 p-2 rounded-l-md border border-[#b3d9bb] text-black focus:outline-none"
								/>
								<button className="bg-[#AEB71D] text-black px-4 rounded-r-md hover:bg-[#a3ab35] transition-colors">
									Choose
								</button>
							</div>
						</div>

						<h3 className="text-2xl font-semibold mb-2">
							Environment Variables
						</h3>
						<div className="grid grid-cols-1 gap-4 mb-4">
							<div>
								<label
									className="block mb-1 font-medium"
									htmlFor="openaiApiKey"
								>
									Enter Open API Key (If Any)
								</label>
								<input
									id="openaiApiKey"
									type="text"
									value={openaiApiKey}
									onChange={(e) => setOpenaiApiKey(e.target.value)}
									placeholder="OpenAI API Key"
									className="w-full p-2 rounded-md border border-[#b3d9bb] text-black focus:outline-none"
								/>
							</div>
							<div>
								<label
									className="block mb-1 font-medium"
									htmlFor="youtubeApiKey"
								>
									Enter Youtube API Key (If Any)
								</label>
								<input
									id="youtubeApiKey"
									type="text"
									value={youtubeApiKey}
									onChange={(e) => setYoutubeApiKey(e.target.value)}
									placeholder="YouTube API Key"
									className="w-full p-2 rounded-md border border-[#b3d9bb] text-black focus:outline-none"
								/>
							</div>
							<div>
								<label className="block mb-1 font-medium" htmlFor="githubToken">
									Enter Github Token
								</label>
								<input
									id="githubToken"
									type="text"
									value={githubToken}
									onChange={(e) => setGithubToken(e.target.value)}
									placeholder="GitHub Token"
									className="w-full p-2 rounded-md border border-[#b3d9bb] text-black focus:outline-none"
								/>
							</div>
						</div>
						<button
							onClick={handleSaveEnvVariables}
							className="bg-[#AEB71D] text-black px-4 py-2 rounded-md hover:bg-[#a3ab35] transition-colors mb-6"
						>
							Save Environment Variables
						</button>
					</div>
				)}

				{activeSection === "llm" && (
					<div className="h-[200px] w-[600px]">
						<h3 className="text-2xl font-semibold mb-6">ARTICLE GENERATION </h3>

						{/* ARTICLE GENERATION */}
						<div className="mb-4">
							<label
								className="block mb-1 font-medium"
								htmlFor="articleProvider"
							>
								Provider
							</label>
							<select
								id="articleProvider"
								value={articleProvider}
								onChange={(e) => setArticleProvider(e.target.value)}
								className="w-full p-2 rounded-md border border-[#b3d9bb] text-black focus:outline-none"
							>
								<option value="OpenAI">OpenAI</option>
								<option value="Ollama">Ollama</option>
								<option value="Mistral">Mistral</option>
							</select>
						</div>

						<div className="grid grid-cols-2 gap-4 mb-6">
							<div>
								<label
									className="block mb-1 font-medium"
									htmlFor="articleModel"
								>
									Model Name
								</label>
								<input
									id="articleModel"
									type="text"
									value={articleModel}
									onChange={(e) => setArticleModel(e.target.value)}
									placeholder="e.g. gpt-4"
									className="w-full p-2 rounded-md border border-[#b3d9bb] text-black focus:outline-none"
								/>
							</div>
							<div>
								<label
									className="block mb-1 font-medium"
									htmlFor="articleMaxTokens"
								>
									Max Tokens
								</label>
								<input
									id="articleMaxTokens"
									type="number"
									value={articleMaxTokens}
									onChange={(e) =>
										setArticleMaxTokens(parseInt(e.target.value, 10))
									}
									className="w-full p-2 rounded-md border border-[#b3d9bb] text-black focus:outline-none"
								/>
							</div>
						</div>

						{/* ARTICLE REFINEMENT */}
						<div className="mb-4">
							<label
								className="block mb-1 font-medium"
								htmlFor="refinementProvider"
							>
								ARTICLE REFINEMENT Provider
							</label>
							<select
								id="refinementProvider"
								value={refinementProvider}
								onChange={(e) => setRefinementProvider(e.target.value)}
								className="w-full p-2 rounded-md border border-[#b3d9bb] text-black focus:outline-none"
							>
								<option value="OpenAI">OpenAI</option>
								<option value="Ollama">Ollama</option>
								<option value="Mistral">Mistral</option>
							</select>
						</div>

						<div className="grid grid-cols-2 gap-4 mb-6">
							<div>
								<label
									className="block mb-1 font-medium"
									htmlFor="refinementModel"
								>
									Model Name
								</label>
								<input
									id="refinementModel"
									type="text"
									value={refinementModel}
									onChange={(e) => setRefinementModel(e.target.value)}
									placeholder="e.g. gpt-4"
									className="w-full p-2 rounded-md border border-[#b3d9bb] text-black focus:outline-none"
								/>
							</div>
							<div>
								<label
									className="block mb-1 font-medium"
									htmlFor="refinementMaxTokens"
								>
									Max Tokens
								</label>
								<input
									id="refinementMaxTokens"
									type="number"
									value={refinementMaxTokens}
									onChange={(e) =>
										setRefinementMaxTokens(parseInt(e.target.value, 10))
									}
									className="w-full p-2 rounded-md border border-[#b3d9bb] text-black focus:outline-none"
								/>
							</div>
						</div>

						<button
							onClick={handleSaveLLMSettings}
							className="bg-[#AEB71D] text-black px-4 py-2 rounded-md hover:bg-[#a3ab35] transition-colors"
						>
							Save LLM Settings
						</button>
					</div>
				)}
			</div>
		</div>
	);
};

export default SettingsModal;
