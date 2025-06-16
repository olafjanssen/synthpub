// features/topics/CreateTopics.tsx

import { useState } from "react";
import Modal from "@/components/modal";
import Button from "@/components/button";
import { useCreateTopic, CreateTopicPayload } from "./hooks";

interface CreateTopicModalProps {
	isOpen: boolean;
	onClose: () => void;
	projectId?: string;
}

const CreateTopics: React.FC<CreateTopicModalProps> = ({
	isOpen,
	onClose,
	projectId,
}) => {
	//TODO: WIll make it as a single object instead of separate state values
	const [name, setName] = useState("");
	const [description, setDescription] = useState("");
	const [feedUrls, setFeedUrls] = useState("");
	const [publishUrls, setPublishUrls] = useState("");
	const [thumbnailUrl, setThumbnailUrl] = useState("");

	const { mutate, error } = useCreateTopic(projectId ?? "");

	const handleSubmit = () => {
		const newTopic: CreateTopicPayload = {
			name,
			description,
			feed_urls: feedUrls
				.split(",")
				.map((url) => url.trim())
				.filter(Boolean),
			publish_urls: publishUrls
				.split(",")
				.map((url) => url.trim())
				.filter(Boolean),
			thumbnail_url: thumbnailUrl,
		};

		mutate(newTopic, {
			onSuccess: () => {
				setName("");
				setDescription("");
				setFeedUrls("");
				setPublishUrls("");
				setThumbnailUrl("");
				onClose();
			},
		});
	};

	if (!isOpen) return null;

	return (
		<Modal onClose={onClose} title="Create Topic">
			<form onSubmit={handleSubmit} className="p-4">
				<div className="mb-4">
					<label className="block text-white">Name</label>
					<input
						type="text"
						value={name}
						onChange={(e) => setName(e.target.value)}
						required
						className="mt-1 w-full text-black border border-gray-300 rounded px-3 py-2"
					/>
				</div>

				<div className="mb-4">
					<label className="block text-white">Description</label>
					<textarea
						value={description}
						onChange={(e) => setDescription(e.target.value)}
						required
						rows={3}
						className="mt-1 w-full text-black border border-gray-300 rounded px-3 py-2"
					/>
				</div>

				<div className="mb-4">
					<label className="block text-white">
						Feed URLs (comma separated)
					</label>
					<input
						type="text"
						value={feedUrls}
						onChange={(e) => setFeedUrls(e.target.value)}
						required
						className="mt-1 w-full text-black border border-gray-300 rounded px-3 py-2"
					/>
				</div>

				<div className="mb-4">
					<label className="block text-white">
						Publish URLs (comma separated)
					</label>
					<input
						type="text"
						value={publishUrls}
						onChange={(e) => setPublishUrls(e.target.value)}
						className="mt-1 w-full text-black border border-gray-300 rounded px-3 py-2"
					/>
				</div>

				<div className="mb-4">
					<label className="block text-white">Thumbnail URL</label>
					<input
						type="text"
						value={thumbnailUrl}
						onChange={(e) => setThumbnailUrl(e.target.value)}
						className="mt-1 w-full text-black border border-gray-300 rounded px-3 py-2"
					/>
				</div>

				{error && <p className="text-red-500">{(error as Error).message}</p>}

				<div className="flex justify-start">
					<Button title="Create Topic" onClick={handleSubmit} />
				</div>
			</form>
		</Modal>
	);
};

export default CreateTopics;
