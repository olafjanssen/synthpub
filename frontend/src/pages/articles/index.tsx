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

const Articles: NextPage = () => {
	return (
		<>
			<Navbar />
			<Article />
		</>
	);
};

export const getServerSideProps: GetServerSideProps = async () => {
	// You can fetch data here if needed
	return {
		props: {}, // Will be passed to the page component as props
	};
};

export default Articles;
