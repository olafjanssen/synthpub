import Link from "next/link";
//import CreateProjectModal from "@/features/create-projects";
import EmptyCard from "@/components/cards/EmptyCard";
import ProjectCard from "@/components/cards/ProjectCard";
import { useFetchProjects } from "./hooks";
import CreateProject from "@/features/create-projects";

export interface Project {
	title: string;
	description: string;
	// eslint-disable-next-line @typescript-eslint/no-explicit-any
	topic_ids: any;
	id: string;
	created_at: Date;
	updated_at: Date | null;
}
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
					<ProjectCard project={project} count={index} />
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
