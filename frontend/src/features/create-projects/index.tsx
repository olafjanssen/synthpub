import { useState, FormEvent } from "react";
import Modal from "@/components/Modal";
import Button from "@/components/Button";
import { useCreateProject } from "./hooks";

interface CreateProjectModalProps {
	isOpen: boolean;
	onClose: () => void;
}

/** Local payload shape (can also import from hooks.ts if you prefer) */
export interface CreateProject {
	title: string;
	description: string;
	topic_ids?: string[];
}

const CreateProject: React.FC<CreateProjectModalProps> = ({
	isOpen,
	onClose,
}) => {
	const [title, setTitle] = useState("");
	const [description, setDescription] = useState("");

	const { mutate, error } = useCreateProject();

	const handleSubmit = (e: FormEvent) => {
		e.preventDefault();

		const newProject: CreateProject = {
			title,
			description,
			topic_ids: [],
		};

		mutate(newProject, {
			onSuccess: () => {
				setTitle("");
				setDescription("");

				onClose();
			},
		});
	};

	if (!isOpen) return null;

	return (
		<Modal onClose={onClose} title="Create Project">
			<form onSubmit={handleSubmit} className="p-4">
				<div className="mb-4">
					<label className="block text-white">Project Title</label>
					<input
						type="text"
						value={title}
						onChange={(e) => setTitle(e.target.value)}
						required
						className="mt-1 w-full text-black border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring focus:border-blue-300"
					/>
				</div>

				<div className="mb-4">
					<label className="block text-white">Description</label>
					<textarea
						value={description}
						onChange={(e) => setDescription(e.target.value)}
						required
						rows={3}
						className="text-black mt-1 w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring focus:border-blue-300"
					></textarea>
				</div>

				{error && <p className="text-red-500">{(error as Error).message}</p>}

				<div className="flex justify-start">
					<Button title="Create Project" />
				</div>
			</form>
		</Modal>
	);
};

export default CreateProject;
