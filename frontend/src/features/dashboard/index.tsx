import Link from "next/link";
import EmptyCard from "@/components/cards/empty-card";
//import ProjectCard from "@/components/cards/ProjectCard";
import { useFetchProjects } from "./hooks";
import CreateProject from "@/features/create-projects";
import ContentCard from "@/components/cards/content-card";

interface Props {
	isModalOpen: boolean;
	setIsModalOpen: (ele: boolean) => void;
}

const Dashboard: React.FC<Props> = ({ isModalOpen, setIsModalOpen }) => {
	const { isLoading, isError, data: projects, error } = useFetchProjects();

	if (isLoading) return <p>Loading projects...</p>;
	if (isError) return <p>Error: {error?.message}</p>;

	return (
		<div className="flex flex-wrap gap-1 gap-y-4" id="projects-list">
			{projects?.map((project, index) => (
				<Link key={project.id} href={`/project/${project.id}`}>
					<ContentCard
						data={project}
						count={index}
						borderColor="#93b39c38"
						hoverColor="grayscale"
					/>
				</Link>
			))}
			<EmptyCard />
			<CreateProject
				isOpen={isModalOpen}
				onClose={() => setIsModalOpen(false)}
			/>
		</div>
	);
};

export default Dashboard;
