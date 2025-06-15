import type { NextPage, GetServerSideProps } from "next";
import Navbar from "@/features/nav-bar/Navbar";
import dynamic from "next/dynamic";

const Article = dynamic(
	() => import("@/features/articles").then((mod) => mod.default),
	{
		loading: () => <div>Loading...</div>,
		ssr: false,
	}
);

interface ArticlePageProps {
	articleId: string;
	pid: string;
	title: string;
}

const Articles: NextPage<ArticlePageProps> = ({ articleId, pid, title }) => {
	if (articleId === "no-article") {
		return (
			<>
				<Navbar projectId={pid} title={title} />
				<Article articleId={articleId} />
				{/* <div>No article available.</div> */}
			</>
		);
	}

	return (
		<>
			<Navbar projectId={pid} title={title} />
			<Article articleId={articleId} />
		</>
	);
};

export const getServerSideProps: GetServerSideProps = async (context) => {
	const { pid, title } = context.query;
	const articleId = context.params?.id || "";

	return {
		props: {
			articleId,
			pid,
			title,
		},
	};
};

export default Articles;
