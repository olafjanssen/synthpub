import Link from "next/link";
import EmptyCard from "@/components/cards/EmptyCard";
import { Project } from "@/utils/types";
import ContentCard from "@/components/cards/ContentCard";
import CreateTopics from "../create-topics";
import { useFetchTopics } from "./hooks";

interface Props {
	project: Project | undefined;
	isModalOpen: boolean;
	setIsModalOpen: (ele: boolean) => void;
}

const Projects: React.FC<Props> = ({
	project,
	isModalOpen,
	setIsModalOpen,
}) => {
	//TODO: fetch by project id

	const { data: topics } = useFetchTopics();

	return (
		<div className="flex flex-wrap gap-1 gap-y-4" id="projects-list">
			{topics?.map((topic, index) => (
				//TODO: will update the url
				<Link
					key={topic.id}
					href={`/articles/${
						topic?.article === null ? "no-article" : topic.article
					}?pid=${project?.id}&&title=${project?.title}`}
				>
					<ContentCard
						data={{ title: topic.name, description: topic.description }}
						count={index}
						borderColor="#f06e6c"
						hoverColor="bg-topCardBgSecond"
					/>
				</Link>
			))}
			<EmptyCard />
			<CreateTopics
				isOpen={isModalOpen}
				onClose={() => setIsModalOpen(false)}
				projectId={project?.id}
			/>
		</div>
	);
};

export default Projects;
