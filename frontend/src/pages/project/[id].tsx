import type { NextPage, GetServerSideProps } from "next";
import Navbar from "@/features/nav-bar";
import { useFetchProjectDetails } from "../../features/projects/hooks";
import { useState } from "react";

import dynamic from "next/dynamic";

const Projects = dynamic(
	() => import("@/features/projects").then((mod) => mod.default),
	{
		loading: () => <p>Loading articles...</p>,
		ssr: true,
	}
);

interface ProjectPageProps {
	projectId: string;
}

const Project: NextPage<ProjectPageProps> = ({ projectId }) => {
	const { data: project } = useFetchProjectDetails(projectId ?? "");
	const [isModalOpen, setIsModalOpen] = useState(false);

	return (
		<>
			<Navbar
				title={project?.title}
				projectId={projectId}
				setIsModalOpen={setIsModalOpen}
			/>
			<Projects
				project={project}
				isModalOpen={isModalOpen}
				setIsModalOpen={setIsModalOpen}
			/>
		</>
	);
};

export const getServerSideProps: GetServerSideProps = async (context) => {
	const { id } = context.params || {};
	const projectId = Array.isArray(id) ? id[0] : id || "";

	return {
		props: {
			projectId,
		},
	};
};

export default Project;
